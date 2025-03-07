from flask import request
from flask_restful import Resource
from backend.app.services.translation import TranslationService
from backend.app.utils.util_logger import Logger

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
        Logger.info("TranslateFile instance initialized.")

    def post(self):
        """
        Handles POST requests to translate a PDF file.

        Receives a JSON payload containing the base64-encoded PDF and the model,
        validates the input, and returns the translated content or an error response.

        Returns:
            tuple: JSON response containing the translated text or an error message, along with the HTTP status code.
        """
        Logger.info("POST request received for TranslateFile.")

        json_data = request.get_json()

        # Check if the incoming request contains the expected 'data' object
        if not json_data or 'data' not in json_data:
            Logger.warning("Missing 'data' object in request.")
            return {"error": "Missing data object"}, 400

        # Extract required parameters from the request data
        data = json_data['data']
        model = data.get('model')
        file = data.get('file')

        # Validate required parameters to ensure all necessary data is provided
        if not model or not file:
            Logger.warning("Missing required parameters in the request.")
            return {"error": "Missing required parameters"}, 400

        # Attempt to translate the PDF file and handle potential errors
        try:
            Logger.info(f"Starting translation with model={model}.")
            result = self.translation_service.translate_file(file, model)
            Logger.info("Translation completed successfully.")
            return {"translation": result}, 200
        except ValueError as e:
            # Log the error and return a 422 error if the input parameters are invalid
            Logger.error(f"Invalid input: {str(e)}")
            return {"error": f"Invalid input: {str(e)}"}, 422
        except Exception as e:
            # Log unexpected errors and return a 500 response
            Logger.error(f"Internal Server Error: {str(e)}")
            return {"error": f"Internal Server Error: {str(e)}"}, 500
