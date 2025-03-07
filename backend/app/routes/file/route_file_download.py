import io
from flask import send_file
from flask_restful import Resource, reqparse
from backend.app.utils import Logger, MongoDBManager, ConfigManager
from backend.app.utils.util_crypt import CryptoManager

class DownloadFile(Resource):
    """
    Resource for downloading a file.
    """
    def __init__(self, mongo_manager: MongoDBManager, config_manager: ConfigManager, crypto_manager: CryptoManager):
        """
        Constructor that injects MongoDBManager, ConfigManager, and Crypto_Manager for file downloads.

        Args:
            mongo_manager (MongoDBManager): Instance of MongoDB manager.
            config_manager (ConfigManager): Instance of configuration manager.
            crypto_manager (Crypto_Manager): Instance of crypto manager for decryption.
        """
        self.mongo_manager = mongo_manager
        self.config_manager = config_manager
        self.crypto_manager = crypto_manager
        # Retrieve the collection name for user files from configuration, defaulting to "user_files"
        self.user_files_collection = self.config_manager.get_mongo_config().get("user_files_collection", "user_files")

    def get(self):
        """
        Handles the GET request for file download.

        Expected headers:
            - filename: Name of the file to download.
            - user: Username of the file owner.
            - title: Title associated with the file.

        Returns:
            Response: The file as a downloadable attachment or an error message with the corresponding HTTP status code.
        """
        # Parse required header parameters.
        parser = reqparse.RequestParser()
        parser.add_argument('filename', location='headers', type=str, required=True, help="Filename is required")
        parser.add_argument('user', location='headers', type=str, required=True, help="User is required")
        parser.add_argument('title', location='headers', type=str, required=True, help="Title is required")
        args = parser.parse_args()

        filename = args['filename']
        username = args['user']
        title = args['title']

        try:
            # Search for the file document in the user files collection.
            files = self.mongo_manager.find_documents(
                self.user_files_collection,
                {'filename': filename, 'user': username, 'title': title}
            )
            if not files:
                Logger.error(f"File '{filename}' for user '{username}' with title '{title}' not found.")
                return {'error': 'File not found'}, 404

            file_entry = files[0]
            Logger.info(f"File '{filename}' retrieved successfully for user '{username}'.")

            # Decrypt the file using the crypto manager.
            plain_data = self.crypto_manager.decrypt_file(username, file_entry["file_lib"])

            # Create an in-memory file-like object for the decrypted file.
            file_like = io.BytesIO(plain_data)
            file_like.seek(0)
            return send_file(file_like, download_name=filename, as_attachment=True)
        except Exception as e:
            Logger.error(f"Error occurred while downloading file '{filename}' for user '{username}': {str(e)}")
            return {'error': f"Error occurred: {str(e)}"}, 500
