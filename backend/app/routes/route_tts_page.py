from flask import request, send_file, make_response
from flask_restful import Resource, reqparse
from backend.app.services.service_tts import TTSService
from backend.app.utils.util_logger import Logger

class TTSPage(Resource):
    """
    Handles TTS synthesis for a page by receiving text, model, speaker, language, page, title, and user,
    updating or inserting the resulting encrypted audio into the tts_files collection, and returning the audio file.
    """
    _instance = None  # Singleton instance

    def __init__(self, config_manager, cache_manager, mongo_manager, crypto_manager):
        """
        Initializes TTSPage with instances of ConfigManager, CacheManager, MongoDBManager, and Crypto_Manager.

        Args:
            config_manager: Provides configuration details.
            cache_manager: Manages caching of TTS results.
            mongo_manager: The MongoDB manager instance.
            crypto_manager: The crypto manager instance for encryption.
        """
        self.tts_service = TTSService(config_manager, cache_manager)
        self.config_manager = config_manager
        self.mongo_manager = mongo_manager
        self.crypto_manager = crypto_manager
        Logger.info("TTSPage instance initialized.")

    def post(self):
        """
        Handles POST requests for TTS.
        Expects a JSON payload with the following data:
            - text: The text to synthesize.
            - model: The TTS model to use (default provided).
            - speaker: The speaker to use (default provided).
            - language: The language for the audio (default "de").
            - page: The page number.
            - title: The title associated with the file.
            - user: The user identifier.
        After synthesis, the encrypted audio is upserted in the tts_files collection based on title, page, user, and language.
        The audio file is then returned.
        """
        Logger.info("POST request received for TTS.")

        json_data = request.get_json()
        if not json_data or 'data' not in json_data:
            Logger.warning("Missing 'data' object in request.")
            return {"error": "Missing data object"}, 400

        data = json_data['data']
        text = data.get('text')
        model = data.get('model', "tts_models/multilingual/multi-dataset/xtts_v2")
        speaker = data.get('speaker', 'Daisy Studious')
        language = data.get('language', "de")
        page = data.get('page')
        title = data.get('title')
        user = data.get('user')

        if not text:
            Logger.warning("Missing required 'text' parameter in the request.")
            return {"error": "Missing required 'text' parameter"}, 400

        try:
            Logger.info(f"Starting TTS synthesis with text='{text[:30]}...' (truncated), model='{model}', speaker='{speaker}', language='{language}'.")
            # Synthesize audio using the TTS service.
            audio_buffer = self.tts_service.synthesize_audio(text, model, speaker, language)
            Logger.info("Audio synthesis completed successfully.")

            # Encrypt the audio using the crypto manager.
            encrypted_audio = self.crypto_manager.encrypt_audio(user, audio_buffer)

            # Retrieve the collection name for TTS files from configuration.
            collection_name = self.config_manager.get_mongo_config().get("tts_files_collection", "tts_files")
            if not collection_name:
                Logger.error("TTS files collection name is not defined in configuration.")
                return {"error": "Configuration error: Missing TTS files collection name"}, 500

            # Build query based on title, page, user, and language.
            query = {
                "title": title,
                "page": page,
                "user": user,
                "language": language
            }
            # Build update operation to set the encrypted audio.
            update_op = {
                "$set": {
                    "encrypted_audio": encrypted_audio
                }
            }

            # Update the document if it exists, otherwise insert a new one.
            update_result = self.mongo_manager.update_document(collection_name, query, update_op, upsert=True)
            Logger.info(f"Update result: Matched: {update_result.matched_count}, Modified: {update_result.modified_count}.")

            # Return the synthesized audio file.
            Logger.info("TTS processing completed successfully. Returning audio file.")
            return send_file(
                audio_buffer,
                mimetype="audio/wav",
                as_attachment=True,
                download_name="output.wav"
            )
        except ValueError as ve:
            Logger.error(f"Invalid input: {str(ve)}")
            return {"error": f"Invalid input: {str(ve)}"}, 422
        except Exception as e:
            Logger.error("Internal Server Error during TTS processing.")
            return {"error": f"Internal Server Error: {str(e)}"}, 500
