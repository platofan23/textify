from flask import request, send_file
from flask_restful import Resource
from backend.app.services.service_tts import TTSService
from backend.app.utils.util_logger import Logger

class TTS(Resource):
    def __init__(self, config_manager, cache_manager):
        self.tts_service = TTSService(config_manager, cache_manager)
        Logger.info("TTS instance initialized.")

    def post(self):
        Logger.info("POST request received for TTS.")

        json_data = request.get_json()

        if not json_data or 'data' not in json_data:
            Logger.warning("Missing 'data' object in request.")
            return {"error": "Missing data object"}, 400

        data = json_data['data']
        text = data.get('text')
        if not text:
            Logger.warning("Missing required 'text' parameter in the request.")
            return {"error": "Missing required 'text' parameter"}, 400

        try:
            Logger.info(f"Starting TTS with text='{text[:30]}...' (truncated for log).")
            audio_buffer = self.tts_service.synthesize_audio(text, None, None)
            Logger.info("TTS completed successfully. Returning audio file.")
            return send_file(
                audio_buffer,
                mimetype="audio/wav",
                as_attachment=True,
                download_name="output.wav"
            )
        except Exception as e:
            Logger.error(f"Internal Server Error: {str(e)}")
            return {"error": f"Internal Server Error: {str(e)}"}, 500
