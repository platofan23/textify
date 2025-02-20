import os
from itertools import count

from pymongo import MongoClient, errors
from backend.app.utils.util_config_manager import ConfigManager
from backend.app.utils import Logger
import gridfs

class MongoDBManager:
    """
    A singleton class to manage MongoDB operations.

    Provides basic methods for interacting with a MongoDB database, such as inserting,
    finding, and deleting documents.

    Attributes:
        client (MongoClient): The MongoDB client instance.
        db (Database): The MongoDB database instance.
        connection_string (str): The connection string for the MongoDB client.
        database_name (str): The name of the MongoDB database.
        config_manager (ConfigManager): The configuration manager instance.
    """
    _instance = None

    def __new__(cls):
        """
        Ensures a single instance of MongoDBManager is created.
        """
        if cls._instance is None:
            cls._instance = super(MongoDBManager ,cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """
        Initializes the MongoDB connection.

        """
        self.config_manager = ConfigManager()

        # Retrieve MongoDB connection details
        self.connection_string = self.config_manager.get_config_value(
            "MONGO_DB", "CONNECTION_STRING", str
        )
        self.database_name = self.config_manager.get_config_value(
            "MONGO_DB", "MONGO_DATABASE", str
        )

        if not self.database_name:
            Logger.error("Database name is not set in the configuration.")
            raise ValueError("Database name is not set in the configuration.")

        try:
            self.client = MongoClient(self.connection_string, serverSelectionTimeoutMS=5000)
            self.db = self.client[self.database_name]
            self.client.admin.command("ping")  # Test connection
            Logger.info(f"Connected to MongoDB database '{self.database_name}' successfully.")
        except errors.ServerSelectionTimeoutError as e:
            Logger.error(f"Could not connect to MongoDB: {e}")
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
            Logger.warning(f"Attempt to access non-existent collection '{collection_name}'.")
            raise ValueError(f"Collection '{collection_name}' does not exist in the database.")
        Logger.info(f"Retrieved collection '{collection_name}'.")
        return self.db[collection_name]

    def insert_document(self, collection_name: str, document: dict, use_GridFS: bool = False):
        """
        Inserts a document into a MongoDB collection.

        Args:
            collection_name (str): The name of the collection.
            document (dict): The document to insert.
            use_GridFS (bool): Whether to use GridFS for large files.

        Returns:
            InsertOneResult: The result of the insert operation.
        """
        collection = self.get_collection(collection_name)

        if use_GridFS:
            fs = gridfs.GridFS(self.db, collection=collection_name)
            file = document.pop("file")
            file_id = fs.put(file, **document)
            Logger.info(
                f"Inserted file into GridFS collection '{collection_name}' with ID: {file_id}."
            )
            return file_id

        result = collection.insert_one(document)
        Logger.info(
            f"Inserted document into collection '{collection_name}' with ID: {result.inserted_id}."
        )
        return result

    def find_documents(self, collection_name: str, query: dict, use_GridFS: bool = False):
        """
        Finds documents in a MongoDB collection.

        Args:
            collection_name (str): The name of the collection.
            query (dict): The query to filter documents.
            use_GridFS (bool): Whether to use GridFS for large files.

        Returns:
            list: A list of documents that match the query.
        """
        collection = self.get_collection(collection_name)
        documents = list(collection.find(query))

        if use_GridFS:
            fs = gridfs.GridFS(self.db, collection=collection_name)
            documents = []
            for file in fs.find(query):
                documents.append(file)
            Logger.info(
                f"Found {len(documents)} files in GridFS collection '{collection_name}' matching query: {query}."
            )
            return documents

        Logger.info(
            f"Found {len(documents)} documents in collection '{collection_name}' matching query: {query}."
        )
        return documents

    def delete_documents(self, collection_name: str, query: dict, use_GridFS: bool = False):
        """
        Deletes documents from a MongoDB collection.

        Args:
            collection_name (str): The name of the collection.
            query (dict): The query to match documents to delete.
            use_GridFS (bool): Whether to use GridFS for large files.

        Returns:
            DeleteResult: The result of the delete operation.
        """
        collection = self.get_collection(collection_name)

        if use_GridFS:
            fs = gridfs.GridFS(self.db, collection=collection_name)
            files = fs.find(query)
            for file in files:
                fs.delete(file._id)
            Logger.info(
                f"Deleted {len(list(files))} files from GridFS collection '{collection_name}' matching query: {query}."
            )
            return

        result = collection.delete_many(query)
        Logger.info(
            f"Deleted {result.deleted_count} documents from collection '{collection_name}' matching query: {query}."
        )
        return result

    def aggregate_documents(self, collection_name: str, pipeline: list):
        """
        Aggregates documents in a MongoDB collection.

        Args:
            collection_name (str): The name of the collection.
            pipeline (list): The aggregation pipeline.

        Returns:
            list: A list of documents resulting from the aggregation.
        """
        collection = self.get_collection(collection_name)
        result = list(collection.aggregate(pipeline))
        Logger.info(
            f"Aggregated documents in collection '{collection_name}' with pipeline: {pipeline}."
        )

        return result
