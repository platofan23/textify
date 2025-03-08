import io
from flask import request, send_file
from flask_restful import Resource

from backend.app.services.tts import TTSService
from backend.app.utils.util_logger import Logger


class TTSPage(Resource):
    """
    Handles TTS synthesis for a given page by retrieving source text from the database,
    generating a TTS audio file, storing it in GridFS (encrypted), and returning the
    decrypted audio to the client.
    """

    def __init__(self, config_manager, cache_manager, mongo_manager, crypto_manager):
        """
        Initializes TTSPage with configuration, caching, MongoDB management, and encryption.
        """
        self.tts_service = TTSService(config_manager, cache_manager)
        self.config_manager = config_manager
        self.mongo_manager = mongo_manager
        self.crypto_manager = crypto_manager
        Logger.info("TTSPage instance initialized.")

    def post(self):
        """
        Processes a TTS request:
          1. Checks if an encrypted TTS audio file already exists in GridFS.
             If found, its metadata is used to decrypt and return the audio.
          2. Otherwise, retrieves source text from the database,
             synthesizes new audio, encrypts and stores it in GridFS,
             and returns the newly synthesized audio.
        """
        Logger.info("Received POST request for TTS.")
        json_data = request.get_json()
        if not json_data or "data" not in json_data:
            Logger.warning("Missing 'data' object in request.")
            return {"error": "Missing data object"}, 400

        data = json_data["data"]
        user = data.get("user")
        page = data.get("page")
        title = data.get("title")
        language = data.get("language", "en")
        model = data.get("model", "tts_models/multilingual/multi-dataset/xtts_v2")
        speaker = data.get("speaker", "Daisy Studious")

        if not user or page is None or not title:
            Logger.warning("Missing required parameters: user, page, or title.")
            return {"error": "Missing required parameters (user, page, title)."}, 400

        try:
            Logger.info(f"Processing TTS request for user={user}, page={page}, title='{title}', language={language}")

            # Check if the TTS audio already exists in GridFS.
            existing_audio_obj = self.mongo_manager.retrieve_tts_audio_from_gridfs(user, page, title, language)
            if existing_audio_obj:
                Logger.info("Existing TTS audio found in GridFS. Decrypting audio before returning.")
                ciphertext = existing_audio_obj.read()
                metadata = existing_audio_obj.metadata  # Metadata stored during insertion
                encryption_dict = {
                    "Ciphertext": ciphertext,
                    "Nonce": metadata.get("Nonce"),
                    "Tag": metadata.get("Tag"),
                    "Ephemeral_public_key_der": metadata.get("Ephemeral_public_key_der")
                }
                decrypted_audio = self.crypto_manager.decrypt_audio(user, encryption_dict)
                # Return the decrypted audio stream directly
                return send_file(decrypted_audio, mimetype=self.config_manager.get_tts_mimetype(), as_attachment=self.config_manager.get_tts_as_attachment(), download_name=self.config_manager.get_tts_download_name())

            Logger.info("No existing TTS audio found. Retrieving source text from the database.")
            user_files_collection = self.config_manager.get_mongo_config().get("user_text_collection", "user_texts")
            source_data = self.mongo_manager.retrieve_and_decrypt_page(user, page, title, user_files_collection)
            if not source_data:
                Logger.warning("No source text available for TTS synthesis.")
                return {"error": "No text available to synthesize."}, 404

            text = self._extract_text_from_structure(source_data)
            Logger.info("Successfully extracted and formatted text for TTS synthesis.")

            # Generate new TTS audio.
            audio_buffer = self._synthesize_audio(text, model, speaker, language)
            Logger.info("New TTS audio synthesized successfully.")

            # Encrypt and store the new TTS audio in GridFS.
            file_id = self._encrypt_and_store_audio(user, page, title, language, audio_buffer)
            Logger.info(f"Stored new TTS audio in GridFS with ID: {file_id}")

            # Return the newly synthesized TTS audio.
            audio_buffer.seek(0)
            return send_file(audio_buffer, mimetype=self.config_manager.get_tts_mimetype(), as_attachment=self.config_manager.get_tts_as_attachment(), download_name=self.config_manager.get_tts_download_name())

        except ValueError as ve:
            Logger.error(f"Invalid input: {ve}")
            return {"error": f"Invalid input: {ve}"}, 422
        except Exception as e:
            Logger.error(f"Internal Server Error during TTS processing: {e}")
            return {"error": f"Internal Server Error: {e}"}, 500

    def _synthesize_audio(self, text, model, speaker, language):
        """
        Generates TTS audio using the provided text, model, speaker, and language.

        Args:
            text (str): Text for synthesis.
            model (str): TTS model identifier.
            speaker (str): Speaker identity.
            language (str): Language code.

        Returns:
            io.BytesIO: Audio file buffer.
        """
        Logger.info("Synthesizing TTS audio.")
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
        Encrypts the synthesized TTS audio and stores it in GridFS.

        Args:
            user (str): User identifier.
            page (int): Page number.
            title (str): Document title.
            language (str): Language code.
            audio_buffer (io.BytesIO): Synthesized audio buffer.

        Returns:
            str: ID of the stored GridFS file.
        """
        file_data = audio_buffer.getvalue()
        encryption_dict = self.crypto_manager.encrypt_audio(user, file_data)
        # Extract the 'Ciphertext' from the encryption output and prepare metadata
        if isinstance(encryption_dict, dict):
            encrypted_audio = encryption_dict.get("Ciphertext", b"")
            metadata = {
                "Nonce": encryption_dict.get("Nonce"),
                "Tag": encryption_dict.get("Tag"),
                "Ephemeral_public_key_der": encryption_dict.get("Ephemeral_public_key_der")
            }
        else:
            raise ValueError("Encryption failed: Unexpected output format.")
        if not isinstance(encrypted_audio, bytes):
            raise ValueError("Encrypted audio is not in bytes format!")
        return self.mongo_manager.store_tts_audio_in_gridfs(
            query={"title": title, "page": page, "user": user, "language": language},
            file_data=encrypted_audio,
            metadata=metadata
        )

    @staticmethod
    def _extract_text_from_structure(text_data):
        """
        Extracts text from structured OCR data and concatenates it into a single string.

        Args:
            text_data (list): List containing nested OCR text data.

        Returns:
            str: Combined text for TTS synthesis.
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
            Logger.info(f"Extracted text (first 100 chars): {final_text[:100]}...")
            return final_text
        except Exception as e:
            Logger.error(f"Error extracting text from structure: {e}")
            return ""
