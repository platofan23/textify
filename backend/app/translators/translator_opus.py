import torch
from transformers import MarianMTModel, MarianTokenizer
from backend.app.utils.util_logger import Logger  # Import the Logger class

class OpusMTTranslator:
    """
    OpusMTTranslator uses Helsinki-NLP's MarianMT models to translate text.

    This class handles text translation by loading the specified MarianMT model.
    It utilizes caching to optimize performance and avoid redundant model and tokenizer loading.

    Args:
        model_name (str): Full model name (e.g., "Helsinki-NLP/opus-mt-en-de").
        cache_manager (CacheManager): Cache to store and reuse models and tokenizers.
        device (str): Device to load the model ('cpu' or 'cuda').
    """

    def __init__(self, model_name, cache_manager, device):
        model_key = f"model-{model_name}"
        tokenizer_key = f"tokenizer-{model_name}"

        if cache_manager.get(model_key) and cache_manager.get(tokenizer_key):
            Logger.info(f"✅ Model and tokenizer for '{model_name}' loaded from cache.")
            self.model = cache_manager.get(model_key)
            self.tokenizer = cache_manager.get(tokenizer_key)
        else:
            Logger.info(f"🔄 Loading model and tokenizer for '{model_name}'...")
            try:
                self.tokenizer = MarianTokenizer.from_pretrained(model_name)
            except Exception as e:
                Logger.error(f"Error loading tokenizer for model '{model_name}'. Error: {str(e)}")
                raise ValueError(f"Error loading tokenizer for model '{model_name}'")
            self.model = MarianMTModel.from_pretrained(model_name)
            cache_manager.set(model_key, self.model)
            cache_manager.set(tokenizer_key, self.tokenizer)

        self.device = torch.device(device)
        self.model.to(self.device)

    @staticmethod
    def load_tokenizer(model_name: str):
        """
        Loads and returns the MarianTokenizer for the given model name.

        Raises:
            ValueError: If the model cannot be loaded (e.g. due to an invalid model name).
        """
        Logger.debug(f"Loading tokenizer for model: {model_name}")
        try:
            return MarianTokenizer.from_pretrained(model_name)
        except Exception as e:
            Logger.error(f"Failed to load tokenizer for model '{model_name}': {str(e)}")
            raise ValueError("Unsupported translation model") from e

    def translate(self, text):
        Logger.info(f"Translating text: {text[:50]}...")
        inputs = self.tokenizer(text, return_tensors="pt", padding=True)
        inputs = {key: value.to(self.device) for key, value in inputs.items()}
        try:
            with torch.no_grad():
                translated = self.model.generate(**inputs)
            result = self.tokenizer.batch_decode(translated, skip_special_tokens=True)
            Logger.info(f"Translation successful for text: {text[:50]}...")
            return result
        except Exception as e:
            Logger.error(f"Error during translation: {str(e)}")
            return [text]
