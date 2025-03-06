import json
from flask import request
from flask_restful import Resource
from backend.app.services.translation import TranslationService
from backend.app.utils.util_logger import Logger

class TranslatePage(Resource):
    """
    Handles translation requests by extracting the 'text' field from structured OCR data,
    translating it, encrypting the translated text (as a JSON string) and storing it in the
    MongoDB document under the 'translations' field. The decrypted (plain) translated text
    is returned in the response.
    """

    def __init__(self, config_manager, cache_manager, mongo_manager, crypto_manager):
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

        # Extract language suffix (e.g., 'de' from "opus-mt-en-de")
        try:
            language = model.rsplit('-', 1)[-1]
        except Exception:
            Logger.error("Failed to extract language from model.")
            return {"error": "Invalid model format"}, 400

        if not model or page is None or not title or not user:
            Logger.warning("Missing required parameters: model, page, title, or user.")
            return {"error": "Missing required parameters"}, 400

        try:
            Logger.info(f"Processing translation for user={user}, page={page}, title={title}, model={model}.")

            # Check if translation already exists and return decrypted version if so
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
                Logger.info(f"Translation for language={language} already exists. Returning decrypted translation.")
                try:
                    # If the decrypted translation is a JSON string, parse it into a Python object.
                    if isinstance(existing_translation, str):
                        translation_obj = json.loads(existing_translation)
                    else:
                        translation_obj = existing_translation
                    return {"translation": translation_obj}, 200
                except Exception as e:
                    Logger.error(f"Error parsing decrypted translation: {e}")
                    return {"error": "Error parsing decrypted translation"}, 500

            # Retrieve and decrypt the source text
            Logger.info("Retrieving and decrypting source text...")
            source_data = self.mongo_manager.retrieve_and_decrypt_page(
                user=user,
                page=page,
                title=title,
                user_files_collection=user_files_collection,
                crypto_manager=self.crypto_manager
            )

            if not source_data:
                Logger.warning("No source text found for translation.")
                return {"error": "No source text found"}, 404

            if not isinstance(source_data, (list, dict)):
                Logger.error(f"Invalid source text format: Expected list or dict, but got {type(source_data)}")
                return {"error": f"Invalid source text format: Expected list or dict, but got {type(source_data)}"}, 500

            # Extract and translate text blocks from the structured OCR data
            translated_text_data = self._extract_and_translate_text_blocks(source_data, model)
            if not translated_text_data:
                Logger.warning("No valid text blocks extracted for translation.")
                return {"error": "No valid text blocks found"}, 400

            Logger.info("Translation completed successfully.")

            # Convert translated text data to a JSON string to ensure valid formatting
            json_translated_text = json.dumps(translated_text_data, ensure_ascii=False)
            # Encrypt the JSON string
            encrypted_translation = self.crypto_manager.encrypt_string(user, json_translated_text)

            # Update the MongoDB document with the encrypted translation
            update_query = {"title": title, "page": page, "user": user}
            update_op = {"$set": {f"translations.{language}": encrypted_translation}}
            update_result = self.mongo_manager.update_document(user_files_collection, update_query, update_op, upsert=True)

            if update_result.matched_count == 0:
                Logger.warning(f"No matching document found for query: {update_query}.")
                return {"error": "No matching document found to update"}, 404

            Logger.info("Translated text successfully saved in MongoDB.")

            # Return the decrypted translated text (structured as per the original OCR format)
            return {"translation": translated_text_data}, 200

        except ValueError as ve:
            Logger.error(f"Invalid input: {str(ve)}")
            return {"error": f"Invalid input: {str(ve)}"}, 422
        except Exception as e:
            Logger.error(f"Internal Server Error during translation: {str(e)}")
            return {"error": f"Internal Server Error: {str(e)}"}, 500

    def _extract_and_translate_text_blocks(self, text_data: list, model: str) -> list:
        """
        Processes a list of OCR-like blocks (each containing a "Block" with "Data"),
        extracts each "text" list, translates it, and replaces the original words with
        the translated words. Other metadata remains unchanged.

        Example input (text_data):
        [
          {
            "Block": {
              "Data": [
                {"text": ["Voter", "turnout", "was"], "size": 0.14},
                {"text": ["82.5%,", "a", ...], "size": 0.15}
              ],
              "Block_Geometry": ...
            }
          }
        ]

        After translation, the 'text' field is replaced with the translated words.

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
                Logger.warning("Skipping block because 'Block' is missing or not a dict.")
                continue

            data_list = block_content.get("Data")
            if not isinstance(data_list, list):
                Logger.warning("Skipping block because 'Data' is missing or not a list.")
                continue

            for item in data_list:
                if not isinstance(item, dict):
                    continue

                text_field = item.get("text")
                if not isinstance(text_field, list):
                    continue

                # Convert the list of words into a single string
                original_text = " ".join(text_field).strip()
                if not original_text:
                    Logger.debug("Skipping empty text block.")
                    continue

                Logger.debug(f"Original text to translate: '{original_text}'")
                # Call the translation service
                translated_result = self.translation_service.translate_text(model, original_text)
                if isinstance(translated_result, list):
                    joined_text = " ".join(translated_result)
                else:
                    joined_text = str(translated_result)

                joined_text = joined_text.strip()
                Logger.debug(f"Translated text: '{joined_text}'")
                # Replace the text field with the translated words split into a list
                item["text"] = joined_text.split(" ")

        Logger.info("Successfully processed and translated all text blocks.")
        return text_data
