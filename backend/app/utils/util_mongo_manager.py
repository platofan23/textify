import io

import gridfs
from pymongo import MongoClient, errors
from typing import Any, Dict, List, Union
from backend.app.utils.util_config_manager import ConfigManager
from backend.app.utils import Logger
from backend.app.utils.util_crypt import Crypto_Manager


class MongoDBManager:
    """
    A singleton class for managing MongoDB operations.
    Provides basic CRUD functionality and extended methods for
    retrieving and decrypting text or audio fields.
    """
    _instance = None

    def __new__(cls) -> "MongoDBManager":
        if cls._instance is None:
            cls._instance = super(MongoDBManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self) -> None:
        """Initialize the MongoDB connection using ConfigManager."""
        self.config_manager = ConfigManager()
        self.connection_string: str = self.config_manager.get_config_value("MONGO_DB", "CONNECTION_STRING", str)
        self.database_name: str = self.config_manager.get_config_value("MONGO_DB", "MONGO_DATABASE", str)

        if not self.database_name:
            Logger.error("Database name is not set in the configuration.")
            raise ValueError("Database name is not set in the configuration.")

        Logger.info(f"Using connection string: {self.connection_string}")
        Logger.info(f"Using database: {self.database_name}")

        try:
            self.client = MongoClient(self.connection_string, serverSelectionTimeoutMS=5000)
            self.db = self.client[self.database_name]
            self.client.admin.command("ping")
            Logger.info(f"Connected to MongoDB database '{self.database_name}' successfully.")
        except errors.ServerSelectionTimeoutError as e:
            Logger.error(f"Could not connect to MongoDB: {e}")
            raise

    # -------------------------------------------------------------------------
    # Interne Hilfsmethoden (DRY-Prinzip)
    # -------------------------------------------------------------------------
    def _retrieve_document(self, collection_name: str, query: dict) -> Union[dict, None]:
        """
        Retrieves a single document matching 'query' from 'collection_name'.
        Logs additional debug info, returns the first matched doc or None if none found.
        """
        Logger.debug(f"Retrieving document from collection='{collection_name}' with query={query}")

        if collection_name not in self.db.list_collection_names():
            Logger.error(f"Collection '{collection_name}' does not exist in the database!")
            return None

        docs = self.find_documents(collection_name, query, use_GridFS=False)

        if not docs:
            Logger.warning(
                f"No documents found in '{collection_name}' for query={query}. Checking existing documents...")
            all_docs = self.find_documents(collection_name, {}, use_GridFS=False)  # Get all docs for debugging
            return None

        return docs[0]

    def _decrypt_data(self, user: str, encrypted_data: dict, crypto_manager: Crypto_Manager) -> bytes:
        """
        Decrypts an encrypted data dictionary using Crypto_Manager.decrypt_file().
        Returns raw decrypted bytes. Raises ValueError if empty or None.
        """
        if not encrypted_data:
            raise ValueError("Encrypted data is empty or missing.")
        return crypto_manager.decrypt_file(user, encrypted_data)

    # -------------------------------------------------------------------------
    # Allgemeine CRUD-Methoden
    # -------------------------------------------------------------------------
    def get_collection(self, collection_name: str):
        collections = self.db.list_collection_names()
        if collection_name not in collections:
            Logger.info(f"Collection '{collection_name}' does not exist. It will be created on first insert.")
        Logger.info(f"Retrieved collection '{collection_name}'.")
        return self.db[collection_name]

    def check_health(self) -> Dict[str, str]:
        try:
            self.client.admin.command("ping")
            Logger.info("✅ MongoDB is healthy.")
            return {"status": "healthy", "database": "connected"}
        except errors.PyMongoError as e:
            Logger.error(f"❌ MongoDB health check failed: {e}")
            return {"status": "unhealthy", "database": "disconnected", "error": str(e)}

    def insert_document(self, collection_name: str, document: Dict[str, Any], use_GridFS: bool = False) -> Union[Any, str]:
        if use_GridFS:
            fs = gridfs.GridFS(self.db, collection=collection_name)
            file_data = document.pop("file", None)
            if file_data is None:
                Logger.error("No file data provided for GridFS insertion.")
                raise ValueError("No file data provided for GridFS insertion.")
            file_id = fs.put(file_data, **document)
            Logger.info(f"Inserted file into GridFS collection '{collection_name}' with ID: {file_id}.")
            return file_id

        collection = self.get_collection(collection_name)
        result = collection.insert_one(document)
        Logger.info(f"Inserted document into collection '{collection_name}' with ID: {result.inserted_id}.")
        return result

    def find_documents(self, collection_name: str, query: Dict[str, Any], use_GridFS: bool = False) -> List[Any]:
        if use_GridFS:
            fs = gridfs.GridFS(self.db, collection=collection_name)
            files = list(fs.find(query))
            Logger.info(f"Found {len(files)} files in GridFS collection '{collection_name}' matching query: {query}.")
            return files

        collection = self.get_collection(collection_name)
        documents = list(collection.find(query))
        Logger.info(f"Found {len(documents)} documents in collection '{collection_name}' matching query: {query}.")
        return documents

    def delete_documents(self, collection_name: str, query: Dict[str, Any], use_GridFS: bool = False) -> Union[None, Any]:
        if use_GridFS:
            fs = gridfs.GridFS(self.db, collection=collection_name)
            files = list(fs.find(query))
            count_deleted = 0
            for file in files:
                fs.delete(file._id)
                count_deleted += 1
            Logger.info(f"Deleted {count_deleted} files from GridFS collection '{collection_name}' matching query: {query}.")
            return

        collection = self.get_collection(collection_name)
        result = collection.delete_many(query)
        Logger.info(f"Deleted {result.deleted_count} documents from collection '{collection_name}' matching query: {query}.")
        return result

    def aggregate_documents(self, collection_name: str, pipeline: list):
        collection = self.get_collection(collection_name)
        result = list(collection.aggregate(pipeline))
        Logger.info(f"Aggregated documents in collection '{collection_name}' with pipeline: {pipeline}.")
        return result

    def update_document(
            self,
            collection_name: str,
            query: Dict[str, Any],
            update: Dict[str, Any],
            upsert: bool = False,
            use_GridFS: bool = False,
            file_data: bytes = None
    ) -> Any:
        """
        Updates a document in MongoDB or stores large binary files in GridFS.

        Args:
            collection_name (str): The name of the collection.
            query (dict): MongoDB query to find the document.
            update (dict): The update operations (ignored if use_GridFS=True).
            upsert (bool, optional): Whether to insert if no match is found. Defaults to False.
            use_GridFS (bool, optional): If True, store the file using GridFS. Defaults to False.
            file_data (bytes, optional): The binary data to store (only required if use_GridFS=True).

        Returns:
            result (UpdateResult or GridFS file ID): Update operation result or the GridFS file ID.
        """
        if use_GridFS:
            if not file_data:
                raise ValueError("file_data is required when using GridFS.")

            fs = gridfs.GridFS(self.db, collection=collection_name)

            # Delete existing files before inserting new one
            existing_files = fs.find(query)
            for file in existing_files:
                Logger.info(f"🗑️ Deleting old file with ID {file._id} from GridFS...")
                fs.delete(file._id)

            # Store the new file in GridFS
            file_id = fs.put(file_data, **query)
            Logger.info(f"✅ Inserted file into GridFS collection '{collection_name}' with ID: {file_id}.")
            return file_id

        # Standard document update
        collection = self.get_collection(collection_name)
        result = collection.update_one(query, update, upsert=upsert)
        Logger.info(
            f"📌 Updated document(s) in '{collection_name}' | Matched: {result.matched_count}, Modified: {result.modified_count}.")
        return result

    # -------------------------------------------------------------------------
    # Spezifische Methoden (keine Code-Dupletten dank interner Hilfsmethoden!)
    # -------------------------------------------------------------------------
    def retrieve_and_decrypt_page(
        self,
        user: str,
        page: int,
        title: str,
        user_files_collection: str,
        crypto_manager: Crypto_Manager
    ) -> str:
        """
        Retrieves a document from 'user_files_collection' for the given user/page/title,
        decrypts doc['source'] using the Crypto_Manager, and returns the plaintext as a string.

        Raises ValueError if not found or 'source' missing.
        """
        query = {"user": user, "page": page, "title": title}
        Logger.info(f"Retrieving page with query={query} from {user_files_collection}.")
        doc = self._retrieve_document(user_files_collection, query)
        if not doc:
            raise ValueError(f"No matching document found for user={user}, page={page}, title={title}.")

        if "source" not in doc:
            raise ValueError("Document does not contain 'source' field.")
        # Entschlüsseln:
        decrypted_bytes = self._decrypt_data(user, doc["source"], crypto_manager)
        return decrypted_bytes.decode("utf-8")

    def retrieve_and_decrypt_tts_audio(
        self,
        user: str,
        page: int,
        title: str,
        language: str,
        tts_files_collection: str,
        crypto_manager: Crypto_Manager
    ) -> (Union[dict, None], Union[io.BytesIO, None]):
        """
        Checks if there's a TTS doc for (user, page, title, language) in 'tts_files_collection',
        decrypts doc["encrypted_audio"], and returns (doc, audio_buffer).
        Or (None, None) if not found or no 'encrypted_audio'.
        """
        query = {"user": user, "page": page, "title": title, "language": language}
        Logger.info(f"Retrieving TTS audio with query={query} from {tts_files_collection}.")
        doc = self._retrieve_document(tts_files_collection, query)
        if not doc or "encrypted_audio" not in doc or not doc["encrypted_audio"]:
            Logger.info("No TTS audio doc or 'encrypted_audio' missing/empty -> (None, None).")
            return None, None

        decrypted_bytes = self._decrypt_data(user, doc["encrypted_audio"], crypto_manager)
        audio_buffer = io.BytesIO(decrypted_bytes)
        audio_buffer.seek(0)
        return doc, audio_buffer

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
        Retrieves the doc from user_files_collection, checks if 'doc["translations"][language]' exists,
        decrypts it, and returns plaintext. If not found or empty -> None.
        """
        query = {"user": user, "page": page, "title": title}
        Logger.info(f"Retrieving translation lang={language} with query={query} from {user_files_collection}.")
        doc = self._retrieve_document(user_files_collection, query)
        if not doc:
            Logger.info("No doc found -> returning None.")
            return None

        if "translations" not in doc or language not in doc["translations"]:
            Logger.info("translations field or that language not found -> None.")
            return None

        encrypted_data = doc["translations"][language]
        if not encrypted_data:
            Logger.info("Translation is empty or None -> returning None.")
            return None

        decrypted_bytes = self._decrypt_data(user, encrypted_data, crypto_manager)
        return decrypted_bytes.decode("utf-8")
