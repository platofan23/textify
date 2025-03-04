from flask import request, send_file
from flask_restful import Resource
from backend.app.services.service_tts import TTSService
from backend.app.utils.util_logger import Logger
import io


class TTSPage(Resource):
    """
    Handles TTS synthesis for a page by receiving model, speaker, language, page, title, and user.
    Retrieves text from DB if no audio exists, updates or inserts encrypted audio in GridFS,
    and returns the audio file.
    """

    def __init__(self, config_manager, cache_manager, mongo_manager, crypto_manager):
        """
        Initializes TTSPage with ConfigManager, CacheManager, MongoDBManager, and Crypto_Manager.
        """
        self.tts_service = TTSService(config_manager, cache_manager)
        self.config_manager = config_manager
        self.mongo_manager = mongo_manager
        self.crypto_manager = crypto_manager
        Logger.info("TTSPage instance initialized.")

    def post(self):
        Logger.info("POST request received for TTS.")

        json_data = request.get_json()
        if not json_data or 'data' not in json_data:
            Logger.warning("Missing 'data' object in request.")
            return {"error": "Missing data object"}, 400

        data = json_data['data']
        model = data.get('model', "tts_models/multilingual/multi-dataset/xtts_v2")
        speaker = data.get('speaker', 'Daisy Studious')
        language = data.get('language', "de")
        page = data.get('page')
        title = data.get('title')
        user = data.get('user')

        # Basic required fields
        if not user or page is None or not title:
            Logger.warning("Missing required parameters: user, page, or title.")
            return {"error": "Missing required parameters (user, page, title)."}, 400

        try:
            Logger.info(f"Starting TTS synthesis: user={user}, page={page}, title='{title}', language={language}")

            # 1️⃣ **Check if the audio already exists in GridFS**
            tts_collection = self.config_manager.get_mongo_config().get("tts_files_collection", "tts_files")
            doc, existing_audio = self.mongo_manager.retrieve_and_decrypt_tts_audio(
                user=user, page=page, title=title, language=language,
                tts_files_collection=tts_collection, crypto_manager=self.crypto_manager
            )

            if existing_audio:
                Logger.info(f"TTS audio already exists for user={user}, page={page}, title={title}. Returning existing file.")
                return send_file(existing_audio, mimetype="audio/wav", as_attachment=True, download_name="output.wav")

            # 2️⃣ **Retrieve text from DB if no audio found**
            Logger.info("No existing TTS audio found. Fetching text from DB.")
            user_files_collection = self.config_manager.get_mongo_config().get("user_files_collection", "user_files")
            text_data = self.mongo_manager.retrieve_and_decrypt_page(
                user=user, page=page, title=title, user_files_collection=user_files_collection,
                crypto_manager=self.crypto_manager
            )

            if not text_data:
                Logger.warning("No text found in DB for TTS synthesis.")
                return {"error": "No text available to synthesize."}, 404

            # 🔹 **Convert text structure to a single string**
            text = self._extract_text_from_structure(text_data)

            if not text.strip():
                Logger.warning("Extracted text is empty after formatting.")
                return {"error": "Extracted text is empty. Cannot proceed with TTS."}, 400

            Logger.info(f"Extracted text for TTS synthesis: {text[:100]}...")  # Log first 100 chars

            # 3️⃣ **Generate TTS audio**
            Logger.info("Synthesizing new TTS audio.")
            audio_buffer = self.tts_service.synthesize_audio(text, model, speaker, language)

            # 🔹 **Ensure we have a BytesIO object**
            if not isinstance(audio_buffer, io.BytesIO):
                raise ValueError("TTS output is not a valid BytesIO object.")

            audio_buffer.seek(0)
            file_data = audio_buffer.read()  # Convert to bytes

            # 4️⃣ **Encrypt and Store in GridFS**
            encrypted_audio = self.crypto_manager.encrypt_audio(user, file_data)

            query = {"title": title, "page": page, "user": user, "language": language}
            update_op = {"$set": {}}  # Empty update operation for GridFS

            # Use GridFS for storing the audio
            file_id = self.mongo_manager.update_document(
                collection_name=tts_collection,
                query=query,
                update=update_op,
                upsert=True,
                use_GridFS=True,
                file_data=encrypted_audio  # Ensure this is bytes!
            )

            Logger.info(f"Stored new TTS audio in GridFS with ID: {file_id}")

            # 5️⃣ **Return the newly synthesized audio**
            Logger.info("Returning newly synthesized TTS audio file.")

            # 🔹 **Convert bytes back to BytesIO before sending**
            audio_stream = io.BytesIO(file_data)
            audio_stream.seek(0)

            return send_file(audio_stream, mimetype="audio/wav", as_attachment=True, download_name="output.wav")

        except ValueError as ve:
            Logger.error(f"Invalid input: {str(ve)}")
            return {"error": f"Invalid input: {str(ve)}"}, 422
        except Exception as e:
            Logger.error(f"Internal Server Error during TTS processing: {str(e)}")
            return {"error": f"Internal Server Error: {str(e)}"}, 500

    def _extract_text_from_structure(self, text_data):
        """
        Extracts text from the structured OCR data and converts it to a single string.

        Args:
            text_data (list): List of dictionaries containing text in structured format.

        Returns:
            str: A single string with extracted text.
        """
        extracted_text = []

        try:
            if isinstance(text_data, list):
                for item in text_data:
                    if isinstance(item, dict) and "Block" in item and "Data" in item["Block"]:
                        for entry in item["Block"]["Data"]:
                            if "text" in entry and isinstance(entry["text"], list):
                                extracted_text.append(" ".join(entry["text"]))

            final_text = " ".join(extracted_text).strip()
            Logger.info(f"Extracted text for TTS synthesis: {final_text[:100]}...")  # Log first 100 chars
            return final_text

        except Exception as e:
            Logger.error(f"Error extracting text from structure: {str(e)}")
            return ""
