import gridfs
from pymongo import MongoClient, errors
from typing import Any, Dict, List, Union
from backend.app.utils.util_config_manager import ConfigManager
from backend.app.utils.util_logger import Logger


class MongoDBManager:
    """
    Singleton-Klasse zur Verwaltung von MongoDB-Operationen.

    Ermöglicht grundlegende Operationen wie das Einfügen, Suchen und Löschen von Dokumenten.
    Wenn eine Collection nicht existiert, wird diese beim ersten Insert automatisch erstellt.
    """
    _instance = None

    def __new__(cls) -> "MongoDBManager":
        if cls._instance is None:
            cls._instance = super(MongoDBManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self) -> None:
        """
        Initialisiert die MongoDB-Verbindung anhand der Konfiguration.
        """
        self.config_manager = ConfigManager()

        self.connection_string: str = self.config_manager.get_config_value("MONGO_DB", "CONNECTION_STRING", str)
        self.database_name: str = self.config_manager.get_config_value("MONGO_DB", "MONGO_DATABASE", str)

        if not self.database_name:
            Logger.error("Database name is not set in the configuration.")
            raise ValueError("Database name is not set in the configuration.")

        # Debug-Ausgaben: Connection String und Datenbankname
        Logger.info(f"Using connection string: {self.connection_string}")
        Logger.info(f"Using database: {self.database_name}")

        try:
            self.client = MongoClient(self.connection_string, serverSelectionTimeoutMS=5000)
            self.db = self.client[self.database_name]
            self.client.admin.command("ping")
            Logger.warning(self.db.list_collection_names())
            Logger.info(f"Connected to MongoDB database '{self.database_name}' successfully.")
        except errors.ServerSelectionTimeoutError as e:
            Logger.error(f"Could not connect to MongoDB: {e}")
            raise

    def get_collection(self, collection_name: str):
        collections = self.db.list_collection_names()
        if collection_name not in collections:
            Logger.info(f"Collection '{collection_name}' does not exist. It will be created on first insert.")
        Logger.info(f"Retrieved collection '{collection_name}'.")
        return self.db[collection_name]

    def check_health(self) -> Dict[str, str]:
        """
        Prüft den Verbindungsstatus zur MongoDB.

        Returns:
            dict: Ein Dictionary mit dem Verbindungsstatus.
        """
        try:
            self.client.admin.command("ping")
            Logger.info("✅ MongoDB is healthy.")
            return {"status": "healthy", "database": "connected"}
        except errors.PyMongoError as e:
            Logger.error(f"❌ MongoDB health check failed: {e}")
            return {"status": "unhealthy", "database": "disconnected", "error": str(e)}

    def insert_document(self, collection_name: str, document: Dict[str, Any], use_GridFS: bool = False) -> Union[Any, str]:
        """
        Fügt ein Dokument in eine MongoDB-Collection ein.

        Args:
            collection_name (str): Name der Collection.
            document (dict): Das einzufügende Dokument.
            use_GridFS (bool): Falls True, wird GridFS verwendet.

        Returns:
            Das Ergebnis des Insertionsvorgangs oder die GridFS-Datei-ID.
        """
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
        """
        Sucht nach Dokumenten in einer MongoDB-Collection.

        Args:
            collection_name (str): Name der Collection.
            query (dict): MongoDB-Abfrage.
            use_GridFS (bool): Falls True, wird in GridFS gesucht.

        Returns:
            Liste der gefundenen Dokumente bzw. Dateien.
        """
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
        """
        Löscht Dokumente aus einer MongoDB-Collection.

        Args:
            collection_name (str): Name der Collection.
            query (dict): MongoDB-Abfrage.
            use_GridFS (bool): Falls True, wird in GridFS gelöscht.
        """
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
