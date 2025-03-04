import json
from flask import request
from flask_restful import Resource
from backend.app.services import TranslationService
from backend.app.utils.util_logger import Logger


class TranslatePage(Resource):
    """
    Handles translation requests by extracting the 'text' field from structured OCR data,
    translating it, and updating the translations array while keeping metadata unchanged.
    """

    def __init__(self, config_manager, cache_manager, mongo_manager, crypto_manager):
        """
        Initializes `TranslatePage` with:
        - `config_manager`: Configuration for MongoDB
        - `cache_manager`: Caching for translation models
        - `mongo_manager`: Handles MongoDB CRUD operations
        - `crypto_manager`: Encrypts and decrypts text data
        """
        self.translation_service = TranslationService(config_manager, cache_manager)
        self.config_manager = config_manager
        self.mongo_manager = mongo_manager
        self.crypto_manager = crypto_manager
        Logger.info("TranslatePage instance initialized.")

    def post(self):
        """
        Processes a translation request:
        1. Checks if translation already exists.
        2. Retrieves and decrypts the `source` text.
        3. Extracts structured text fields for translation.
        4. Translates only the `text` fields.
        5. Stores the translated text in `translations[language]` in MongoDB.
        """
        Logger.info("Received POST request for TranslatePage.")

        json_data = request.get_json()
        if not json_data or "data" not in json_data:
            Logger.warning("Missing 'data' object in request.")
            return {"error": "Missing data object"}, 400

        data = json_data["data"]
        model, page, title, user = data.get("model"), data.get("page"), data.get("title"), data.get("user")

        # Extract language suffix (e.g., 'en' from "opus-mt-en-de")
        language = self._extract_language_from_model(model)
        if not language:
            return {"error": "Invalid model format"}, 400

        if not model or page is None or not title or not user:
            Logger.warning("Missing required parameters: model, page, title, or user.")
            return {"error": "Missing required parameters"}, 400

        try:
            Logger.info(f"Processing translation: user={user}, page={page}, title={title}, model={model}")

            # Check if translation already exists
            user_files_collection = self.config_manager.get_mongo_config().get("user_files_collection", "user_files")
            existing_translation = self.mongo_manager.retrieve_and_decrypt_translation(
                user=user, page=page, title=title, language=language,
                user_files_collection=user_files_collection, crypto_manager=self.crypto_manager
            )

            if existing_translation:
                Logger.info(f"Translation for language={language} already exists. Returning existing translation.")
                return {"translation": existing_translation}, 200

            # Retrieve and decrypt the source text
            source_data = self.mongo_manager.retrieve_and_decrypt_page(
                user=user, page=page, title=title, user_files_collection=user_files_collection,
                crypto_manager=self.crypto_manager
            )

            if not source_data:
                Logger.warning("No source text found for translation.")
                return {"error": "No source text found"}, 404

            if not isinstance(source_data, (list, dict)):
                Logger.error(f"Invalid source text format: Expected list or dict, but got {type(source_data)}")
                return {"error": f"Invalid source text format: Expected list or dict, but got {type(source_data)}"}, 500

            # Extract and translate text
            translated_text_data = self._extract_and_translate_text_blocks(source_data, model)
            if not translated_text_data:
                Logger.warning("No valid text blocks extracted for translation.")
                return {"error": "No valid text blocks found"}, 400

            Logger.info("Translation completed successfully.")

            # Encrypt translated text
            encrypted_translation = self.crypto_manager.encrypt_string(user, translated_text_data)

            # Update MongoDB document with the translation
            self._update_translation_in_mongo(user_files_collection, title, page, user, language, encrypted_translation)

            Logger.info("Translated text successfully saved in MongoDB.")
            return {"translation": translated_text_data}, 200

        except ValueError as ve:
            Logger.error(f"Invalid input: {str(ve)}")
            return {"error": f"Invalid input: {str(ve)}"}, 422
        except Exception as e:
            Logger.error(f"Internal Server Error during translation: {str(e)}")
            return {"error": f"Internal Server Error: {str(e)}"}, 500

    def _extract_language_from_model(self, model):
        """
        Extracts the language suffix from the model name.

        Args:
            model (str): Translation model name (e.g., 'opus-mt-en-de').

        Returns:
            str or None: Extracted language or None if invalid.
        """
        try:
            return model.rsplit("-", 1)[-1]
        except Exception:
            Logger.error("Failed to extract language from model.")
            return None

    def _extract_and_translate_text_blocks(self, text_data, model):
        """
        Extracts `text` fields from structured OCR data, translates them, and
        replaces the original words while keeping metadata unchanged.

        Args:
            text_data (list): OCR data containing text blocks.
            model (str): Translation model to use.

        Returns:
            list: Updated text data with translations.
        """
        if not isinstance(text_data, list):
            Logger.warning(f"Expected a list of blocks, got {type(text_data)}")
            return text_data

        for block_dict in text_data:
            if not isinstance(block_dict, dict):
                Logger.warning("Skipping item because it's not a dictionary.")
                continue

            block_content = block_dict.get("Block")
            if not isinstance(block_content, dict):
                Logger.warning("Skipping item because 'Block' is missing or not a dictionary.")
                continue

            data_list = block_content.get("Data")
            if not isinstance(data_list, list):
                Logger.warning("Skipping item because 'Data' is missing or not a list.")
                continue

            for item in data_list:
                if not isinstance(item, dict):
                    continue

                text_field = item.get("text")
                if not isinstance(text_field, list):
                    continue  # Skip if 'text' field is missing or not a list

                original_text = " ".join(text_field).strip()
                if not original_text:
                    Logger.debug("Skipping empty text block.")
                    continue

                Logger.debug(f"Original text to translate: '{original_text}'")
                translated_result = self.translation_service.translate_text(model, original_text)

                if isinstance(translated_result, list):
                    joined_text = " ".join(translated_result)
                else:
                    joined_text = str(translated_result)

                joined_text = joined_text.strip()
                Logger.debug(f"Translated text: '{joined_text}'")

                item["text"] = joined_text.split(" ")

        Logger.info("Successfully processed and translated all text blocks.")
        return text_data

    def _update_translation_in_mongo(self, collection, title, page, user, language, encrypted_translation):
        """
        Updates the MongoDB document with the translated text.

        Args:
            collection (str): MongoDB collection name.
            title (str): Document title.
            page (int): Page number.
            user (str): User identifier.
            language (str): Target translation language.
            encrypted_translation (dict): Encrypted translation data.
        """
        update_query = {"title": title, "page": page, "user": user}
        update_op = {"$set": {f"translations.{language}": encrypted_translation}}

        update_result = self.mongo_manager.update_document(collection, update_query, update_op, upsert=True)
        if update_result.matched_count == 0:
            Logger.warning(f"No matching document found for query: {update_query}.")
            raise ValueError("No matching document found to update")
