import os
import shutil
import configparser

from flask import send_file
from flask_restful import Resource, reqparse
from werkzeug.datastructures import FileStorage

# Konfiguration laden
config = configparser.ConfigParser()
config.read('./config/config.ini')
if os.getenv("IsDocker"):
    config.read('./config/docker.ini')
MAX_TOTAL_SIZE = int(config['REST']['MAX_TOTAL_SIZE_GB']) * 1024 * 1024 * 1024
ALLOWED_EXTENSIONS = set(config['REST']['ALLOWED_EXTENSIONS'].replace(" ", "").split(','))
UPLOAD_FOLDER = config['REST']['UPLOAD_FOLDER']


# Hilfsfunktion zur Dateityp-Überprüfung
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Ressource für Datei-Upload
class UploadFile(Resource):
    def post(self):
        # Parameter validieren
        parser = reqparse.RequestParser()
        parser.add_argument('User', location='headers', required=True, help="User header is required")
        parser.add_argument('Title', location='headers', required=True, help="Title header is required")
        parser.add_argument('files', type=FileStorage, location='files', action='append', required=True)
        args = parser.parse_args()

        files = args['files']
        user = args['User']
        title = args['Title']

        total_size = 0

        # Zielverzeichnisse erstellen
        user_folder_path = os.path.join(UPLOAD_FOLDER, user)
        os.makedirs(user_folder_path, exist_ok=True)
        title_folder_path = os.path.join(user_folder_path, title)
        os.makedirs(title_folder_path, exist_ok=True)

        # Dateien speichern
        for file in files:
            if file.filename == '':
                return {'error': 'No selected file'}, 400
            if allowed_file(file.filename):
                total_size += len(file.read())
                file.seek(0)
                if total_size > MAX_TOTAL_SIZE:
                    shutil.rmtree(title_folder_path)
                    return {'error': f'Total file size exceeds {MAX_TOTAL_SIZE} bytes'}, 413
                file.save(os.path.join(title_folder_path, file.filename))
            else:
                return {'error': 'Invalid file type'}, 415
        return {'message': 'Files uploaded successfully'}, 201


# Ressource für Datei-Download
class DownloadFile(Resource):
    def get(self):
        # Parameter validieren
        parser = reqparse.RequestParser()
        parser.add_argument('filename', type=str, required=True, help="Filename is required")
        parser.add_argument('user', type=str, required=True, help="User is required")
        parser.add_argument('title', type=str, required=True, help="Title is required")
        args = parser.parse_args()

        filename = args['filename']
        user = args['user']
        title = args['title']

        try:
            # Datei-Pfad zusammenbauen
            user_folder_path = os.path.join(UPLOAD_FOLDER, user)
            title_folder_path = os.path.join(user_folder_path, title)
            file_path = os.path.join(title_folder_path, filename)

            if not os.path.exists(file_path):
                return {'error': 'File not found'}, 404

            # Datei senden
            return send_file(file_path, download_name=filename, as_attachment=True)
        except Exception as e:
            return {'error': f'Error occurred: {str(e)}'}, 500
