import base64
import hashlib
from backend.app.translators import OpusMTTranslator
from backend.app.utils import preprocess_text, split_text_into_chunks, join_and_split_translations, PDFProcessor
from backend.app.utils.util_logger import Logger  # Import the Logger class

class TranslationService:
    """
    Provides translation functionality for both PDF files and plain text.

    This service handles translation requests by utilizing translation models,
    supports caching to avoid redundant translations, and processes PDF files page by page.
    """
    _instance = None  # Singleton instance

    def __init__(self, config_manager, cache_manager):
        """
        Initializes TranslationService with instances of ConfigManager and CacheManager.

        Args:
            config_manager: Manages application configurations and device settings.
            cache_manager: Handles caching of translations to optimize performance.
        """
        self.config_manager = config_manager
        self.cache_manager = cache_manager
        Logger.info("TranslationService initialized.")

    def translate_file(self, file, model):
        """
        Translates a base64-encoded PDF file page by page.

        The method checks if the entire file has been cached previously. If not,
        the PDF is decoded, its text is extracted, and each page is translated individually.

        Args:
            file (str): Base64-encoded PDF file.
            model (str): Full translation model name (e.g., "Helsinki-NLP/opus-mt-en-de").

        Returns:
            list: List of translated pages if successful.
            dict: Error message and HTTP status code if text extraction fails.
        """
        file_hash = hashlib.md5(file.encode()).hexdigest()
        cache_key = f"{model}-{file_hash}"

        cached_translation = self.cache_manager.get(cache_key)
        if cached_translation:
            Logger.info(f"[CACHE HIT] Returning cached PDF: {cache_key}")
            return cached_translation
        else:
            Logger.info(f"[CACHE MISS] No cache entry for: {cache_key}")

        file_content = base64.b64decode(file)
        extracted_text = PDFProcessor.extract_text_from_pdf(file_content)

        if not extracted_text:
            Logger.warning("Failed to extract text from PDF.")
            return {"error": "Failed to extract text from PDF."}, 400

        translated_pages = []
        for i, page in enumerate(extracted_text):
            Logger.debug(f"Translating page {i + 1}.")
            translated_text = self.translate_and_chunk_text(model, page)
            translated_pages.append(translated_text)

        self.cache_manager.set(cache_key, translated_pages)
        Logger.info(f"[CACHE SET] Storing PDF in cache: {cache_key}")

        return translated_pages

    def translate_and_chunk_text(self, model, text):
        """
        Translates plain text using the specified translation model.

        Text is preprocessed and then split into chunks if necessary to fit within model constraints.
        Caching is used to optimize performance by storing previous translations.

        Args:
            model (str): Full translation model name (e.g., "Helsinki-NLP/opus-mt-en-de").
            text (str): Text to be translated.

        Returns:
            list or str: Translated text if successful; otherwise, an error message.
        """
        text = preprocess_text(text)
        text_hash = hashlib.md5(text.encode()).hexdigest()
        cache_key = f"{model}-{text_hash}"

        cached_translation = self.cache_manager.get(cache_key)
        if cached_translation:
            Logger.info(f"[CACHE HIT] Returning cached text: {cache_key}")
            return cached_translation
        else:
            Logger.info(f"[CACHE MISS] No cache entry for: {cache_key}")

        # Load the tokenizer using the provided model.
        tokenizer = OpusMTTranslator.load_tokenizer(model)
        max_token = self.config_manager.get_config_value('TEXT', 'MAX_TOKEN', int)
        chunks = split_text_into_chunks(tokenizer, text, max_token)

        translated_chunks = []
        for chunk in chunks:
            Logger.debug(f"Translating chunk: {chunk[:50]}...")  # Log first 50 characters of the chunk.
            translated_chunk = self.translate_text(model, chunk)
            translated_chunks.append(translated_chunk)

        translated_text = join_and_split_translations(translated_chunks)
        self.cache_manager.set(cache_key, translated_text)
        Logger.info(f"[CACHE SET] Storing text translation in cache: {cache_key}")

        return translated_text

    def translate_text(self, model, text):
        """
        Helper method to perform the actual text translation using the specified model.

        Args:
            model (str): Full translation model name (e.g., "Helsinki-NLP/opus-mt-en-de").
            text (str): Text to translate.

        Returns:
            list or str: Translated text.
        """
        # Instantiate the translator using the full model name.
        translator = OpusMTTranslator(model, self.cache_manager, self.config_manager.get_torch_device())
        return translator.translate(text)
