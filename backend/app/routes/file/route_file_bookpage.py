from flask_restful import Resource, reqparse
from backend.app.utils import Logger, MongoDBManager, ConfigManager, CryptoManager

class GetBookPage(Resource):
    def __init__(self, config_manager: ConfigManager, mongo_manager: MongoDBManager, crypto_manager: CryptoManager):
        """
        Constructor that injects MongoDBManager and ConfigManager for file deletion.

        Args:
            mongo_manager (MongoDBManager): The MongoDB manager instance.
            config_manager (ConfigManager): The configuration manager instance.
        """
        self.mongo_manager = mongo_manager
        self.config_manager = config_manager
        self.user_text_collection = self.config_manager.get_mongo_config().get("user_text_collection", "user_texts")
        self.crypto_manager = crypto_manager

    def get(self):
        """
        Retrieves book information for a user.
        Returns:
            list: A list of books and their page counts.
        """

        # Validate parameters
        parser = reqparse.RequestParser()
        parser.add_argument('user', location='headers', type=str, required=True, help="User is required")
        parser.add_argument('title', location='headers', type=str, required=True, help="Title is required")
        parser.add_argument('page', location='headers', type=int, required=True, help="Page is required")
        parser.add_argument('lang', location='headers', type=str, required=False, default='source', help="Language is required")
        args = parser.parse_args()


        user = args['user']
        title = args['title']
        page = args['page']
        lang = args['lang']

        try:
            # Retrieve books from MongoDB
            Logger.info(f'Retrieving books for user {user}')
            books = self.mongo_manager.find_documents(self.user_text_collection, {'user': user, 'title': title, 'page': page}, use_GridFS=False)
            Logger.info(f'Book page retrieved successfully')

            # Decrypt text
            text = self.crypto_manager.decrypt_file(user, books[0]['text'][lang])

            Logger.debug(f'text : {text}')

            return json.loads(text), 200
        except Exception as e:
            Logger.error(f'Error occurred: {str(e)}')
            return {'error': f'Error occurred: {str(e)}'}, 500