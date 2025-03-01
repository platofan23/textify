from flask import request
from flask_restful import Resource

from backend.app.services import TranslationService
from backend.app.utils.util_logger import Logger  # Import the Logger class

class TranslateText(Resource):
    """
    Handles the translation of plain text by receiving the text and model,
    and returning the translated result.

    This class interacts with the TranslationService to process and return translated text.
    """
    _instance = None  # Singleton instance

    def __init__(self, config_manager, cache_manager):
        """
        Initializes TranslateText with instances of ConfigManager and CacheManager.

        Args:
            config_manager (ConfigManager): Provides configuration details for the translation process.
            cache_manager (CacheManager): Manages caching of translated text to prevent redundant translations.
        """
        self.translation_service = TranslationService(config_manager, cache_manager)
        self.config_manager = config_manager
        Logger.info("TranslateText instance initialized.")

    def post(self):
        """
        Handles POST requests to translate plain text.

        Expects a JSON payload containing the text and model.
        The translated result is returned in the response.

        Returns:
            tuple: JSON response with translated text or error message, along with the HTTP status code.
        """
        Logger.info("POST request received for TranslateText.")

        json_data = request.get_json()

        # Validate if the incoming request contains the expected 'data' object.
        if not json_data or 'data' not in json_data:
            Logger.warning("Missing 'data' object in request.")
            return {"error": "Missing data object"}, 400

        # Extract translation parameters from request data.
        data = json_data['data']
        model = data.get('model')
        text = data.get('text')
        upload_id = data.get('upload_id')

        # Validate required parameters.
        if not model or not text:
            Logger.warning("Missing required parameters in the request.")
            return {"error": "Missing required parameters"}, 400

        # Attempt to perform text translation and handle potential errors.
        try:
            Logger.info(f"Starting text translation with model={model}.")
            result = self.translation_service.translate_and_chunk_text(model, text)
            Logger.info("Text translation completed successfully.")
            response = {"translation": result}

            # Include optional upload_id if provided.
            if upload_id:
                response['upload_id'] = upload_id

            return response, 200
        except ValueError as e:
            Logger.error(f"Invalid input: {str(e)}")
            return {"error": f"Invalid input: {str(e)}"}, 422
        except Exception as e:
            Logger.error(f"Internal Server Error: {str(e)}")
            return {"error": f"Internal Server Error: {str(e)}"}, 500
