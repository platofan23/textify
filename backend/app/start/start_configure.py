import os

from flask import Flask
from flask_cors import CORS

from backend.app.utils import ConfigManager, CacheManager

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
        config_path='./config/docker.ini'

    print("Environment is in Docker:", os.getenv("IsDocker"))

    app = Flask(__name__)
    config_manager = ConfigManager(config_path)
    cache_manager = CacheManager(maxsize=10000, clear_cache_on_start=True)

    # Configure Flask app
    max_content_length_mb = config_manager.get_config_value('REST', 'MAX_CONTENT_LENGTH_MB', int, default=10)
    app.config['MAX_CONTENT_LENGTH'] = max_content_length_mb * 1024 * 1024
    CORS(app)

    return app, config_manager, cache_manager
