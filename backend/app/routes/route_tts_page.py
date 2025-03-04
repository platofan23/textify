from flask import request, send_file
from flask_restful import Resource
from backend.app.services.service_tts import TTSService
from backend.app.utils.util_logger import Logger
import io


class TTSPage(Resource):
    """
    Stellt TTS-Synthese für eine Seite bereit.
    Holt den Text aus der Datenbank, generiert eine Audiodatei, speichert sie in GridFS
    und gibt sie an den Client zurück.
    """

    def __init__(self, config_manager, cache_manager, mongo_manager, crypto_manager):
        """
        Initialisiert `TTSPage` mit:
        - `config_manager`: Konfigurationswerte für MongoDB
        - `cache_manager`: Cache für Modelle & Ergebnisse
        - `mongo_manager`: MongoDBManager für CRUD-Operationen & GridFS
        - `crypto_manager`: Verschlüsselungs-Manager für Audio-Daten
        """
        self.tts_service = TTSService(config_manager, cache_manager)
        self.config_manager = config_manager
        self.mongo_manager = mongo_manager
        self.crypto_manager = crypto_manager
        Logger.info("TTSPage instance initialized.")

    def post(self):
        """Empfängt eine TTS-Anfrage, verarbeitet sie und gibt eine Audiodatei zurück."""
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

        if not user or page is None or not title:
            Logger.warning("Missing required parameters: user, page, or title.")
            return {"error": "Missing required parameters (user, page, title)."}, 400

        try:
            Logger.info(f"Checking if TTS file already exists: user={user}, page={page}, title='{title}', language={language}")

            # 1️⃣ **Prüfen, ob die Audiodatei bereits existiert**
            existing_audio = self.mongo_manager.retrieve_tts_audio_from_gridfs(user, page, title, language)
            if existing_audio:
                Logger.info(f"✅ Returning existing TTS file from GridFS: {title}")
                return send_file(existing_audio, mimetype="audio/wav", as_attachment=True, download_name="tts_output.wav")

            # 2️⃣ **Text aus der Datenbank abrufen**
            Logger.info("No existing audio found. Fetching text from DB.")
            user_files_collection = self.config_manager.get_mongo_config().get("user_files_collection", "user_files")
            text_data = self.mongo_manager.retrieve_and_decrypt_page(
                user=user, page=page, title=title, user_files_collection=user_files_collection,
                crypto_manager=self.crypto_manager
            )

            if not text_data:
                Logger.warning("No text found in DB for TTS synthesis.")
                return {"error": "No text available to synthesize."}, 404

            text = self._extract_text_from_structure(text_data)

            Logger.info("Text successfully extracted and formatted for TTS synthesis.")

            # 3️⃣ **Neue TTS-Audio-Datei generieren**
            Logger.info("Synthesizing new TTS audio.")
            audio_buffer = self.tts_service.synthesize_audio(text, model, speaker, language)

            # 🔹 Konvertiere in Bytes, falls notwendig
            if isinstance(audio_buffer, io.BytesIO):
                audio_buffer.seek(0)
                file_data = audio_buffer.read()
            elif isinstance(audio_buffer, bytes):
                file_data = audio_buffer
            else:
                raise TypeError("Unexpected audio format received!")

            Logger.info(f"✅ TTS synthesis completed. Audio size: {len(file_data)} bytes.")

            # 4️⃣ **TTS-Audio verschlüsseln und in GridFS speichern**
            encrypted_audio = self.crypto_manager.encrypt_audio(user, file_data)

            # GridFS erwartet reine Bytes → `Ciphertext` extrahieren
            if isinstance(encrypted_audio, dict):
                encrypted_audio = encrypted_audio["Ciphertext"]

            if not isinstance(encrypted_audio, bytes):
                raise ValueError("Encrypted audio is not in bytes format!")

            # Datei in GridFS speichern
            file_id = self.mongo_manager.store_tts_audio_in_gridfs(
                query={"title": title, "page": page, "user": user, "language": language},
                file_data=encrypted_audio
            )

            Logger.info(f"✅ Stored new TTS audio in GridFS with ID: {file_id}")

            # 5️⃣ **Datei an den Client zurückgeben**
            Logger.info("Returning newly synthesized TTS audio file.")
            return send_file(io.BytesIO(file_data), mimetype="audio/wav", as_attachment=True, download_name="tts_output.wav")

        except ValueError as ve:
            Logger.error(f"Invalid input: {str(ve)}")
            return {"error": f"Invalid input: {str(ve)}"}, 422
        except Exception as e:
            Logger.error(f"Internal Server Error during TTS processing: {str(e)}")
            return {"error": f"Internal Server Error: {str(e)}"}, 500

    def _extract_text_from_structure(self, text_data):
        """
        Extrahiert Text aus dem strukturierten OCR-Format und konvertiert ihn zu einem String.

        Args:
            text_data (list): Liste mit verschachtelten Textdaten.

        Returns:
            str: Formatierter zusammenhängender Text.
        """
        extracted_text = []

        try:
            if isinstance(text_data, list):
                for item in text_data:
                    if "Block" in item and "Data" in item["Block"]:
                        for entry in item["Block"]["Data"]:
                            if "text" in entry and isinstance(entry["text"], list):
                                extracted_text.append(" ".join(entry["text"]))

            final_text = " ".join(extracted_text)
            Logger.info(f"Extracted text for TTS synthesis: {final_text[:100]}...")  # Log nur die ersten 100 Zeichen
            return final_text

        except Exception as e:
            Logger.error(f"Error extracting text from structure: {str(e)}")
            return ""
