import io
from flask import send_file, make_response
from flask_restful import Resource, reqparse
from werkzeug.datastructures import FileStorage

from backend.app.utils import Logger, MongoDBManager, ConfigManager
from backend.app.utils.util_crypt import Crypto_Manager


class UploadFile(Resource):
    def __init__(self, mongo_manager: MongoDBManager, config_manager: ConfigManager, crypto_manager: Crypto_Manager):
        """
        Constructor that injects MongoDBManager, ConfigManager, and Crypto_Manager for file uploads.

        Args:
            mongo_manager (MongoDBManager): The MongoDB manager instance.
            config_manager (ConfigManager): The configuration manager instance.
            crypto_manager (Crypto_Manager): The crypto manager instance for encryption.
        """
        self.mongo_manager = mongo_manager
        self.config_manager = config_manager
        self.crypto_manager = crypto_manager

        self.max_total_size = int(self.config_manager.get_rest_config().get("max_total_size_gb")) * 1024 * 1024 * 1024
        self.allowed_extensions = set(self.config_manager.get_rest_config().get("allowed_extensions"))
        self.user_files_collection = self.config_manager.get_mongo_config().get("user_files_collection", "user_files")

    def allowed_file(self, filename: str) -> bool:
        """
        Checks if the file extension is allowed.

        Args:
            filename (str): The file name.

        Returns:
            bool: True if allowed, otherwise False.
        """
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in self.allowed_extensions

    def post(self):
        """
        Handles the POST request for file uploads.
        Expects headers:
            - User: Username of the uploader.
            - Title: A title for the file.
        Expects one or more files (multipart/form-data) under the key 'File'.
        """
        parser = reqparse.RequestParser()
        parser.add_argument('User', location='headers', required=True, help="User header is required")
        parser.add_argument('Title', location='headers', required=True, help="Title header is required")
        parser.add_argument('File', type=FileStorage, location="files", action='append', required=True)
        args = parser.parse_args()

        files = args['File']
        username = args['User']
        title = args['Title']

        total_size = 0
        file_ids = []

        # Check if the user exists in the "users" collection.
        user_docs = self.mongo_manager.find_documents("users", {'Username': username})
        if not user_docs:
            Logger.error('User not found')
            return {'error': 'User not found'}, 404
        user = user_docs[0]

        for file in files:
            if file.filename == '':
                Logger.error('No selected file')
                return {'error': 'No selected file'}, 400

            if not self.allowed_file(file.filename):
                Logger.error('Invalid file type')
                return {'error': 'Invalid file type'}, 415

            # Calculate total size of uploaded files.
            file_content = file.read()
            total_size += len(file_content)
            file.seek(0)
            if total_size > self.max_total_size:
                # If total size is exceeded, delete previously uploaded files.
                for file_id in file_ids:
                    self.mongo_manager.delete_documents(self.user_files_collection, {'_id': file_id}, use_GridFS=False)
                Logger.error(f'Total file size exceeds {self.max_total_size} bytes')
                return {'error': f'Total file size exceeds {self.max_total_size} bytes'}, 413

            # Encrypt the file using the injected crypto_manager.
            encrypted_file_lib = self.crypto_manager.encrypt_file(user, file)
            size_mb = self.crypto_manager.get_encrypted_file_size_mb(encrypted_file_lib)
            Logger.info(f'Encrypted file size: {size_mb} MB')

            # Insert the encrypted file document into the file collection.
            file_id = self.mongo_manager.insert_document(
                self.user_files_collection,
                {'file_lib': encrypted_file_lib, 'filename': file.filename, 'user': username, 'title': title},
                use_GridFS=False
            )
            file_ids.append(file_id)
            Logger.info(f'File {file.filename} uploaded successfully')

        Logger.info('Files uploaded successfully')
        return {'message': 'Files uploaded successfully'}, 201


class DownloadFile(Resource):
    def __init__(self, mongo_manager: MongoDBManager, config_manager: ConfigManager, crypto_manager: Crypto_Manager):
        """
        Constructor that injects MongoDBManager, ConfigManager, and Crypto_Manager for file downloads.

        Args:
            mongo_manager (MongoDBManager): The MongoDB manager instance.
            config_manager (ConfigManager): The configuration manager instance.
            crypto_manager (Crypto_Manager): The crypto manager instance for decryption.
        """
        self.mongo_manager = mongo_manager
        self.config_manager = config_manager
        self.crypto_manager = crypto_manager
        self.user_files_collection = self.config_manager.get_mongo_config().get("user_files_collection", "user_files")

    def get(self):
        """
        Handles the GET request for file download.
        Expects headers:
            - filename: Name of the file to download.
            - user: Username of the file owner.
            - title: Title associated with the file.
        """
        parser = reqparse.RequestParser()
        parser.add_argument('filename', location='headers', type=str, required=True, help="Filename is required")
        parser.add_argument('user', location='headers', type=str, required=True, help="User is required")
        parser.add_argument('title', location='headers', type=str, required=True, help="Title is required")
        args = parser.parse_args()

        filename = args['filename']
        username = args['user']
        title = args['title']

        try:
            # Search for the file document in the file collection.
            files = self.mongo_manager.find_documents(
                self.user_files_collection,
                {'filename': filename, 'user': username, 'title': title},
                use_GridFS=False
            )
            if not files:
                Logger.error('File not found')
                return {'error': 'File not found'}, 404

            file_entry = files[0]
            Logger.info(f'File {filename} retrieved successfully')

            # Decrypt the file using the injected crypto_manager.
            plain_data = self.crypto_manager.decrypt_file(username, file_entry["file_lib"], filename)

            # Use BytesIO to hold the decrypted file in memory.
            file_like = io.BytesIO(plain_data)
            file_like.seek(0)
            return send_file(file_like, download_name=filename, as_attachment=True)
        except Exception as e:
            Logger.error(f'Error occurred: {str(e)}')
            return {'error': f'Error occurred: {str(e)}'}, 500


class DeleteFile(Resource):
    def __init__(self, mongo_manager: MongoDBManager, config_manager: ConfigManager):
        """
        Constructor that injects MongoDBManager and ConfigManager for file deletion.

        Args:
            mongo_manager (MongoDBManager): The MongoDB manager instance.
            config_manager (ConfigManager): The configuration manager instance.
        """
        self.mongo_manager = mongo_manager
        self.config_manager = config_manager
        self.user_files_collection = self.config_manager.get_mongo_config().get("user_files_collection", "user_files")

    def delete(self):
        """
        Handles the DELETE request to remove a file.
        Expects headers:
            - filename: Name of the file to delete.
            - user: Username of the file owner.
            - title: Title associated with the file.
        """
        parser = reqparse.RequestParser()
        parser.add_argument('filename', location='headers', type=str, required=True, help="Filename is required")
        parser.add_argument('user', location='headers', type=str, required=True, help="User is required")
        parser.add_argument('title', location='headers', type=str, required=True, help="Title is required")
        args = parser.parse_args()

        filename = args['filename']
        username = args['user']
        title = args['title']

        try:
            # Delete the file document from the file collection using GridFS.
            self.mongo_manager.delete_documents(
                self.user_files_collection,
                {'filename': filename, 'user': username, 'title': title},
                use_GridFS=True
            )
            Logger.info(f'File {filename} deleted successfully')
            return {'message': 'File deleted successfully'}, 200
        except Exception as e:
            Logger.error(f'Error occurred: {str(e)}')
            return {'error': f'Error occurred: {str(e)}'}, 500
