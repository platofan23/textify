from pymongo import MongoClient, errors
from backend.app.utils.util_config_manager import ConfigManager
from backend.app.utils.util_logger import Logger


class MongoDBManager:
    """
    A singleton class to manage MongoDB operations.

    Provides basic methods for interacting with a MongoDB database, such as inserting,
    finding, and deleting documents.

    Attributes:
        client (MongoClient): The MongoDB client instance.
        db (Database): The MongoDB database instance.
    """
    _instance = None

    def __new__(cls, config_manager: ConfigManager):
        """
        Ensures a single instance of MongoDBManager is created.
        """
        if cls._instance is None:
            cls._instance = super(MongoDBManager, cls).__new__(cls)
            cls._instance._initialize(config_manager)
        return cls._instance

    def _initialize(self, config_manager: ConfigManager):
        """
        Initializes the MongoDB connection.

        Args:
            config_manager (ConfigManager): The configuration manager for fetching MongoDB settings.
        """
        self.config_manager = config_manager

        # Retrieve MongoDB connection details
        self.connection_string = self.config_manager.get_config_value(
            "MONGO_DB", "CONNECTION_STRING", str
        )
        self.database_name = self.config_manager.get_config_value(
            "MONGO_DB", "MONGO_DATABASE", str
        )

        if not self.database_name:
            raise ValueError("Database name is not set in the configuration.")

        try:
            self.client = MongoClient(self.connection_string, serverSelectionTimeoutMS=5000)
            self.db = self.client[self.database_name]
            self.client.admin.command("ping")  # Test connection
            Logger().message("Connected to MongoDB successfully.")
        except errors.ServerSelectionTimeoutError as e:
            Logger().error(f"Could not connect to MongoDB: {e}")
            raise

    def get_collection(self, collection_name: str):
        """
        Retrieves a MongoDB collection.

        Args:
            collection_name (str): The name of the collection to retrieve.

        Returns:
            Collection: The MongoDB collection instance.

        Raises:
            ValueError: If the collection does not exist.
        """
        if collection_name not in self.db.list_collection_names():
            Logger().warning(f"Collection '{collection_name}' does not exist in the database.")
            raise ValueError(f"Collection '{collection_name}' does not exist in the database.")
        return self.db[collection_name]

    def insert_document(self, collection_name: str, document: dict):
        """
        Inserts a document into a MongoDB collection.

        Args:
            collection_name (str): The name of the collection.
            document (dict): The document to insert.

        Returns:
            InsertOneResult: The result of the insert operation.
        """
        collection = self.get_collection(collection_name)
        result = collection.insert_one(document)
        Logger().message(f"Document inserted with ID: {result.inserted_id}")
        return result

    def find_documents(self, collection_name: str, query: dict):
        """
        Finds documents in a MongoDB collection.

        Args:
            collection_name (str): The name of the collection.
            query (dict): The query to filter documents.

        Returns:
            list: A list of documents that match the query.
        """
        collection = self.get_collection(collection_name)
        documents = list(collection.find(query))
        Logger().message(f"Found {len(documents)} documents in collection '{collection_name}'.")
        return documents

    def delete_documents(self, collection_name: str, query: dict):
        """
        Deletes documents from a MongoDB collection.

        Args:
            collection_name (str): The name of the collection.
            query (dict): The query to match documents to delete.

        Returns:
            DeleteResult: The result of the delete operation.
        """
        collection = self.get_collection(collection_name)
        result = collection.delete_many(query)
        Logger().message(f"Deleted {result.deleted_count} documents from collection '{collection_name}'.")
        return result
