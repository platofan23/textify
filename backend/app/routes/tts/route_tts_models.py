import traceback

from flask_restful import Resource
from backend.app.utils.util_logger import Logger

class ModelTTS(Resource):
    def __init__(self, config_manager, cache_manager):
        self.config_manager = config_manager
        self.cache_manager = cache_manager

    def get(self):
        try:
            models = self.config_manager.get_tts_models()

            if not models:
                Logger.warning("No TTS models found in configuration.")
                return {"error": "No TTS models available"}, 404

            Logger.info(f"Returning available TTS models: {models}")
            return {"models": models}, 200

        except Exception as e:
            Logger.error(f"Error retrieving TTS models: {str(e)}\n{traceback.format_exc()}")
            return {"error": "Failed to retrieve TTS models"}, 500

