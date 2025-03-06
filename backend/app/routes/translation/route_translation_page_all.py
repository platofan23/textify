import json
from flask import request
from flask_restful import Resource
from backend.app.services.translation import TranslationService
from backend.app.utils.util_logger import Logger

class TranslateAllPages(Resource):
    """
    Handles bulk translation requests for all pages of a given title.
    For each page, if a translation for the target language exists, it is left unchanged.
    Otherwise, the source text is retrieved, translated, and the encrypted translation is stored in MongoDB.
    If no errors occur, a success message is returned.
    """

    def __init__(self, config_manager, cache_manager, mongo_manager, crypto_manager):
        self.translation_service = TranslationService(config_manager, cache_manager)
        self.config_manager = config_manager
        self.mongo_manager = mongo_manager
        self.crypto_manager = crypto_manager
        Logger.info("TranslateAllPages instance initialized.")

    def post(self):
        Logger.info("POST request received for TranslateAllPages.")
        json_data = request.get_json()
        if not json_data or "data" not in json_data:
            Logger.warning("Missing 'data' object in request.")
            return {"error": "Missing data object"}, 400

        data = json_data["data"]
        model = data.get("model")
        title = data.get("title")
        user = data.get("user")

        # Extract target language (e.g., 'de' from "opus-mt-en-de")
        try:
            language = model.rsplit("-", 1)[-1]
        except Exception:
            Logger.error("Failed to extract language from model.")
            return {"error": "Invalid model format"}, 400

        if not model or not title or not user:
            Logger.warning("Missing required parameters: model, title, or user.")
            return {"error": "Missing required parameters"}, 400

        try:
            Logger.info(f"Retrieving all pages for user={user}, title='{title}'.")
            user_files_collection = self.config_manager.get_mongo_config().get("user_text_collection")
            query = {"user": user, "title": title}
            pages = self.mongo_manager.find_documents(user_files_collection, query)

            if not pages:
                Logger.warning(f"No pages found for title='{title}'.")
                return {"error": "No pages found"}, 404

            for doc in pages:
                Logger.debug(f"Processing document: {doc}")
                page_number = doc.get("page")
                Logger.info(f"Processing page {page_number} of title '{title}'.")

                # Ensure the document has a 'translations' field
                if "translations" not in doc or not isinstance(doc["translations"], dict):
                    doc["translations"] = {}

                # If translation already exists, skip processing this page
                if language in doc["translations"] and doc["translations"][language]:
                    Logger.info(f"Translation for page {page_number} already exists. Skipping translation.")
                    continue

                # Retrieve and decrypt source text for the page
                Logger.info(f"Retrieving and decrypting source text for page {page_number}.")
                source_data = self.mongo_manager.retrieve_and_decrypt_page(
                    user=user,
                    page=page_number,
                    title=title,
                    user_files_collection=user_files_collection,

                )
                if not source_data:
                    Logger.warning(f"No source text found for page {page_number}. Skipping translation.")
                    continue

                if not isinstance(source_data, (list, dict)):
                    Logger.error(f"Invalid source text format for page {page_number}. Expected list or dict.")
                    continue

                # Extract and translate text blocks from the source data
                translated_text_data = self._extract_and_translate_text_blocks(source_data, model)
                if not translated_text_data:
                    Logger.warning(f"No valid text blocks extracted for page {page_number}. Skipping translation.")
                    continue

                Logger.info(f"Translation completed successfully for page {page_number}.")

                # Convert the translated text data to a JSON string and encrypt it
                try:
                    json_translated_text = json.dumps(translated_text_data, ensure_ascii=False)
                    encrypted_translation = self.crypto_manager.encrypt_string(user, json_translated_text)
                except Exception as e:
                    Logger.error(f"Error encrypting translation for page {page_number}: {e}")
                    continue

                # Update the MongoDB document with the encrypted translation
                update_query = {"title": title, "page": page_number, "user": user}
                update_op = {"$set": {f"translations.{language}": encrypted_translation}}
                update_result = self.mongo_manager.update_document(user_files_collection, update_query, update_op, upsert=True)
                if update_result.matched_count == 0:
                    Logger.warning(f"No matching document found for page {page_number}. Skipping update.")
                    continue

                Logger.info(f"Translated text successfully saved in MongoDB for page {page_number}.")

            Logger.info("All pages processed successfully. No errors encountered.")
            return {"message": "All pages translated successfully."}, 200

        except Exception as e:
            Logger.error(f"Internal Server Error during translation: {str(e)}")
            return {"error": f"Internal Server Error: {str(e)}"}, 500

    def _extract_and_translate_text_blocks(self, text_data: list, model: str) -> list:
        """
        Processes OCR-like structured blocks to extract and translate 'text' fields.
        Replaces the original 'text' field with the translated words while preserving other metadata.

        Args:
            text_data (list): OCR data containing text blocks.
            model (str): Translation model identifier.

        Returns:
            list: Updated OCR data with translated text.
        """
        if not isinstance(text_data, list):
            Logger.warning(f"Expected a list of blocks, got {type(text_data)}")
            return text_data

        for block_dict in text_data:
            if not isinstance(block_dict, dict):
                Logger.warning("Skipping non-dict block item.")
                continue

            block_content = block_dict.get("Block")
            if not isinstance(block_content, dict):
                Logger.warning("Skipping block due to missing or invalid 'Block' field.")
                continue

            data_list = block_content.get("Data")
            if not isinstance(data_list, list):
                Logger.warning("Skipping block due to missing or invalid 'Data' field.")
                continue

            for item in data_list:
                if not isinstance(item, dict):
                    continue

                text_field = item.get("text")
                if not isinstance(text_field, list):
                    continue

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
                # Replace the 'text' field with the translated words (as a list)
                item["text"] = joined_text.split(" ")

        Logger.info("Processed and translated all text blocks successfully.")
        return text_data
