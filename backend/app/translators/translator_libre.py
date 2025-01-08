import requests

class LibreTranslateTranslator:
    """
    LibreTranslateTranslator uses the LibreTranslate API to translate text
    between specified languages.

    This class handles the interaction with the LibreTranslate API, performing text translations
    and leveraging a cache to minimize redundant API calls.

    Args:
        source_lang (str): Source language code (e.g., 'en').
        target_lang (str): Target language code (e.g., 'de').
        cache_manager (CacheManager): Cache to store and reuse translations.
        url (str): The URL of the LibreTranslate API endpoint.
        headers (dict): HTTP headers to include with API requests.
    """

    def __init__(self, source_lang, target_lang, cache_manager, url, headers):
        """
        Initializes LibreTranslateTranslator with the necessary translation parameters and configurations.

        Args:
            source_lang (str): The source language for the translation.
            target_lang (str): The target language for the translation.
            cache_manager (CacheManager): Instance to manage caching of translations.
            url (str): LibreTranslate API endpoint URL.
            headers (dict): Request headers for API calls.
        """
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.cache_manager = cache_manager
        self.url = url
        self.headers = headers

    def translate(self, text):
        """
        Translates the input text using the LibreTranslate API.

        This method first checks if the translation already exists in the cache.
        If not, it makes an API request to perform the translation and caches the result.

        Args:
            text (str or list): Text to be translated. Lists are joined into a single string.

        Returns:
            list: Translated text in the target language.
        """
        if isinstance(text, list):
            text = " ".join(text)  # Join list of text into a single string if necessary

        # Generate cache key based on text
        cache_key = f"Libre-{text}"
        if self.cache_manager.get(cache_key):
            return self.cache_manager.get(cache_key)

        payload = {
            "q": text,
            "source": self.source_lang,
            "target": self.target_lang,
            "format": "text"
        }

        # Make a POST request to LibreTranslate
        response = requests.post(self.url, headers=self.headers, json=payload)

        if response.status_code == 200:
            result = response.json().get("translatedText", text)
            self.cache_manager.set(cache_key, result)  # Cache the translation
            return [result]

        # Return original text if translation fails
        return [text]
