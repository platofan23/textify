import os

from flask import Flask
from flask_cors import CORS

from backend.app.utils import ConfigManager, CacheManager
from backend.app.utils.util_mongo_manager import MongoDBManager
from backend.app.utils.util_logger import Logger  # Importiere die Logger-Klasse

def create_app(config_path='./config/config.ini'):
    """
    Creates and configures the Flask app.

    Args:
        config_path (str): Path to the configuration file.

    Returns:
        Flask: Configured Flask application instance.
        ConfigManager: ConfigManager instance.
        CacheManager: CacheManager instance.
    """

    if os.getenv("IsDocker"):
        config_path = './config/docker.ini'

    Logger.info(f"Environment is in Docker: {os.getenv('IsDocker')}")

    app = Flask(__name__)
    config_manager = ConfigManager(config_path)
    Logger.info(f"Loaded configuration from: {config_path}")

    cache_manager = CacheManager(
        maxsize=config_manager.get_config_value('CACHE', 'MAX_ENTRIES', int),
        clear_cache_on_start=True
    )
    Logger.info("CacheManager initialized with maximum size: " + str(config_manager.get_config_value('CACHE', 'MAX_ENTRIES', int)))

    mongo_manager = MongoDBManager()
    Logger.info("MongoDBManager initialized.")

    # Configure Flask app
    max_content_length_mb = config_manager.get_config_value('REST', 'MAX_CONTENT_LENGTH_MB', int, default=10)
    app.config['MAX_CONTENT_LENGTH'] = max_content_length_mb * 1024 * 1024
    Logger.info(f"Set Flask MAX_CONTENT_LENGTH to: {max_content_length_mb} MB")

    CORS(app, origins=[
        "https://172.142.0.5:5173",
        "https://localhost:5173",
        "https://127.0.0.1:5173"
    ])
    Logger.info("CORS configured with allowed origins.")

    return app, config_manager, cache_manager
