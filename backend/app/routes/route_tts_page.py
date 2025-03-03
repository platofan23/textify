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
            text = self.mongo_manager.retrieve_and_decrypt_page(
                user=user, page=page, title=title, user_files_collection=user_files_collection,
                crypto_manager=self.crypto_manager
            )
            Logger.info("Text retrieved from DB for TTS synthesis.")

            if not text:
                Logger.warning("No text found in DB for TTS synthesis.")
                return {"error": "No text available to synthesize."}, 404

            # 3️⃣ **Generate TTS audio**
            Logger.info("Synthesizing new TTS audio.")
            audio_buffer = self.tts_service.synthesize_audio(text, model, speaker, language)
            Logger.info("Audio synthesis completed successfully.")

            # 4️⃣ **Encrypt and Store in GridFS**
            encrypted_audio = self.crypto_manager.encrypt_audio(user, audio_buffer)

            query = {"title": title, "page": page, "user": user, "language": language}
            update_op = {"$set": {}}  # Empty update operation for GridFS

            # Use GridFS for storing the audio
            update_result = self.mongo_manager.update_document(
                collection_name=tts_collection,
                query=query,
                update=update_op,
                upsert=True,
                use_GridFS=True,
                gridfs_field="encrypted_audio",  # Store file in GridFS
                file_data=encrypted_audio  # The encrypted audio data
            )

            Logger.info(f"Stored new TTS audio in GridFS. Matched={update_result.matched_count}, Modified={update_result.modified_count}.")

            # 5️⃣ **Return the newly synthesized audio**
            Logger.info("Returning newly synthesized TTS audio file.")
            audio_buffer.seek(0)
            return send_file(audio_buffer, mimetype="audio/wav", as_attachment=True, download_name="output.wav")

        except ValueError as ve:
            Logger.error(f"Invalid input: {str(ve)}")
            return {"error": f"Invalid input: {str(ve)}"}, 422
        except Exception as e:
            Logger.error(f"Internal Server Error during TTS processing: {str(e)}")
            return {"error": f"Internal Server Error: {str(e)}"}, 500
