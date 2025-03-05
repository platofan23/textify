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
        """Initializes the MongoDB connection and GridFS storage."""
        self.config_manager = ConfigManager()
        self.connection_string: str = self.config_manager.get_config_value("MONGO_DB", "CONNECTION_STRING", str)
        self.database_name: str = self.config_manager.get_config_value("MONGO_DB", "MONGO_DATABASE", str)

        if not self.database_name:
            Logger.error("Database name is not set in the configuration.")
            raise ValueError("Database name is not set in the configuration.")

        Logger.info(f"Connecting to MongoDB: {self.database_name}")

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

    # ------------------------ General CRUD Operations ------------------------

    def get_collection(self, collection_name: str):
        collections = self.db.list_collection_names()
        if collection_name not in collections:
            Logger.info(f"Collection '{collection_name}' does not exist. It will be created on first insert.")
        return self.db[collection_name]

    def insert_document(self, collection_name: str, document: Dict[str, Any]) -> Any:
        collection = self.get_collection(collection_name)
        result = collection.insert_one(document)
        Logger.info(f"Document inserted into '{collection_name}' with ID: {result.inserted_id}.")
        return result.inserted_id

    def find_documents(self, collection_name: str, query: Dict[str, Any]) -> List[Any]:
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
        collection = self.get_collection(collection_name)
        result = collection.update_one(query, update, upsert=upsert)
        Logger.info(
            f"Updated document(s) in '{collection_name}'. Matched: {result.matched_count}, Modified: {result.modified_count}.")
        return result

    def delete_documents(self, collection_name: str, query: Dict[str, Any]) -> None:
        collection = self.get_collection(collection_name)
        result = collection.delete_many(query)
        Logger.info(f"Deleted {result.deleted_count} document(s) from '{collection_name}'.")

    # ------------------------ GridFS Operations for TTS Files ------------------------

    def _store_file_in_gridfs(self, query: Dict[str, Any], file_data: bytes, metadata: Dict[str, Any] = None) -> str:
        """
        Deletes existing files matching the query and stores a new file in GridFS.
        The encryption metadata is stored in the file's metadata field.
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
        """Stores TTS audio in GridFS along with encryption metadata."""
        return self._store_file_in_gridfs(query, file_data, metadata)

    def retrieve_tts_audio_from_gridfs(self, user: str, page: int, title: str, language: str) -> Union[io.BytesIO, None]:
        """Retrieves a stored TTS audio file from GridFS."""
        query = {"user": user, "page": page, "title": title, "language": language}
        Logger.info(f"Retrieving TTS audio from GridFS with query={query}")
        file = self.fs.find_one(query)
        if not file:
            Logger.info("No TTS audio found in GridFS.")
            return None
        Logger.info(f"File found in GridFS with ID: {file._id}")
        file_buffer = io.BytesIO(file.read())
        file_buffer.seek(0)
        # The encryption metadata is stored in file.metadata
        file_buffer.metadata = file.metadata  # Attach metadata for later use
        return file_buffer

    # ------------------------ Text Processing & Translations ------------------------

    def _retrieve_single_document(self, collection_name: str, query: Dict[str, Any]) -> Union[Dict[str, Any], None]:
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
        query = {"user": user, "page": page, "title": title}
        Logger.info(f"Retrieving translation for language={language} from '{user_files_collection}' with query={query}.")
        doc = self._retrieve_single_document(user_files_collection, query)
        if not doc or "translations" not in doc or language not in doc["translations"]:
            return None
        decrypted_bytes = crypto_manager.decrypt_file(user, doc["translations"][language])
        return decrypted_bytes.decode("utf-8")

    @staticmethod
    def get_encrypted_file_size_mb(encrypted_file_lib: dict) -> float:
        total_size_bytes = (
            len(encrypted_file_lib["Ephemeral_public_key_der"]) +
            len(encrypted_file_lib["Nonce"]) +
            len(encrypted_file_lib["Tag"]) +
            len(encrypted_file_lib["Ciphertext"])
        )
        return total_size_bytes / (1024 * 1024)
