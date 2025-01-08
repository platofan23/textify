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
        cache_manager (CacheManager): Cache to store and reuse translations.
        device (str): Device to load the model ('cpu' or 'cuda').
    """
    def __init__(self, source_lang, target_lang, cache_manager, device):
        """
        Initializes the OpusMTTranslator with the specified source and target languages,
        and loads the corresponding MarianMT model and tokenizer.

        Args:
            source_lang (str): Source language code.
            target_lang (str): Target language code.
            cache_manager (CacheManager): Manages cached translations.
            device (str): Specifies the device to run the model ('cpu' or 'cuda').
        """
        model_name = f"Helsinki-NLP/opus-mt-{source_lang}-{target_lang}"
        self.tokenizer = MarianTokenizer.from_pretrained(model_name)
        self.model = MarianMTModel.from_pretrained(model_name)
        self.model.to(torch.device(device))
        self.cache_manager = cache_manager

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
        """
        Translates the input text using the OpusMT model.

        The method checks if the translation exists in the cache. If not,
        it performs the translation and stores the result in the cache.

        Args:
            text (str or list): Text to be translated. Lists are joined into a single string.

        Returns:
            list: Translated text in the target language.
        """
        if isinstance(text, list):
            text = " ".join(text)

        # Generate cache key based on the input text
        cache_key = f"Opus-{text}"
        if self.cache_manager.get(cache_key):
            return self.cache_manager.get(cache_key)

        # Perform translation
        inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True)
        translated = self.model.generate(**inputs)
        translated_text = self.tokenizer.batch_decode(translated, skip_special_tokens=True)

        # Store the result in cache
        self.cache_manager.set(cache_key, translated_text)
        return translated_text
