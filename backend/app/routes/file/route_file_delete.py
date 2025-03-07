from flask_restful import Resource, reqparse
from backend.app.utils import Logger, MongoDBManager, ConfigManager
from gridfs import GridFS


class DeleteFile(Resource):
    """
    Resource for deleting a file.
    """

    def __init__(self, mongo_manager: MongoDBManager, config_manager: ConfigManager):
        """
        Constructor that injects MongoDBManager and ConfigManager for file deletion.

        Args:
            mongo_manager (MongoDBManager): Instance of MongoDB manager.
            config_manager (ConfigManager): Instance of configuration manager.
        """
        self.mongo_manager = mongo_manager
        self.config_manager = config_manager
        # Retrieve the collection name for user files from configuration, defaulting to "user_files"
        self.user_files_collection = self.config_manager.get_mongo_config().get("user_files_collection", "user_files")

    def delete(self):
        """
        Handles DELETE requests to remove a file.

        Expected headers:
            - filename (optional): The filename of the file to be deleted.
            - page (optional): The page number associated with the file to be deleted (as an integer).
            - user: The username of the file owner.
            - title: The title associated with the file.

        Behavior:
            - If 'filename' is provided, deletion is attempted using 'filename' and 'user' only.
            - Otherwise, deletion is attempted using 'title', 'user', and 'page'.

        Returns:
            tuple: A dictionary with a success or error message and the corresponding HTTP status code.
        """
        # Parse header parameters
        parser = reqparse.RequestParser()
        parser.add_argument('filename', location='headers', type=str, required=False, help="Filename if provided")
        parser.add_argument('page', location='headers', type=int, required=False,
                            help="Page if provided must be an integer")
        parser.add_argument('user', location='headers', type=str, required=True, help="User is required")
        parser.add_argument('title', location='headers', type=str, required=False, help="Title is required")
        args = parser.parse_args()

        filename = args.get('filename')
        page = args.get('page')
        username = args['user']
        title = args['title']

        # Determine query based on provided identifier(s)
        if filename:
            # If filename is provided, use only filename and user.
            query = {'filename': filename, 'user': username}
        else:
            # Otherwise, title and page must be provided.
            if page is None:
                Logger.error("Either filename or page must be provided.")
                return {'error': 'Either filename or page must be provided.'}, 400
            query = {'title': title, 'user': username, 'page': page}

        try:
            # Check if the file exists in the user_files collection
            collection = self.mongo_manager.get_collection(self.user_files_collection)
            file_doc = collection.find_one(query)

            # Check if the file exists in tts_files via GridFS
            tts_fs = GridFS(self.mongo_manager.db, collection="tts_files")
            tts_file_doc = tts_fs.find_one(query)

            # If neither file exists, return a 404 error
            if not file_doc and not tts_file_doc:
                Logger.error(f"File with identifiers {query} not found in both user_files and GridFS tts_files.")
                return {'error': 'File not found'}, 404

            # Delete from user_files collection if exists
            if file_doc:
                self.mongo_manager.delete_documents(
                    self.user_files_collection,
                    query,
                    False
                )
                Logger.info(f"File with identifiers {query} deleted from collection '{self.user_files_collection}'.")

            # Delete from GridFS (tts_files) if exists
            if tts_file_doc:
                self.mongo_manager.delete_documents(
                    "tts_files",
                    query,
                    True
                )
                Logger.info(f"File with identifiers {query} deleted from GridFS collection 'tts_files'.")

            return {'message': 'File deleted successfully'}, 200

        except Exception as e:
            Logger.error(f"Error deleting file with identifiers {query}: {str(e)}")
            return {'error': f"Error occurred: {str(e)}"}, 500
