import base64
import hashlib

import torch

from backend.app.translators import OpusMTTranslator, LibreTranslateTranslator
from backend.app.utils import TranslationModel, PDFProcessor, preprocess_text, split_text_into_chunks, \
    join_and_split_translations


class TranslationService:
    """
    Provides translation functionality for both PDF files and plain text.

    This service handles translation requests by utilizing the OpusMT or LibreTranslate models,
    supports caching to avoid redundant translations, and processes PDF files page by page.
    """
    _instance = None  # Singleton instance
    def __init__(self, config_manager, cache_manager):
        """
        Initializes TranslationService with instances of ConfigManager and CacheManager.

        Args:
            config_manager (ConfigManager): Manages application configurations and device settings.
            cache_manager (CacheManager): Handles caching of translations to optimize performance.
        """
        self.config_manager = config_manager
        self.cache_manager = cache_manager

    def translate_file(self, file, model, sourcelanguage, targetlanguage):
        """
        Translates a base64-encoded PDF file page by page.

        The method checks if the entire file has been cached previously. If not,
        the PDF is decoded, its text is extracted, and each page is translated individually.

        Args:
            file (str): Base64-encoded PDF file.
            model (str): Translation model (OpusMT or LibreTranslate).
            sourcelanguage (str): Source language code.
            targetlanguage (str): Target language code.

        Returns:
            list or dict: List of translated pages, or error message if extraction fails.
        """
        try:
            model_enum = TranslationModel(model)
        except ValueError:
            raise ValueError(f"Unsupported translation model: {model}")

        # Generate cache key based on file hash and translation parameters
        file_hash = hashlib.md5(file.encode()).hexdigest()
        cache_key = f"{model_enum.value}-{sourcelanguage}-{targetlanguage}-{file_hash}"

        # Check if file translation exists in cache
        cached_translation = self.cache_manager.get(cache_key)
        if cached_translation:
            print(f"[CACHE HIT] Returning cached PDF: {cache_key}")
            return cached_translation
        else:
            print(f"[CACHE MISS] No cache entry for: {cache_key}")

        # Decode PDF and extract text
        file_content = base64.b64decode(file)
        extracted_text = PDFProcessor.extract_text_from_pdf(file_content)

        if not extracted_text:
            return {"error": "Failed to extract text from PDF."}, 400

        translated_pages = []

        # Translate each extracted page
        for i, page in enumerate(extracted_text):
            translated_text = self._translate_text(model, sourcelanguage, targetlanguage, page)
            translated_pages.append(translated_text)

        # Store translated PDF in cache
        self.cache_manager.set(cache_key, translated_pages)
        print(f"[CACHE SET] Storing PDF in cache: {cache_key}")

        return translated_pages

    def translate_text(self, model, sourcelanguage, targetlanguage, text):
        """
        Translates plain text using the specified translation model.

        Text is tokenized and processed in chunks if necessary to fit within model constraints.
        Caching is used to optimize performance by storing previous translations.

        Args:
            model (str): Translation model (OpusMT or LibreTranslate).
            sourcelanguage (str): Source language code.
            targetlanguage (str): Target language code.
            text (str): Text to be translated.

        Returns:
            list or str: Translated text or error message if translation fails.
        """
        try:
            model_enum = TranslationModel(model)
        except ValueError:
            raise ValueError(f"Unsupported translation model: {model}")

        text = preprocess_text(text)

        # Generate cache key for text translation
        text_hash = hashlib.md5(text.encode()).hexdigest()
        cache_key = f"{model_enum.value}-{sourcelanguage}-{targetlanguage}-{text_hash}"

        # Check if text translation exists in cache
        cached_translation = self.cache_manager.get(cache_key)
        if cached_translation:
            print(f"[CACHE HIT] Returning cached text: {cache_key}")
            return cached_translation
        else:
            print(f"[CACHE MISS] No cache entry for: {cache_key}")

        # Load tokenizer and split text into chunks for translation
        tokenizer = OpusMTTranslator.load_tokenizer(sourcelanguage, targetlanguage)
        chunks = split_text_into_chunks(tokenizer, text, max_tokens=150)

        translated_chunks = []
        for chunk in chunks:
            print(chunk)
            translated_chunk = self._translate_text(model_enum, sourcelanguage, targetlanguage, chunk)
            translated_chunks.append(translated_chunk)

        # Combine translated chunks into final result
        translated_text = join_and_split_translations(translated_chunks)

        # Store translated text in cache
        self.cache_manager.set(cache_key, translated_text)
        print(f"[CACHE SET] Storing text translation in cache: {cache_key}")

        return translated_text

    def _translate_text(self, model_enum, sourcelanguage, targetlanguage, text):
        """
        Helper method to perform actual text translation using the specified model.

        Args:
            model_enum (TranslationModel): Enum representing the selected translation model.
            sourcelanguage (str): Source language code.
            targetlanguage (str): Target language code.
            text (str): Text to translate.

        Returns:
            list or str: Translated text.
        """
        if isinstance(model_enum, str):
            model_enum = TranslationModel(model_enum)

        if model_enum == TranslationModel.OPUS_MT:
            translator = OpusMTTranslator(
                sourcelanguage,
                targetlanguage,
                self.cache_manager,
                self.config_manager.get_torch_device()
            )
        elif model_enum == TranslationModel.LIBRE:
            translator = LibreTranslateTranslator(
                sourcelanguage,
                targetlanguage,
                self.cache_manager,
                self.config_manager.get_config_value('TRANSLATE', 'URL_LIBRE_TRANSLATE', str, default='http://localhost:55000/translate'),
                self.config_manager.get_config_value('TRANSLATE', 'HEADER_LIBRE_TRANSLATE', dict, default='{"Content-Type": "application/json"}')
            )
        else:
            raise ValueError(f"Unsupported translation model: {model_enum.value}")

        return translator.translate(text)
