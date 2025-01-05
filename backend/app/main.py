# General imports
import configparser
from flask import Flask
from flask_cors import CORS
from flask_restful import Api

# Import routes
from routes import *

# Config
config = configparser.ConfigParser()
config.read('../config/config.ini')

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = int(config['REST']['MAX_CONTENT_LENGTH_MB']) * 1024 * 1024
CORS(app)
api = Api(app)

# Endpoints file
api.add_resource(DownloadFile, '/download_file')
api.add_resource(UploadFile, '/upload_files')

# Endpoint user
api.add_resource(ReadFile, '/read_file')

# Endpoints translation
api.add_resource(TranslateFile, '/translate_file')
api.add_resource(TranslateText, '/translate_text')

# Endpoints user
api.add_resource(RegisterUser, '/register')
api.add_resource(LoginUser, '/login')

# Start flask-app
if __name__ == '__main__':
    port = int(config['REST'].get('PORT', '5555'))
    host = config['REST'].get('HOST', '127.0.0.1')
    app.run(host=host,port=port,debug=True)

