import traceback

from flask_restful import Resource
from backend.app.utils.util_logger import Logger

class SpeakerTTS(Resource):
    def __init__(self, config_manager, cache_manager):
        self.config_manager = config_manager
        self.cache_manager = cache_manager

    def get(self):
        try:
            speakers = self.config_manager.get_tts_speakers()

            if not  speakers:
                Logger.warning("No TTS  speakers found in configuration.")
                return {"error": "No TTS  speakers available"}, 404

            Logger.info(f"Returning available TTS  speakers: { speakers}")
            return {"models":  speakers}, 200

        except Exception as e:
            Logger.error(f"Error retrieving TTS  speakers: {str(e)}\n{traceback.format_exc()}")
            return {"error": "Failed to retrieve TTS  speakers"}, 500

