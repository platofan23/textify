import json

from flask_restful import Resource, reqparse
from backend.app.utils import Logger, MongoDBManager, ConfigManager


class GetBookLanguage(Resource):
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

    def get(self):
        """
        Retrieves book information for a user.
        Returns:
            list: A list of books and their translations.
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
                                                      {'user': user, 'title': title, 'page': 1})

            return book[0]['text']["language"], 200
        except Exception as e:
            Logger.error(f'Error occurred: {str(e)}')
            return {'error': f'Error occurred: {str(e)}'}, 500