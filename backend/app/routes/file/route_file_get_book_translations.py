import json

from flask_restful import Resource, reqparse
from backend.app.utils import Logger, MongoDBManager, ConfigManager


class GetBookTranslations(Resource):
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
            books = self.mongo_manager.find_documents(self.user_text_collection,
                                                      {'user': user, 'title': title, 'page': 1})

            if not books:
                Logger.info(f'No books found for user {user} with title {title}')
                return {'error': 'No books found'}, 404

            if 'translations' not in books[0]:
                Logger.info(f'No translations found for book {title}')
                return {'error': 'No translations found'}, 404

            translations = books[0]['translations']

            # Handle the translations field based on its type
            if isinstance(translations, str):
                try:
                    return_books = json.loads(translations)
                except json.JSONDecodeError:
                    Logger.error(f'Invalid JSON in translations field')
                    return {'error': 'Invalid translations data'}, 500
            else:
                # If it's already a dict/list, use it directly
                return_books = translations

            Logger.info(f'Book translations retrieved successfully')

            Logger.debug(f'Translations: {return_books.keys()}')

            # Return keys as a JSON-serializable dictionary
            return {'languages': list(return_books.keys())}, 200
        except Exception as e:
            Logger.error(f'Error occurred: {str(e)}')
            return {'error': f'Error occurred: {str(e)}'}, 500