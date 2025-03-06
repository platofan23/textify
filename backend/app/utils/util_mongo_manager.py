import io
import json
import gridfs
from pymongo import MongoClient, errors
from typing import Any, Dict, List, Union
from backend.app.utils.util_config_manager import ConfigManager
from backend.app.utils import Logger
from backend.app.utils.util_crypt import Crypto_Manager

class MongoDBManager:
    """
    Singleton class for managing MongoDB operations with GridFS support.
    Handles CRUD operations, TTS file storage, and translation retrieval.
    """
    _instance = None

    def __new__(cls) -> "MongoDBManager":
        if cls._instance is None:
            cls._instance = super(MongoDBManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self) -> None:
        """
        Initializes the MongoDB connection and GridFS storage.
        """
        self.config_manager = ConfigManager()
        self.connection_string: str = self.config_manager.get_config_value("MONGO_DB", "CONNECTION_STRING", str)
        self.database_name: str = self.config_manager.get_config_value("MONGO_DB", "MONGO_DATABASE", str)

        if not self.database_name:
            Logger.error("Database name is not set in the configuration.")
            raise ValueError("Database name is not set in the configuration.")

        Logger.info(f"Connecting to MongoDB database: {self.database_name}")

        try:
            self.client = MongoClient(self.connection_string, serverSelectionTimeoutMS=5000)
            self.db = self.client[self.database_name]
            # Initialize GridFS for TTS audio files (using a separate collection)
            self.fs = gridfs.GridFS(self.db, collection="tts_files")
            self.client.admin.command("ping")
            Logger.info(f"Successfully connected to MongoDB database '{self.database_name}'.")
        except errors.ServerSelectionTimeoutError as e:
            Logger.error(f"Connection to MongoDB failed: {e}")
            raise

    def check_health(self) -> Dict[str, str]:
        """
        Checks the health of the MongoDB database.

        Returns:
            dict: A dictionary with the database status (e.g., {"database": "healthy"} or {"database": "error"}).
        """
        try:
            self.db.command("ping")
            return {"database": "healthy"}
        except Exception as e:
            Logger.error(f"Database ping failed: {str(e)}")
            return {"database": "error"}

    # ------------------------ General CRUD Operations ------------------------

    def get_collection(self, collection_name: str):
        """
        Retrieves a MongoDB collection. If the collection does not exist, it logs a message indicating
        that the collection will be created on the first insert.

        Args:
            collection_name (str): The name of the collection.

        Returns:
            Collection: The MongoDB collection object.
        """
        collections = self.db.list_collection_names()
        if collection_name not in collections:
            Logger.info(f"Collection '{collection_name}' does not exist. It will be created on first insert.")
        return self.db[collection_name]

    def insert_document(self, collection_name: str, document: Dict[str, Any]) -> Any:
        """
        Inserts a document into a specified collection.

        Args:
            collection_name (str): The collection name.
            document (Dict[str, Any]): The document to insert.

        Returns:
            The inserted document's ID.
        """
        collection = self.get_collection(collection_name)
        result = collection.insert_one(document)
        Logger.info(f"Document inserted into '{collection_name}' with ID: {result.inserted_id}.")
        return result.inserted_id

    def find_documents(self, collection_name: str, query: Dict[str, Any]) -> List[Any]:
        """
        Finds documents in a specified collection based on a query.

        Args:
            collection_name (str): The collection name.
            query (Dict[str, Any]): The query to use.

        Returns:
            list: A list of matching documents.
        """
        collection = self.get_collection(collection_name)
        documents = list(collection.find(query))
        Logger.info(f"Found {len(documents)} document(s) in '{collection_name}'.")
        return documents

    def update_document(
            self,
            collection_name: str,
            query: Dict[str, Any],
            update: Dict[str, Any],
            upsert: bool = False
    ) -> Any:
        """
        Updates a document in a specified collection.

        Args:
            collection_name (str): The collection name.
            query (Dict[str, Any]): The query to match documents.
            update (Dict[str, Any]): The update operation to perform.
            upsert (bool, optional): Whether to insert a new document if no match is found. Defaults to False.

        Returns:
            The result of the update operation.
        """
        collection = self.get_collection(collection_name)
        result = collection.update_one(query, update, upsert=upsert)
        Logger.info(
            f"Updated document(s) in '{collection_name}'. Matched: {result.matched_count}, Modified: {result.modified_count}."
        )
        return result

    def delete_documents(self, collection_name: str, query: Dict[str, Any], use_gridfs: bool = False) -> None:
        """
        Deletes documents from the specified collection or files from GridFS if required.

        Args:
            collection_name (str): The collection name.
            query (Dict[str, Any]): The query to match documents.
            use_gridfs (bool, optional): If True, perform deletion via GridFS. Defaults to False.
        """
        if use_gridfs:
            fs = gridfs.GridFS(self.db, collection=collection_name)
            deleted_count = 0
            for file in fs.find(query):
                fs.delete(file._id)
                deleted_count += 1
            Logger.info(f"Deleted {deleted_count} file(s) from GridFS in '{collection_name}' using query: {query}.")
        else:
            collection = self.get_collection(collection_name)
            result = collection.delete_many(query)
            Logger.info(f"Deleted {result.deleted_count} document(s) from '{collection_name}'.")

    def aggregate_documents(self, collection_name: str, pipeline: List[Dict[str, Any]]) -> List[Any]:
        """
        Aggregates documents in a specified collection using the provided pipeline.

        Args:
            collection_name (str): The collection name.
            pipeline (list): A list of aggregation stages.

        Returns:
            list: The result of the aggregation as a list of documents.

        Raises:
            Exception: Propagates any exceptions encountered during aggregation.
        """
        try:
            collection = self.db[collection_name]
            result = list(collection.aggregate(pipeline))
            Logger.info(f"Aggregation on collection '{collection_name}' completed successfully.")
            return result
        except Exception as e:
            Logger.error(f"Aggregation error on collection '{collection_name}': {str(e)}")
            raise e

    # ------------------------ GridFS Operations for TTS Files ------------------------

    def _store_file_in_gridfs(self, query: Dict[str, Any], file_data: bytes, metadata: Dict[str, Any] = None) -> str:
        """
        Deletes any existing files matching the query and stores a new file in GridFS.
        The encryption metadata is stored in the file's metadata field.

        Args:
            query (Dict[str, Any]): The query to identify files.
            file_data (bytes): The binary file data to store.
            metadata (Dict[str, Any], optional): Additional metadata to store with the file.

        Returns:
            str: The ID of the stored file.
        """
        Logger.info(f"Storing file in GridFS with query={query} and metadata={metadata}")
        existing_files = self.fs.find(query)
        for file in existing_files:
            Logger.info(f"Deleting old file with ID {file._id} from GridFS.")
            self.fs.delete(file._id)
        file_id = self.fs.put(file_data, metadata=metadata, **query)
        Logger.info(f"File successfully stored in GridFS with ID: {file_id}")
        return str(file_id)

    def store_tts_audio_in_gridfs(self, query: Dict[str, Any], file_data: bytes, metadata: Dict[str, Any]) -> str:
        """
        Stores TTS audio in GridFS along with encryption metadata.

        Args:
            query (Dict[str, Any]): The query parameters to index the file.
            file_data (bytes): The binary audio data.
            metadata (Dict[str, Any]): Additional metadata to store.

        Returns:
            str: The ID of the stored file.
        """
        return self._store_file_in_gridfs(query, file_data, metadata)

    def retrieve_tts_audio_from_gridfs(self, user: str, page: int, title: str, language: str) -> Union[io.BytesIO, None]:
        """
        Retrieves a stored TTS audio file from GridFS.

        Args:
            user (str): The username associated with the file.
            page (int): The page number associated with the file.
            title (str): The title associated with the file.
            language (str): The language of the audio file.

        Returns:
            io.BytesIO or None: A BytesIO stream of the file if found; otherwise, None.
        """
        query = {"user": user, "page": page, "title": title, "language": language}
        Logger.info(f"Retrieving TTS audio from GridFS with query={query}")
        file = self.fs.find_one(query)
        if not file:
            Logger.info("No TTS audio found in GridFS.")
            return None
        Logger.info(f"File found in GridFS with ID: {file._id}")
        file_buffer = io.BytesIO(file.read())
        file_buffer.seek(0)
        # Attach metadata for later use (if needed)
        file_buffer.metadata = file.metadata
        return file_buffer

    # ------------------------ Text Processing & Translations ------------------------

    def _retrieve_single_document(self, collection_name: str, query: Dict[str, Any]) -> Union[Dict[str, Any], None]:
        """
        Retrieves a single document matching the query from a specified collection.

        Args:
            collection_name (str): The collection name.
            query (Dict[str, Any]): The query to match.

        Returns:
            dict or None: The first matching document, or None if no document is found.
        """
        documents = self.find_documents(collection_name, query)
        return documents[0] if documents else None

    def retrieve_and_decrypt_page(
            self,
            user: str,
            page: int,
            title: str,
            user_files_collection: str,
            crypto_manager: Crypto_Manager
    ) -> Union[dict, list]:
        """
        Retrieves a document representing a page from a user file, decrypts it,
        and returns the resulting data.

        Args:
            user (str): The username.
            page (int): The page number.
            title (str): The title associated with the file.
            user_files_collection (str): The collection name.
            crypto_manager (Crypto_Manager): The crypto manager for decryption.

        Returns:
            dict or list: The decrypted content of the page.
        """
        query = {"user": user, "page": page, "title": title}
        Logger.info(f"Retrieving page with query={query} from collection '{user_files_collection}'.")
        doc = self._retrieve_single_document(user_files_collection, query)
        if not doc or "text" not in doc or "source" not in doc["text"]:
            raise ValueError(f"No valid document found for user={user}, page={page}, title={title}.")
        decrypted_bytes = crypto_manager.decrypt_file(user, doc["text"]["source"])
        return json.loads(decrypted_bytes.decode("utf-8"))

    def retrieve_and_decrypt_translation(
            self,
            user: str,
            page: int,
            title: str,
            language: str,
            user_files_collection: str,
            crypto_manager: Crypto_Manager
    ) -> Union[str, None]:
        """
        Retrieves and decrypts a translated text from a document.

        Args:
            user (str): The username.
            page (int): The page number.
            title (str): The title associated with the file.
            language (str): The target language for the translation.
            user_files_collection (str): The collection name.
            crypto_manager (Crypto_Manager): The crypto manager for decryption.

        Returns:
            str or None: The decrypted translation text if found; otherwise, None.
        """
        query = {"user": user, "page": page, "title": title}
        Logger.info(f"Retrieving translation for language={language} from '{user_files_collection}' with query={query}.")
        doc = self._retrieve_single_document(user_files_collection, query)
        if not doc or "translations" not in doc or language not in doc["translations"]:
            return None
        decrypted_bytes = crypto_manager.decrypt_file(user, doc["translations"][language])
        return decrypted_bytes.decode("utf-8")

    @staticmethod
    def get_encrypted_file_size_mb(encrypted_file_lib: dict) -> float:
        """
        Calculates and returns the size of the encrypted file in megabytes.

        Args:
            encrypted_file_lib (dict): Dictionary containing encrypted file components.

        Returns:
            float: The size of the encrypted file in MB.
        """
        total_size_bytes = (
            len(encrypted_file_lib["Ephemeral_public_key_der"]) +
            len(encrypted_file_lib["Nonce"]) +
            len(encrypted_file_lib["Tag"]) +
            len(encrypted_file_lib["Ciphertext"])
        )
        return total_size_bytes / (1024 * 1024)
