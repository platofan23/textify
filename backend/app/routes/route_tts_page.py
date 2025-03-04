from flask import request, send_file
from flask_restful import Resource
from backend.app.services.service_tts import TTSService
from backend.app.utils.util_logger import Logger
import io


class TTSPage(Resource):
    """
    Handles TTS synthesis for a given page by retrieving text from the database,
    generating an audio file, storing it in GridFS, and returning it to the client.
    """

    def __init__(self, config_manager, cache_manager, mongo_manager, crypto_manager):
        """
        Initializes `TTSPage` with:
        - `config_manager`: Configuration values for MongoDB
        - `cache_manager`: Cache for models & results
        - `mongo_manager`: MongoDBManager for CRUD operations & GridFS
        - `crypto_manager`: Encryption manager for audio files
        """
        self.tts_service = TTSService(config_manager, cache_manager)
        self.config_manager = config_manager
        self.mongo_manager = mongo_manager
        self.crypto_manager = crypto_manager
        Logger.info("TTSPage instance initialized.")

    def post(self):
        """Processes a TTS request, generates audio if not available, and returns it."""
        Logger.info("Received POST request for TTS.")

        json_data = request.get_json()
        if not json_data or "data" not in json_data:
            Logger.warning("Missing 'data' object in request.")
            return {"error": "Missing data object"}, 400

        data = json_data["data"]
        user, page, title, language = data.get("user"), data.get("page"), data.get("title"), data.get("language", "de")
        model, speaker = data.get("model", "tts_models/multilingual/multi-dataset/xtts_v2"), data.get("speaker", "Daisy Studious")

        if not user or page is None or not title:
            Logger.warning("Missing required parameters: user, page, or title.")
            return {"error": "Missing required parameters (user, page, title)."}, 400

        try:
            Logger.info(f"Checking if TTS file already exists: user={user}, page={page}, title='{title}', language={language}")

            # Check if the TTS file already exists in GridFS
            existing_audio = self.mongo_manager.retrieve_tts_audio_from_gridfs(user, page, title, language)
            if existing_audio:
                Logger.info(f"Returning existing TTS file from GridFS for title: {title}")
                return send_file(existing_audio, mimetype="audio/wav", as_attachment=True, download_name="tts_output.wav")

            # Retrieve and decrypt text from the database
            Logger.info("No existing audio found. Fetching text from the database.")
            user_files_collection = self.config_manager.get_mongo_config().get("user_files_collection", "user_files")
            text_data = self.mongo_manager.retrieve_and_decrypt_page(user, page, title, user_files_collection, self.crypto_manager)

            if not text_data:
                Logger.warning("No text found in the database for TTS synthesis.")
                return {"error": "No text available to synthesize."}, 404

            text = self._extract_text_from_structure(text_data)
            Logger.info("Successfully extracted and formatted text for TTS synthesis.")

            # Generate new TTS audio
            audio_buffer = self._synthesize_audio(text, model, speaker, language)

            # Encrypt and store the TTS audio in GridFS
            file_id = self._encrypt_and_store_audio(user, page, title, language, audio_buffer)
            Logger.info(f"Stored new TTS audio in GridFS with ID: {file_id}")

            # Return the generated TTS audio
            Logger.info("Returning newly synthesized TTS audio file.")
            return send_file(audio_buffer, mimetype="audio/wav", as_attachment=True, download_name="tts_output.wav")

        except ValueError as ve:
            Logger.error(f"Invalid input: {str(ve)}")
            return {"error": f"Invalid input: {str(ve)}"}, 422
        except Exception as e:
            Logger.error(f"Internal Server Error during TTS processing: {str(e)}")
            return {"error": f"Internal Server Error: {str(e)}"}, 500

    def _extract_text_from_structure(self, text_data):
        """
        Extracts text from structured OCR format and converts it into a single string.

        Args:
            text_data (list): List containing nested text data.

        Returns:
            str: Formatted continuous text.
        """
        extracted_text = []

        try:
            if isinstance(text_data, list):
                for item in text_data:
                    block = item.get("Block", {})
                    for entry in block.get("Data", []):
                        text_segment = entry.get("text")
                        if isinstance(text_segment, list):
                            extracted_text.append(" ".join(text_segment))

            final_text = " ".join(extracted_text)
            Logger.info(f"Extracted text for TTS synthesis: {final_text[:100]}...")  # Log only first 100 chars
            return final_text

        except Exception as e:
            Logger.error(f"Error extracting text from structure: {str(e)}")
            return ""

    def _synthesize_audio(self, text, model, speaker, language):
        """
        Generates TTS audio using the provided model, speaker, and language.

        Args:
            text (str): Input text for synthesis.
            model (str): TTS model to use.
            speaker (str): Speaker identity for the model.
            language (str): Language for synthesis.

        Returns:
            io.BytesIO: Audio file buffer.
        """
        Logger.info("Synthesizing new TTS audio.")
        audio_buffer = self.tts_service.synthesize_audio(text, model, speaker, language)

        if isinstance(audio_buffer, io.BytesIO):
            audio_buffer.seek(0)
            return audio_buffer
        elif isinstance(audio_buffer, bytes):
            return io.BytesIO(audio_buffer)
        else:
            raise TypeError("Unexpected audio format received!")

    def _encrypt_and_store_audio(self, user, page, title, language, audio_buffer):
        """
        Encrypts the generated TTS audio and stores it in GridFS.

        Args:
            user (str): User identifier.
            page (int): Page number.
            title (str): Title of the document.
            language (str): Language of the TTS output.
            audio_buffer (io.BytesIO): The synthesized audio buffer.

        Returns:
            str: ID of the stored GridFS file.
        """
        file_data = audio_buffer.getvalue()
        encrypted_audio = self.crypto_manager.encrypt_audio(user, file_data)

        # Ensure the encrypted data is in bytes format
        if isinstance(encrypted_audio, dict):
            encrypted_audio = encrypted_audio.get("Ciphertext", b"")

        if not isinstance(encrypted_audio, bytes):
            raise ValueError("Encrypted audio is not in bytes format!")

        return self.mongo_manager.store_tts_audio_in_gridfs(
            query={"title": title, "page": page, "user": user, "language": language},
            file_data=encrypted_audio
        )
