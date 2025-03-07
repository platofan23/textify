from flask_restful import Resource, reqparse
from backend.app.utils import Logger, MongoDBManager, ConfigManager


class GetBookInfo(Resource):
    def __init__(self, mongo_manager: MongoDBManager, config_manager: ConfigManager):
        """
        Constructor that injects MongoDBManager and ConfigManager for retrieving book information.

        Args:
            mongo_manager (MongoDBManager): Instance of MongoDB manager.
            config_manager (ConfigManager): Instance of configuration manager.
        """
        self.mongo_manager = mongo_manager
        self.config_manager = config_manager
        # Get the collection name for user files from configuration, defaulting to "user_files"
        self.user_files_collection = self.config_manager.get_mongo_config().get("user_files_collection", "user_files")

    def get(self):
        """
        Retrieves book information for a user by aggregating document data from MongoDB.

        Returns:
            list or tuple: A list of books with their page counts if successful; otherwise, an error message with HTTP status 500.
        """
        # Validate request parameters
        parser = reqparse.RequestParser()
        parser.add_argument('user', location='headers', type=str, required=True, help="User header is required")
        args = parser.parse_args()

        user = args['user']

        try:
            # Log retrieval attempt
            Logger.info(f"Retrieving books for user: {user}")

            # Perform aggregation query on the specified collection to retrieve book information
            books = self.mongo_manager.aggregate_documents(
                self.config_manager.get_mongo_config().get("user_files_collection"),
                [
                    {"$match": {"user": user}},
                    {"$group": {"_id": "$title", "count": {"$sum": 1}}},
                    {"$sort": {"_id": 1}}
                ]
            )

            Logger.info("Books retrieved successfully")
            Logger.info(f"Retrieved books: {books}")

            return books
        except Exception as e:
            Logger.error(f"Error occurred while retrieving books: {str(e)}")
            # Return error message and HTTP 500 error code
            return {'error': f"Error occurred: {str(e)}"}, 500
