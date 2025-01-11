from flask import request
from flask_restful import Resource

from backend.app.services import TranslationService

class TranslateFile(Resource):
    """
    Handles the translation of PDF files by receiving a base64-encoded PDF,
    decoding it, extracting the text page by page, translating it, and returning the translated result.

    This class interfaces with the TranslationService to perform the actual translation.
    """

    _instance = None  # Singleton instance

    def __init__(self, config_manager, cache_manager):
        """
        Initializes TranslateFile with instances of ConfigManager and CacheManager.

        Args:
            config_manager (ConfigManager): Provides configuration details needed for translation services.
            cache_manager (CacheManager): Manages caching of translated files to avoid redundant translations.
        """
        self.translation_service = TranslationService(config_manager, cache_manager)
        self.config_manager = config_manager

    def post(self):
        """
        Handles POST requests to translate a PDF file.

        Receives a JSON payload containing the base64-encoded PDF and translation parameters,
        validates the input, and returns the translated content or an error response.

        Returns:
            tuple: JSON response containing the translated text or an error message, along with the HTTP status code.
        """
        json_data = request.get_json()

        # Check if the incoming request contains the expected 'data' object
        if not json_data or 'data' not in json_data:
            return {"error": "Missing data object"}, 400

        # Extract required parameters from the request data
        data = json_data['data']
        model = data.get('model')
        sourcelanguage = data.get('sourcelanguage')
        targetlanguage = data.get('targetlanguage')
        file = data.get('file')

        # Validate required parameters to ensure all necessary data is provided
        if not model or not sourcelanguage or not targetlanguage or not file:
            return {"error": "Missing required parameters"}, 400

        # Attempt to translate the PDF file and handle potential errors
        try:
            result = self.translation_service.translate_file(file, model, sourcelanguage, targetlanguage)
            return {"translation": result}, 200
        except ValueError as e:
            # Return a 422 error if the input parameters are invalid
            return {"error": f"Invalid input: {str(e)}"}, 422
        except Exception as e:
            # Catch all other unexpected errors and return a 500 response
            return {"error": f"Internal Server Error: {str(e)}"}, 500
