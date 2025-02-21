import io

from PIL import Image
from flask import send_file
from flask_restful import Resource, reqparse
from werkzeug.datastructures import FileStorage
from backend.app.utils import Logger, MongoDBManager, ConfigManager, Crypt
from backend.app.services import multi_reader

# Load configuration
config_manager = ConfigManager()

MAX_TOTAL_SIZE = int(config_manager.get_rest_config().get("max_total_size_gb")) * 1024 * 1024 * 1024
ALLOWED_EXTENSIONS = set(config_manager.get_rest_config().get("allowed_extensions"))

# MongoDB setup
mongo_manager = MongoDBManager()
crypt = Crypt()

# Helper function to check allowed file types
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Resource for file upload
class UploadFile(Resource):
    def post(self):
        # Validate parameters
        parser = reqparse.RequestParser()
        parser.add_argument('User', location='headers', required=True, help="User header is required")
        parser.add_argument('Title', location='headers', required=True, help="Title header is required")
        parser.add_argument('Files', type=FileStorage, location="files", action='append', required=True)
        args = parser.parse_args()

        files = args['Files']
        username = args['User']
        title = args['Title']

        total_size = 0
        file_ids = []

        # check if user exists
        user_documents = mongo_manager.find_documents(config_manager.get_mongo_config().get("users_collection"),
                                                      {'Username': username})
        if not user_documents:
            Logger.error('User not found ' + username)
            return {'error': 'User not found'}, 404

        user = user_documents[0]

        # Save files to MongoDB
        for file in files:
            if file.filename == '':
                Logger.error('No selected file')
                return {'error': 'No selected file'}, 400
            if allowed_file(file.filename):
                total_size += len(file.read())
                file.seek(0)
                if total_size > MAX_TOTAL_SIZE:

                    # Reverse changes by deleting uploaded files
                    for file_id in file_ids:
                        mongo_manager.delete_documents(config_manager.get_mongo_config().get("user_files_collection"), {'_id': file_id}, use_GridFS=False)
                        mongo_manager.delete_documents(config_manager.get_mongo_config().get("user_text_collection"), {'file_id': file_id.inserted_id}, use_GridFS=False)
                    Logger.error(f'Total file size exceeds {MAX_TOTAL_SIZE} bytes')
                    return {'error': f'Total file size exceeds {MAX_TOTAL_SIZE} bytes'}, 413

                # Encrypt file
                encrypted_file_lib = crypt.encrypt_file(user, file)
                crypt.get_encrypted_file_size_mb(encrypted_file_lib)

                # Perform OCR
                file.seek(0)  # Reset file pointer to the beginning

                text, text_font_size = multi_reader(file.read(), "doctr", language="en")
                Logger.debug(f'Text: {text}; Font size: {text_font_size}')

                # Save file to MongoDB
                file_id = mongo_manager.insert_document(config_manager.get_mongo_config().get("user_files_collection"), {'file_lib': encrypted_file_lib, 'filename': file.filename, 'user': username, 'title': title}, use_GridFS=False)
                mongo_manager.insert_document(config_manager.get_mongo_config().get("user_text_collection"),
                                              {'text': text, 'user': username, 'title': title, 'file_id': file_id.inserted_id},
                                              use_GridFS=False)
                file_ids.append(file_id)
                Logger.info(f'File {file.filename} uploaded successfully')
            else:
                Logger.error('Invalid file type')
                return {'error': 'Invalid file type'}, 415

        Logger.info('Files uploaded successfully')
        return {'message': 'Files uploaded successfully'}, 201




# Resource for file download
class DownloadFile(Resource):
    def get(self):
        # Validate parameters
        parser = reqparse.RequestParser()
        parser.add_argument('filename', location='headers', type=str, required=True, help="Filename is required")
        parser.add_argument('user', location='headers', type=str, required=True, help="User is required")
        parser.add_argument('title', location='headers', type=str, required=True, help="Title is required")
        args = parser.parse_args()

        filename = args['filename']
        user = args['user']
        title = args['title']

        try:
            # Retrieve file from MongoDB
            files = mongo_manager.find_documents(config_manager.get_mongo_config().get("user_files_collection"), {'filename': filename, 'user': user, 'title': title}, use_GridFS=False)
            if not files:
                Logger.error('File not found')
                return {'error': 'File not found'}, 404

            file = files[0]
            Logger.info(f'File {filename} retrieved successfully')
            file_path = crypt.decrypt_png(user, file['file_lib'], file_name=filename)

            Logger.debug(f'\\decrypted_files\\decrypted_{filename}')

            return send_file(file_path, as_attachment=True)
        except Exception as e:
            Logger.error(f'Error occurred: {str(e)}')
            return {'error': f'Error occurred: {str(e)}'}, 500


# Resource for file deletion
class DeleteFile(Resource):
    def delete(self):
        # Validate parameters
        parser = reqparse.RequestParser()
        parser.add_argument('filename', location='headers', type=str, required=True, help="Filename is required")
        parser.add_argument('user', location='headers', type=str, required=True, help="User is required")
        parser.add_argument('title', location='headers', type=str, required=True, help="Title is required")
        args = parser.parse_args()

        filename = args['filename']
        user = args['user']
        title = args['title']

        try:
            # Delete file from MongoDB
            result = mongo_manager.delete_documents(config_manager.get_mongo_config().get("user_files_collection"), {'filename': filename, 'user': user, 'title': title}, use_GridFS=True)
            if result.deleted_count == 0:
                Logger.error('File not found')
                return {'error': 'File not found'}, 404

            Logger.info(f'File {filename} deleted successfully')
            return {'message': 'File deleted successfully'}, 200
        except Exception as e:
            Logger.error(f'Error occurred: {str(e)}')
            return {'error': f'Error occurred: {str(e)}'}, 500


class GetBookInfo(Resource):
    def get(self):
        """
        Retrieves book information for a user.
        Returns:
            list: A list of books and their page counts.
        """

        # Validate parameters
        parser = reqparse.RequestParser()
        parser.add_argument('user', location='headers', type=str, required=True, help="User is required")
        args = parser.parse_args()

        user = args['user']

        try:
            # Retrieve books from MongoDB
            Logger.info(f'Retrieving books for user {user}')
            books = mongo_manager.aggregate_documents(config_manager.get_mongo_config().get("user_files_collection"),
                                                      [
                                                          {
                                                              "$match": {"user": user}
                                                          },
                                                          {
                                                              "$group": {
                                                                  "_id": "$title",
                                                                  "count": {"$sum": 1}
                                                              }
                                                          },
                                                          {
                                                              "$sort": {"_id": 1}
                                                          }
                                                      ])

            Logger.info(f'Books retrieved successfully')
            Logger.debug(f'Files: {books}')

            return books
        except Exception as e:
            Logger.error(f'Error occurred: {str(e)}')
            return {'error': f'Error occurred: {str(e)}'}, 500