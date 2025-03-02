from flask import request, make_response
from flask_restful import Resource, reqparse

from backend.app.services import TranslationService
from backend.app.utils.util_logger import Logger

class TranslatePage(Resource):
    """
    Handles the translation of a page by receiving page content, model, page number, title, and user,
    and updating the translated result in the database.
    """
    _instance = None  # Singleton instance

    def __init__(self, config_manager, cache_manager, mongo_manager, crypto_manager):
        """
        Initializes TranslatePage with ConfigManager, CacheManager, and MongoDBManager.

        Args:
            config_manager (ConfigManager): Provides configuration details.
            cache_manager (CacheManager): Manages caching of translations.
            mongo_manager (MongoDBManager): The MongoDB manager instance.
        """
        self.translation_service = TranslationService(config_manager, cache_manager)
        self.config_manager = config_manager
        self.mongo_manager = mongo_manager
        self.crypto_manager = crypto_manager
        Logger.info("TranslatePage instance initialized.")

    def post(self):
        """
        Processes POST requests for page translation.

        Expects a JSON payload with the following data:
            - model: Translation model identifier.
            - page_content: The content of the page to translate.
            - page: The page number.
            - title: The title of the document.
            - user: The user associated with the document.

        Returns:
            A JSON response with the update result or an error message.
        """
        Logger.info("POST request received for TranslatePage.")

        json_data = request.get_json()
        if not json_data or 'data' not in json_data:
            Logger.warning("Missing 'data' object in request.")
            return {"error": "Missing data object"}, 400

        data = json_data['data']
        model = data.get('model')
        text= data.get('text')
        page = data.get('page')
        title = data.get('title')
        user = data.get('user')

        try:
            language = model.rsplit('-', 1)[-1]
        except Exception as e:
            Logger.error("Failed to extract language from model.")
            return {"error": "Invalid model format"}, 400

        # Validate required parameters.
        if not model or not text:
            Logger.warning("Missing required parameters: model or text.")
            return {"error": "Missing required parameters"}, 400

        if page is None:
            Logger.warning("Missing required parameter: page.")
            return {"error": "Missing required parameter: page"}, 400

        try:
            Logger.info(f"Starting page translation with model: {model}.")
            # Perform the translation using the translation service.
            result = self.translation_service.translate_and_chunk_text(model, text)
            Logger.info("Page translation completed successfully.")

            encrypted_result = self.crypto_manager.encrypt_string(user, result)

            # Retrieve the collection name from configuration.
            collection_name = self.config_manager.get_mongo_config().get("user_files_collection")
            if not collection_name:
                Logger.error("User files collection name is not defined in the configuration.")
                return {"error": "Configuration error: Missing collection name"}, 500

            # Build the query to find the document based on title, page, and user.
            query = {"title": title, "page": page, "user": user}
            # Build the update operation to set the new translation in the field for the detected language.
            update_op = {"$set": {"translations." + language: encrypted_result}}

            # Update the document only if it exists.
            update_result = self.mongo_manager.update_document(collection_name, query, update_op, upsert=True)

            if update_result.matched_count == 0:
                Logger.warning(f"No matching document found for query: {query}.")
                return {"error": "No matching document found to update"}, 404

            response = {
                "message": "Page translation updated successfully",
                "matched_count": update_result.matched_count,
                "modified_count": update_result.modified_count
            }
            Logger.info(
                f"Update result: Matched: {update_result.matched_count}, Modified: {update_result.modified_count}.")
            return make_response(response, 200)
        except ValueError as ve:
            Logger.error(f"Invalid input: {str(ve)}")
            return {"error": f"Invalid input: {str(ve)}"}, 422
        except Exception as e:
            Logger.error("Internal Server Error during page translation.")
            return {"error": f"Internal Server Error: {str(e)}"}, 500
