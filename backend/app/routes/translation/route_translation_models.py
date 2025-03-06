from flask_restful import Resource
import traceback
from backend.app.utils.util_logger import Logger

class ModelTranslation(Resource):
    def __init__(self, config_manager, cache_manager):
        self.config_manager = config_manager
        self.cache_manager = cache_manager

    def get(self):
        try:
            models = self.config_manager.get_translation_models()

            if not models:
                Logger.warning("No translation models found in configuration.")
                return {"error": "No translation models available"}, 404

            Logger.info(f"Returning available translation models: {models}")
            return {"models": models}, 200

        except Exception as e:
            Logger.error(f"Error retrieving translation models: {str(e)}\n{traceback.format_exc()}")
            return {"error": "Failed to retrieve translation models"}, 500
