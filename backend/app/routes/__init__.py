import configparser

from flask import Flask
from backend.app.routes.file_manager import file_manager_bp
from backend.app.routes.ocr import ocr_bp

def create_app():
    # Load configuration from config.ini
    config = configparser.ConfigParser()
    config.read('../../config.ini')

    app = Flask(__name__)
    app.config['MAX_CONTENT_LENGTH'] = int(config['REST']['MAX_CONTENT_LENGTH_MB']) * 1024 * 1024

    # Register Blueprints
    app.register_blueprint(file_manager_bp)
    app.register_blueprint(ocr_bp)

    return app