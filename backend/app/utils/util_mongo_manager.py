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
    Singleton-Klasse für das MongoDB-Management mit GridFS-Unterstützung.
    Verwaltung von CRUD-Operationen, TTS-Dateien und Übersetzungen.
    """
    _instance = None

    def __new__(cls) -> "MongoDBManager":
        if cls._instance is None:
            cls._instance = super(MongoDBManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self) -> None:
        """Initialisiert die MongoDB-Verbindung und GridFS."""
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
            self.fs = gridfs.GridFS(self.db, collection="tts_files")  # GridFS für TTS-Dateien
            self.client.admin.command("ping")
            Logger.info(f"Connected to MongoDB database '{self.database_name}' successfully.")
        except errors.ServerSelectionTimeoutError as e:
            Logger.error(f"Could not connect to MongoDB: {e}")
            raise

    # -------------------------------------------------------------------------
    # 🔹 CRUD-Methoden für allgemeine Datenbankoperationen
    # -------------------------------------------------------------------------

    def get_collection(self, collection_name: str):
        collections = self.db.list_collection_names()
        if collection_name not in collections:
            Logger.info(f"Collection '{collection_name}' does not exist. It will be created on first insert.")
        return self.db[collection_name]

    def insert_document(self, collection_name: str, document: Dict[str, Any]) -> Any:
        """Fügt ein neues Dokument in die Sammlung ein."""
        collection = self.get_collection(collection_name)
        result = collection.insert_one(document)
        Logger.info(f"Inserted document into '{collection_name}' with ID: {result.inserted_id}.")
        return result.inserted_id

    def find_documents(self, collection_name: str, query: Dict[str, Any]) -> List[Any]:
        """Findet Dokumente, die dem Query entsprechen."""
        collection = self.get_collection(collection_name)
        documents = list(collection.find(query))
        Logger.info(f"Found {len(documents)} documents in '{collection_name}'.")
        return documents

    def update_document(
            self,
            collection_name: str,
            query: Dict[str, Any],
            update: Dict[str, Any],
            upsert: bool = False
    ) -> Any:
        """Aktualisiert oder fügt ein Dokument in MongoDB hinzu (falls `upsert=True`)."""
        collection = self.get_collection(collection_name)
        result = collection.update_one(query, update, upsert=upsert)
        Logger.info(
            f"Updated document(s) in '{collection_name}'. Matched: {result.matched_count}, Modified: {result.modified_count}.")
        return result

    def delete_documents(self, collection_name: str, query: Dict[str, Any]) -> None:
        """Löscht Dokumente basierend auf einer Query."""
        collection = self.get_collection(collection_name)
        result = collection.delete_many(query)
        Logger.info(f"Deleted {result.deleted_count} documents from '{collection_name}'.")

    # -------------------------------------------------------------------------
    # 🔹 TTS-Dateien in GridFS speichern & abrufen
    # -------------------------------------------------------------------------

    def store_tts_audio_in_gridfs(self, query: Dict[str, Any], file_data: bytes) -> str:
        """
        Speichert eine TTS-Audiodatei in GridFS.

        Args:
            query (dict): Metadaten zur Datei (z.B. {'user': 'Admin', 'page': 1, ...}).
            file_data (bytes): Audiodatei als Bytes.

        Returns:
            str: ID der gespeicherten Datei.
        """
        Logger.info(f"Storing TTS audio in GridFS for query={query}")

        existing_files = self.fs.find(query)
        for file in existing_files:
            Logger.info(f"🗑 Deleting old file with ID {file._id} from GridFS...")
            self.fs.delete(file._id)

        file_id = self.fs.put(file_data, **query)
        Logger.info(f"✅ Stored new TTS audio in GridFS with ID: {file_id}")
        return str(file_id)

    def retrieve_tts_audio_from_gridfs(self, user: str, page: int, title: str, language: str) -> Union[
        io.BytesIO, None]:
        """
        Ruft eine gespeicherte TTS-Audiodatei aus GridFS ab.

        Returns:
            io.BytesIO: Audio-Stream oder None, falls nicht gefunden.
        """
        query = {"user": user, "page": page, "title": title, "language": language}
        Logger.info(f"Retrieving TTS audio from GridFS with query={query}")

        file = self.fs.find_one(query)
        if not file:
            Logger.info("No TTS audio found in GridFS.")
            return None

        Logger.info(f"✅ Found TTS audio file in GridFS with ID: {file._id}")
        audio_buffer = io.BytesIO(file.read())
        audio_buffer.seek(0)
        return audio_buffer

    # -------------------------------------------------------------------------
    # 🔹 Textverarbeitung & Übersetzungen
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
        Holt ein verschlüsseltes Dokument aus MongoDB, entschlüsselt es und gibt es zurück.
        """
        query = {"user": user, "page": page, "title": title}
        Logger.info(f"Retrieving page with query={query} from collection '{user_files_collection}'.")

        doc = self.find_documents(user_files_collection, query)
        if not doc:
            raise ValueError(f"No matching document found for user={user}, page={page}, title={title}.")

        encrypted_source = doc[0]["text"]["source"]
        decrypted_bytes = crypto_manager.decrypt_file(user, encrypted_source)
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
        Ruft eine Übersetzung ab, entschlüsselt sie und gibt den Text zurück.
        """
        query = {"user": user, "page": page, "title": title}
        Logger.info(f"Retrieving translation for lang={language} with query={query} from {user_files_collection}.")

        doc = self.find_documents(user_files_collection, query)
        if not doc or language not in doc[0].get("translations", {}):
            return None

        encrypted_translation = doc[0]["translations"][language]
        decrypted_bytes = crypto_manager.decrypt_file(user, encrypted_translation)
        return decrypted_bytes.decode("utf-8")
