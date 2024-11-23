from flask import Flask
import configparser
from routes.file_manager import files_bp

# Load configuration from config.ini
config = configparser.ConfigParser()
config.read('../../config.ini')

# Set up Flask
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = int(config['REST']['MAX_CONTENT_LENGTH_MB']) * 1024 * 1024

# Register Blueprints
app.register_blueprint(files_bp)

if __name__ == '__main__':
    app.run()