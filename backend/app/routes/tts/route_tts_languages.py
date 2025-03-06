import traceback

from flask_restful import Resource
from backend.app.utils.util_logger import Logger

class LanguageTTS(Resource):
    def __init__(self, config_manager, cache_manager):
        self.config_manager = config_manager
        self.cache_manager = cache_manager

    def get(self):
        try:
            languages = self.config_manager.get_tts_languages()

            if not languages:
                Logger.warning("No TTS languages found in configuration.")
                return {"error": "No TTS languages available"}, 404

            Logger.info(f"Returning available languages: {languages}")
            return {"languages": languages}, 200

        except Exception as e:
            Logger.error(f"Error retrieving TTS languages: {str(e)}\n{traceback.format_exc()}")
            return {"error": "Failed to retrieve TTS languages"}, 500

