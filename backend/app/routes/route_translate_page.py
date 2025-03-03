from flask import request
from flask_restful import Resource
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
        Initializes TranslatePage with ConfigManager, CacheManager, MongoDBManager, and Crypto_Manager.

        Args:
            config_manager (ConfigManager): Provides configuration details.
            cache_manager (CacheManager): Manages caching of translations.
            mongo_manager (MongoDBManager): The MongoDB manager instance.
            crypto_manager (Crypto_Manager): Manages encryption/decryption for text.
        """
        self.translation_service = TranslationService(config_manager, cache_manager)
        self.config_manager = config_manager
        self.mongo_manager = mongo_manager
        self.crypto_manager = crypto_manager
        Logger.info("TranslatePage instance initialized.")

    def post(self):
        Logger.info("POST request received for TranslatePage.")
        json_data = request.get_json()
        if not json_data or 'data' not in json_data:
            Logger.warning("Missing 'data' object in request.")
            return {"error": "Missing data object"}, 400

        data = json_data['data']
        model = data.get('model')
        page = data.get('page')
        title = data.get('title')
        user = data.get('user')

        # Language-Detection
        try:
            language = model.rsplit('-', 1)[-1]
        except Exception:
            Logger.error("Failed to extract language from model.")
            return {"error": "Invalid model format"}, 400

        # Validate required parameters
        if not model:
            Logger.warning("Missing required parameter: model.")
            return {"error": "Missing required parameters"}, 400
        if page is None:
            Logger.warning("Missing required parameter: page.")
            return {"error": "Missing required parameter: page"}, 400

        try:
            Logger.info(f"Starting page translation with model={model}, page={page}, title={title}, user={user}.")

            # 1) Check if there's already a translation for this language
            user_files_collection = self.config_manager.get_mongo_config().get("user_files_collection", "user_files")
            existing_translation = self.mongo_manager.retrieve_and_decrypt_translation(
                user=user,
                page=page,
                title=title,
                language=language,
                user_files_collection=user_files_collection,
                crypto_manager=self.crypto_manager
            )
            if existing_translation:
                # if already there, directly return
                Logger.info(f"Translation for language '{language}' already exists. Returning existing translation.")
                return {"translation": existing_translation}, 200

            # 2) If no existing translation, decrypt the source text
            doc, source_text = self.mongo_manager.retrieve_and_decrypt_page(
                user=user,
                page=page,
                title=title,
                user_files_collection=user_files_collection,
                crypto_manager=self.crypto_manager
            )

            # 3) Translate
            translated_text = self.translation_service.translate_and_chunk_text(model, source_text)
            Logger.info("Page translation completed successfully.")

            # 4) Encrypt result & update DB
            encrypted_result = self.crypto_manager.encrypt_string(user, translated_text)
            collection_name = self.config_manager.get_mongo_config().get("user_files_collection")
            if not collection_name:
                Logger.error("User files collection name is not defined in the configuration.")
                return {"error": "Configuration error: Missing collection name"}, 500

            query = {"title": title, "page": page, "user": user}
            update_op = {"$set": {f"translations.{language}": encrypted_result}}
            update_result = self.mongo_manager.update_document(collection_name, query, update_op, upsert=True)

            if update_result.matched_count == 0:
                Logger.warning(f"No matching document found for query: {query}.")
                return {"error": "No matching document found to update"}, 404

            response = {"translation": translated_text}
            Logger.info("Text translation updated successfully.")
            return response, 200

        except ValueError as ve:
            Logger.error(f"Invalid input: {str(ve)}")
            return {"error": f"Invalid input: {str(ve)}"}, 422
        except Exception as e:
            Logger.error(f"Internal Server Error during page translation: {str(e)}")
            return {"error": f"Internal Server Error: {str(e)}"}, 500

