import json

from flask_restful import Resource, reqparse
from backend.app.utils import Logger, MongoDBManager, ConfigManager


class DeleteBook(Resource):
    def __init__(self, config_manager: ConfigManager, mongo_manager: MongoDBManager):
        """
        Constructor that injects MongoDBManager and ConfigManager for file deletion.

        Args:
            mongo_manager (MongoDBManager): The MongoDB manager instance.
            config_manager (ConfigManager): The configuration manager instance.
        """
        self.mongo_manager = mongo_manager
        self.config_manager = config_manager
        self.user_text_collection = self.config_manager.get_mongo_config().get("user_text_collection", "user_texts")

    def delete(self):
        """
        Handles DELETE requests to remove a book.
        """

        # Validate parameters
        parser = reqparse.RequestParser()
        parser.add_argument('user', location='headers', type=str, required=True, help="User is required")
        parser.add_argument('title', location='headers', type=str, required=True, help="Title is required")
        args = parser.parse_args()

        user = args['user']
        title = args['title']

        try:
            # Retrieve books from MongoDB
            Logger.info(f'Retrieving books for user {user}')
            book = self.mongo_manager.find_documents(self.user_text_collection,
                                                      {'user': user, 'title': title})

            if not book:
                Logger.info(f'No books found for user {user} with title {title}')
                return {'error': 'No books found'}, 404

            # Delete the book
            self.mongo_manager.delete_documents(self.user_text_collection, {'user': user, 'title': title})
            Logger.info(f'Book deleted successfully')

            return {'message': 'Book deleted successfully'}, 200
        except Exception as e:
            Logger.error(f'Error occurred: {str(e)}')
            return {'error': f'Error occurred: {str(e)}'}, 500
