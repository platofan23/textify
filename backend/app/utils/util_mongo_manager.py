import io
import json

import gridfs
from pymongo import MongoClient, errors
from typing import Any, Dict, List, Union, Tuple
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
            collection_name (str): Name of the (GridFS-)Collection in MongoDB.
            query (dict): The query to find the document(s).
            update (dict): The update instructions (ignored if use_GridFS=True).
            upsert (bool, optional): Insert if no match is found. Defaults to False.
            use_GridFS (bool, optional): If True, store/delete files in GridFS instead of normal update.
            file_data (bytes, optional): The binary data to store (only required if use_GridFS=True).

        Returns:
            - GridFS file ID (if use_GridFS=True)
            - UpdateResult (if use_GridFS=False)
        """
        # Falls wir GridFS verwenden:
        if use_GridFS:
            if not file_data:
                raise ValueError("file_data is required when using GridFS.")

            fs = gridfs.GridFS(self.db, collection=collection_name)

            # 1) Alte Dateien löschen (GridFS kann nicht direkt 'updaten', daher löschen und neu anlegen).
            existing_files = fs.find(query)
            for old_file in existing_files:
                Logger.info(f"🗑️ Deleting old file with ID {old_file._id} from GridFS collection '{collection_name}'.")
                fs.delete(old_file._id)

            # 2) Neue Datei in GridFS anlegen.
            #    Metadaten werden aus `query` übernommen, damit man file_obj.<field> = ... abfragen kann.
            file_id = fs.put(file_data, **query)
            Logger.info(f"✅ Inserted file into GridFS collection '{collection_name}' with ID: {file_id}.")
            return file_id

        # --- Normales UpdateOne in einer Collection ---
        collection = self.get_collection(collection_name)

        # Prüfen, ob im 'update' bereits ein Mongo-Operator enthalten ist.
        # Falls nicht, fassen wir das in {"$set": ...} ein.
        if not any(key.startswith("$") for key in update.keys()):
            update = {"$set": update}

        result = collection.update_one(query, update, upsert=upsert)

        Logger.info(
            f"📌 Updated document(s) in '{collection_name}' "
            f"| Matched: {result.matched_count}, Modified: {result.modified_count}."
        )
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
    ) -> Union[dict, list]:
        """
        Retrieves a document from 'user_files_collection' for the given user/page/title,
        decrypts doc['text']['source'] using the Crypto_Manager, and returns the structured data.

        Args:
            user (str): The user requesting the document.
            page (int): The page number.
            title (str): The document title.
            user_files_collection (str): MongoDB collection name.
            crypto_manager (Crypto_Manager): The encryption manager instance.

        Returns:
            Union[dict, list]: The decrypted document structure (can be a dict or list).

        Raises:
            ValueError: If the document or the 'source' field is missing.
        """
        query = {"user": user, "page": page, "title": title}
        Logger.info(f"Retrieving page with query={query} from collection '{user_files_collection}'.")

        doc = self._retrieve_document(user_files_collection, query)

        if not doc:
            raise ValueError(f"No matching document found for user={user}, page={page}, title={title}.")

        if "text" not in doc or "source" not in doc["text"]:
            raise ValueError("Document does not contain 'text' or 'source' field.")

        # Entschlüsselung des 'source'-Blocks innerhalb 'text'
        encrypted_source = doc["text"]["source"]
        decrypted_bytes = self._decrypt_data(user, encrypted_source, crypto_manager)

        try:
            # Konvertiere das entschlüsselte Byte-Array zurück zu JSON
            decrypted_data = json.loads(decrypted_bytes.decode("utf-8"))
            Logger.info(f"Successfully decrypted source text. Data type: {type(decrypted_data)}")

            if not isinstance(decrypted_data, (dict, list)):
                raise ValueError(f"Unexpected decrypted format: Expected dict or list, got {type(decrypted_data)}")

            return decrypted_data

        except json.JSONDecodeError as e:
            Logger.error(f"Failed to parse decrypted source text: {str(e)}")
            raise ValueError("Decrypted source text is not a valid JSON format.")

    def retrieve_and_decrypt_tts_audio(
            self,
            user: str,
            page: int,
            title: str,
            language: str,
            tts_files_collection: str,
            crypto_manager: Crypto_Manager
    ) -> Tuple[Union[dict, None], Union[io.BytesIO, None]]:
        """
        Retrieves encrypted TTS audio from GridFS by user/page/title/language,
        decrypts it, and returns (doc, audio_buffer).
        If not found or missing audio, returns (None, None).

        Args:
            user (str): The username (for loading the user's private key).
            page (int): The page number.
            title (str): The document title.
            language (str): The TTS audio language or voice tag.
            tts_files_collection (str): The name of the GridFS collection for TTS files.
            crypto_manager (Crypto_Manager): For decrypting the audio.

        Returns:
            (dict or None, io.BytesIO or None):
                - A dictionary with the file's metadata (doc) if found,
                - A BytesIO stream with the decrypted audio.
                or (None, None) if not found or missing.
        """
        query = {"user": user, "page": page, "title": title, "language": language}
        Logger.info(f"Retrieving TTS audio with query={query} from GridFS collection '{tts_files_collection}'.")

        fs = gridfs.GridFS(self.db, collection=tts_files_collection)

        # Finde passendes TTS-File in GridFS
        matching_files = list(fs.find(query))
        if not matching_files:
            Logger.info(f"No TTS audio found for {query}. -> (None, None)")
            return None, None

        # Nimm das erste gefundene. (Wenn du mehrere Versionen haben kannst, musst du ggf. alle durchgehen.)
        file_obj = matching_files[0]
        Logger.debug(f"Found TTS GridFS file ID={file_obj._id}. Retrieving data...")

        # Gelesene verschlüsselte Bytes
        encrypted_audio_data = file_obj.read()
        if not encrypted_audio_data:
            Logger.info("Found TTS file but it is empty -> (None, None).")
            return None, None

        Logger.info("Decrypting existing TTS audio.")
        # Audio entschlüsseln
        try:
            decrypted_audio_bytes = crypto_manager.decrypt_file(user, encrypted_audio_data)
            audio_buffer = io.BytesIO(decrypted_audio_bytes)
            audio_buffer.seek(0)
        except Exception as e:
            Logger.error(f"Failed to decrypt TTS audio: {str(e)}")
            return None, None

        Logger.info("Successfully retrieved existing TTS audio from GridFS.")
        # dateiMetadaten = file_obj (enthält doc._id, length, uploadDate, etc.)
        # Du kannst das in ein dict konvertieren oder so zurückgeben.
        file_doc = {
            "_id": file_obj._id,
            "filename": file_obj.filename,
            "user": file_obj.user if hasattr(file_obj, "user") else None,
            "page": file_obj.page if hasattr(file_obj, "page") else None,
            "title": file_obj.title if hasattr(file_obj, "title") else None,
            "language": file_obj.language if hasattr(file_obj, "language") else None,
            "length": file_obj.length,
            "uploadDate": file_obj.uploadDate
        }

        return file_doc, audio_buffer

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
