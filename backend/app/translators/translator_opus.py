from transformers import MarianMTModel, MarianTokenizer
import torch


class OpusMTTranslator:
    """
    OpusMTTranslator uses Helsinki-NLP's MarianMT models to translate text
    between specified languages.

    This class handles text translation by loading the appropriate MarianMT model
    for the specified source and target languages. It utilizes caching to optimize
    performance and avoid redundant translations.

    Args:
        source_lang (str): Source language code (e.g., 'en').
        target_lang (str): Target language code (e.g., 'de').
        cache_manager (CacheManager): Cache to store and reuse translations, models, and tokenizers.
        device (str): Device to load the model ('cpu' or 'cuda').
    """

    def __init__(self, source_lang, target_lang, cache_manager, device):
        model_key = f"model-{source_lang}-{target_lang}"
        tokenizer_key = f"tokenizer-{source_lang}-{target_lang}"

        if cache_manager.get(model_key) and cache_manager.get(tokenizer_key):
            print(f"✅ Model and tokenizer for '{source_lang}-{target_lang}' loaded from cache.")
            self.model = cache_manager.get(model_key)
            self.tokenizer = cache_manager.get(tokenizer_key)
        else:
            model_name = f"Helsinki-NLP/opus-mt-{source_lang}-{target_lang}"
            print(f"🔄 Loading model and tokenizer for '{source_lang}-{target_lang}'...")
            self.tokenizer = MarianTokenizer.from_pretrained(model_name)
            self.model = MarianMTModel.from_pretrained(model_name)
            cache_manager.set(model_key, self.model)
            cache_manager.set(tokenizer_key, self.tokenizer)

        self.device = torch.device(device)
        self.model.to(self.device)


    @staticmethod
    def load_tokenizer(sourcelanguage: str, targetlanguage: str):
        """
        Loads and returns the MarianTokenizer for the specified language pair.

        Args:
            sourcelanguage (str): Source language code.
            targetlanguage (str): Target language code.

        Returns:
            MarianTokenizer: Tokenizer for the specified language pair.
        """
        model_name = f"Helsinki-NLP/opus-mt-{sourcelanguage}-{targetlanguage}"
        return MarianTokenizer.from_pretrained(model_name)

    def translate(self, text):
        inputs = self.tokenizer(text, return_tensors="pt", padding=True)
        inputs = {key: value.to(self.device) for key, value in inputs.items()}
        with torch.no_grad():
            translated = self.model.generate(**inputs)
        return self.tokenizer.batch_decode(translated, skip_special_tokens=True)

