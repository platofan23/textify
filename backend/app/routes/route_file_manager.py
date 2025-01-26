import os
import configparser
from flask import send_file
from flask_restful import Resource, reqparse
from werkzeug.datastructures import FileStorage
from backend.app.utils import MongoDBManager, ConfigManager
from backend.app.utils.util_logger import Logger

# Load configuration
CONFIG_PATH = os.getenv("CONFIG_PATH", "./config/config.ini")  # Standardmäßiger Pfad zur Konfigurationsdatei
DOCKER_CONFIG_PATH = "./config/docker.ini"

config_path = CONFIG_PATH
if os.getenv("IsDocker"):
    config_path = DOCKER_CONFIG_PATH

if not os.path.exists(config_path):
    raise FileNotFoundError(f"Configuration file not found at {config_path}")

config_manager = ConfigManager(config_path)
config = configparser.ConfigParser()
config.read(config_path)

MAX_TOTAL_SIZE = int(config['REST']['MAX_TOTAL_SIZE_GB']) * 1024 * 1024 * 1024
ALLOWED_EXTENSIONS = set(config['REST']['ALLOWED_EXTENSIONS'].replace(" ", "").split(','))

# MongoDB setup
mongo_manager = MongoDBManager(config_manager)

# Helper function to check allowed file types
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Resource for file upload
class UploadFile(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('User', location='headers', required=True, help="User header is required")
        parser.add_argument('Title', location='headers', required=True, help="Title header is required")
        parser.add_argument('files', type=FileStorage, location='files', action='append', required=True)
        args = parser.parse_args()

        files = args['files']
        user = args['User']
        title = args['Title']

        if not files or len(files) == 0:
            Logger.error('No files uploaded')
            return {'error': 'No files uploaded'}, 400

        total_size = 0
        file_ids = []

        try:
            for file in files:
                if file.filename == '':
                    Logger.error('No selected file')
                    return {'error': 'No selected file'}, 400

                if not allowed_file(file.filename):
                    Logger.error('Invalid file type')
                    return {'error': f"Invalid file type: {file.filename}"}, 415

                file_size = len(file.read())
                file.seek(0)  # Setze den Lesezeiger zurück
                total_size += file_size

                if total_size > MAX_TOTAL_SIZE:
                    for file_id in file_ids:
                        mongo_manager.delete_documents(config['MONGO_DB']['MONGO_USER_FILES_COLLECTION'], {'_id': file_id}, use_GridFS=True)
                    Logger.error(f'Total file size exceeds {MAX_TOTAL_SIZE} bytes')
                    return {'error': f'Total file size exceeds {MAX_TOTAL_SIZE} bytes'}, 413

                file_id = mongo_manager.insert_document(
                    config['MONGO_DB']['MONGO_USER_FILES_COLLECTION'],
                    {'file': file, 'filename': file.filename, 'user': user, 'title': title},
                    use_GridFS=True
                )
                file_ids.append(file_id)
                Logger.info(f'File {file.filename} uploaded successfully')

            Logger.info('Files uploaded successfully')
            return {'message': 'Files uploaded successfully'}, 201

        except Exception as e:
            Logger.error(f"Error during upload: {str(e)}")
            return {'error': f"Error during upload: {str(e)}"}, 500

# Resource for file download
class DownloadFile(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('filename', location='headers', type=str, required=True, help="Filename is required")
        parser.add_argument('user', location='headers', type=str, required=True, help="User is required")
        parser.add_argument('title', location='headers', type=str, required=True, help="Title is required")
        args = parser.parse_args()

        filename = args['filename']
        user = args['user']
        title = args['title']

        try:
            files = mongo_manager.find_documents(
                config['MONGO_DB']['MONGO_USER_FILES_COLLECTION'],
                {'filename': filename, 'user': user, 'title': title},
                use_GridFS=True
            )
            if not files:
                Logger.error('File not found')
                return {'error': 'File not found'}, 404

            file = files[0]
            Logger.info(f'File {filename} retrieved successfully')
            return send_file(file, download_name=filename, as_attachment=True)

        except Exception as e:
            Logger.error(f'Error occurred: {str(e)}')
            return {'error': f'Error occurred: {str(e)}'}, 500

# Resource for file deletion
class DeleteFile(Resource):
    def delete(self):
        parser = reqparse.RequestParser()
        parser.add_argument('filename', location='headers', type=str, required=True, help="Filename is required")
        parser.add_argument('user', location='headers', type=str, required=True, help="User is required")
        parser.add_argument('title', location='headers', type=str, required=True, help="Title is required")
        args = parser.parse_args()

        filename = args['filename']
        user = args['user']
        title = args['title']

        try:
            result = mongo_manager.delete_documents(
                config['MONGO_DB']['MONGO_USER_FILES_COLLECTION'],
                {'filename': filename, 'user': user, 'title': title},
                use_GridFS=True
            )
            if result.deleted_count == 0:
                Logger.error('File not found')
                return {'error': 'File not found'}, 404

            Logger.info(f'File {filename} deleted successfully')
            return {'message': 'File deleted successfully'}, 200

        except Exception as e:
            Logger.error(f'Error occurred: {str(e)}')
            return {'error': f'Error occurred: {str(e)}'}, 500
