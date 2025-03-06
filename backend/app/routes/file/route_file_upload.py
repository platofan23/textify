from flask_restful import Resource, reqparse
from werkzeug.datastructures import FileStorage
from backend.app.utils import Logger, MongoDBManager, ConfigManager
from backend.app.utils.util_crypt import CryptoManager

class UploadFile(Resource):
    """
    Resource for uploading files.
    """
    def __init__(self, mongo_manager: MongoDBManager, config_manager: ConfigManager, crypto_manager: CryptoManager):
        """
        Constructor that injects MongoDBManager, ConfigManager, and Crypto_Manager for file uploads.

        Args:
            mongo_manager (MongoDBManager): Instance of MongoDB manager.
            config_manager (ConfigManager): Instance of configuration manager.
            crypto_manager (Crypto_Manager): Instance of crypto manager for encryption.
        """
        self.mongo_manager = mongo_manager
        self.config_manager = config_manager
        self.crypto_manager = crypto_manager

        # Maximum total size (in bytes) allowed for uploaded files.
        self.max_total_size = int(self.config_manager.get_rest_config().get("max_total_size_gb")) * 1024 * 1024 * 1024
        # Allowed file extensions.
        self.allowed_extensions = set(self.config_manager.get_rest_config().get("allowed_extensions"))
        # Collection name for storing user files.
        self.user_files_collection = self.config_manager.get_mongo_config().get("user_files_collection", "user_files")

    def allowed_file(self, filename: str) -> bool:
        """
        Checks if the file extension is allowed.

        Args:
            filename (str): The name of the file.

        Returns:
            bool: True if the file extension is allowed, otherwise False.
        """
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in self.allowed_extensions

    def post(self):
        """
        Handles the POST request for file uploads.

        Expected headers:
            - User: Username of the uploader.
            - Title: A title for the file.
        Expected files:
            - Files: One or more files (multipart/form-data) under the key 'Files'.

        Returns:
            tuple: A JSON response with a success or error message and the corresponding HTTP status code.
        """
        # Parse required headers and file uploads.
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

        # Check if the user exists in the "users" collection.
        user_docs = self.mongo_manager.find_documents("users", {'Username': username})
        if not user_docs:
            Logger.error("User not found")
            return {'error': 'User not found'}, 404
        user = user_docs[0]

        for file in files:
            if file.filename == '':
                Logger.error("No selected file")
                return {'error': 'No selected file'}, 400

            if not self.allowed_file(file.filename):
                Logger.error("Invalid file type")
                return {'error': 'Invalid file type'}, 415

            # Read file content to calculate the total size.
            file_content = file.read()
            total_size += len(file_content)
            file.seek(0)  # Reset file pointer for subsequent operations

            if total_size > self.max_total_size:
                # If the total size limit is exceeded, remove previously inserted documents.
                for file_id in file_ids:
                    self.mongo_manager.delete_documents(self.user_files_collection, {'_id': file_id}, False)
                Logger.error(f"Total file size exceeds allowed limit of {self.max_total_size} bytes")
                return {'error': f'Total file size exceeds allowed limit of {self.max_total_size} bytes'}, 413

            # Encrypt the file using the crypto manager.
            encrypted_file_lib = self.crypto_manager.encrypt_file(user, file)
            size_mb = self.crypto_manager.get_encrypted_file_size_mb(encrypted_file_lib)
            Logger.info(f"Encrypted file size: {size_mb} MB")

            # Insert the encrypted file document into the file collection.
            file_id = self.mongo_manager.insert_document(
                self.user_files_collection,
                {'file_lib': encrypted_file_lib, 'filename': file.filename, 'user': username, 'title': title},
            )
            file_ids.append(file_id)
            Logger.info(f"File '{file.filename}' uploaded successfully")

        Logger.info("Files uploaded successfully")
        return {'message': 'Files uploaded successfully'}, 201
