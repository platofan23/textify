import json
from flask import request
from flask_restful import Resource
from backend.app.services import TranslationService
from backend.app.utils.util_logger import Logger


class TranslatePage(Resource):
    """
    Handles translation requests, extracts only the 'text' field from structured OCR data,
    translates it, and updates the translations array while keeping other metadata unchanged.
    """

    def __init__(self, config_manager, cache_manager, mongo_manager, crypto_manager):
        self.translation_service = TranslationService(config_manager, cache_manager)
        self.config_manager = config_manager
        self.mongo_manager = mongo_manager
        self.crypto_manager = crypto_manager
        Logger.info("TranslatePage instance initialized.")

    def post(self):
        """
        Processes a translation request:
        1. Retrieves the encrypted `source` text.
        2. Extracts structured text from `text` fields inside the OCR data.
        3. Translates only the `text` fields.
        4. Stores the translated text in the `translations[language]` array.
        """
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

        # Extract language suffix (e.g., 'en' from "opus-mt-en-de")
        try:
            language = model.rsplit('-', 1)[-1]
        except Exception:
            Logger.error("Failed to extract language from model.")
            return {"error": "Invalid model format"}, 400

        # Validate required parameters
        if not model or page is None or not title or not user:
            Logger.warning("Missing required parameters: model, page, title, or user.")
            return {"error": "Missing required parameters"}, 400

        try:
            Logger.info(f"Processing translation for user={user}, page={page}, title={title}, model={model}.")

            # 1️⃣ **Check if translation already exists**
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
                Logger.info(f"Translation for language={language} already exists. Returning existing translation.")
                return {"translation": existing_translation}, 200

            # 2️⃣ **Retrieve and Decrypt Source Text**
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

            # 3️⃣ **Extract and Translate Text**
            translated_text_data = self._extract_and_translate_text_blocks(source_data, model)

            if not translated_text_data:
                Logger.warning("No valid text blocks extracted for translation.")
                return {"error": "No valid text blocks found"}, 400

            Logger.info("Translation completed successfully.")

            # 4️⃣ **Encrypt Translated Text**
            encrypted_translation = self.crypto_manager.encrypt_string(user, translated_text_data)

            # 5️⃣ **Update MongoDB Document**
            update_query = {"title": title, "page": page, "user": user}
            update_op = {"$set": {f"translations.{language}": encrypted_translation}}

            update_result = self.mongo_manager.update_document(user_files_collection, update_query, update_op,
                                                               upsert=True)

            if update_result.matched_count == 0:
                Logger.warning(f"No matching document found for query: {update_query}.")
                return {"error": "No matching document found to update"}, 404

            Logger.info("Translated text successfully saved in MongoDB.")

            return {"translation": translated_text_data}, 200

        except ValueError as ve:
            Logger.error(f"Invalid input: {str(ve)}")
            return {"error": f"Invalid input: {str(ve)}"}, 422
        except Exception as e:
            Logger.error(f"Internal Server Error during translation: {str(e)}")
            return {"error": f"Internal Server Error: {str(e)}"}, 500

    def _extract_and_translate_text_blocks(self, text_data: list, model: str):
        """
        Processes a list of OCR-like blocks (each containing a "Block" with "Data"),
        finds each "text" list, translates it, and replaces the original words with
        the translated words. All other metadata remains unchanged.

        Example input (text_data):
        [
          {
            "Block": {
              "Data": [
                { "text": ["Voter", "turnout", "was"], "size": 0.14 },
                { "text": ["82.5%,", "a", ...], "size": 0.15 }
              ],
              "Block_Geometry": ...
            }
          }
        ]

        After translation, the 'text' field is replaced with the translated words.
        """

        if not isinstance(text_data, list):
            Logger.warning(f"Expected a list of blocks, got {type(text_data)}")
            return text_data

        for block_dict in text_data:
            # block_dict z. B. { "Block": { "Data": [...] } }
            if not isinstance(block_dict, dict):
                Logger.warning("Skipping item because it's not a dict.")
                continue

            block_content = block_dict.get("Block")
            if not isinstance(block_content, dict):
                Logger.warning("Skipping item because 'Block' is missing or not a dict.")
                continue

            data_list = block_content.get("Data")
            if not isinstance(data_list, list):
                Logger.warning("Skipping because 'Data' is missing or not a list.")
                continue

            # Schleife über jedes Element in data_list
            for item in data_list:
                # item z. B. { "text": ["Voter", "turnout", ...], "size": ... }
                if not isinstance(item, dict):
                    continue

                text_field = item.get("text")
                if not isinstance(text_field, list):
                    # Falls kein 'text'-Feld oder es ist kein list -> skip
                    continue

                # Aus list -> String
                original_text = " ".join(text_field).strip()
                if not original_text:
                    Logger.debug("Skipping empty text block.")
                    continue

                Logger.debug(f"Original text to translate: '{original_text}'")

                # 1) Übersetzung aufrufen
                translated_result = self.translation_service.translate_text(model, original_text)

                # 2) Sicherstellen, dass 'translated_result' ein String ist
                #    Falls der Übersetzer eine Liste zurückgibt, machen wir daraus einen String.
                if isinstance(translated_result, list):
                    joined_text = " ".join(translated_result)
                else:
                    # Falls es schon ein String ist
                    joined_text = str(translated_result)

                joined_text = joined_text.strip()
                Logger.debug(f"Translated text: '{joined_text}'")

                # 3) Ersetze das 'text'-Feld wieder durch eine Wörter-Liste
                item["text"] = joined_text.split(" ")

        Logger.info("✅ Successfully processed and translated all text blocks.")
        return text_data





