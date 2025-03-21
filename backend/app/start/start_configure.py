import os

from flask import Flask
from flask_cors import CORS
import torch

from backend.app.utils import ConfigManager, CacheManager, CryptoManager
from backend.app.utils.util_mongo_manager import MongoDBManager
from backend.app.utils.util_logger import Logger


def create_app(config_path='./config/config.ini'):
    """
    Creates and configures the Flask application.

    Args:
        config_path (str): Path to the configuration file. Defaults to './config/config.ini'.

    Returns:
        tuple: (Flask application instance, ConfigManager instance, CacheManager instance,
                MongoDBManager instance, Crypto_Manager instance)
    """
    # Configure Torch threading options.
    #torch.set_num_threads(4)         # Use up to 4 threads for intra-op parallelism
    #torch.set_num_interop_threads(2)   # Use 2 threads for inter-op parallelism

    Logger.info(f"Running in Docker: {os.getenv('IsDocker')}")

    # Initialize the Flask application.
    app = Flask(__name__)

    # Initialize configuration manager.
    config_manager = ConfigManager()

    # Initialize cache manager using configured maximum entries and clear cache on startup.
    max_entries = config_manager.get_config_value('CACHE', 'MAX_ENTRIES', int)
    cache_manager = CacheManager(maxsize=max_entries, clear_cache_on_start=True)
    crypto_manager = CryptoManager(config_manager)
    Logger.info(f"CacheManager initialized with max size: {max_entries}")

    # Initialize MongoDB manager.
    mongo_manager = MongoDBManager(crypto_manager)
    Logger.info("MongoDBManager initialized.")

    # Configure Flask settings.
    max_content_length_mb = config_manager.get_config_value('REST', 'MAX_CONTENT_LENGTH_MB', int, default=10)
    app.config['MAX_CONTENT_LENGTH'] = max_content_length_mb * 1024 * 1024
    Logger.info(f"Set Flask MAX_CONTENT_LENGTH to: {max_content_length_mb} MB")
    app.root_path = os.getcwd()
    Logger.debug(f"Flask root path: {app.root_path}")

    # Enable CORS for specified origins.
    cors_urls = config_manager.get_cors_urls()
    CORS(app, origins=cors_urls)
    Logger.info("CORS configured for allowed origins.")

    return app, config_manager, cache_manager, mongo_manager, crypto_manager
