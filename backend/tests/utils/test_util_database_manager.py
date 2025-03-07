import unittest
from unittest.mock import patch, MagicMock
from backend.app.utils.util_mongo_manager import MongoDBManager


class TestMongoDBManager(unittest.TestCase):
    """
    Unit tests for MongoDBManager, including GridFS operations.
    """

    def setUp(self):
        """
        Sets up a mock instance of MongoDB before each test.
        """
        self.patcher_mongo_client = patch("backend.app.utils.util_mongo_manager.MongoClient")
        self.mock_mongo_client = self.patcher_mongo_client.start()

        # Mock MongoDB client and database
        self.mock_client = MagicMock()
        self.mock_db = MagicMock()
        self.mock_mongo_client.return_value = self.mock_client
        self.mock_client.__getitem__.return_value = self.mock_db

        # Patch ConfigManager
        self.patcher_config_manager = patch("backend.app.utils.util_mongo_manager.ConfigManager")
        self.mock_config_manager = self.patcher_config_manager.start()
        self.mock_config_manager.return_value.get_config_value.side_effect = lambda section, key, value_type, default=None: {
            ("MONGO_DB", "CONNECTION_STRING", str): "mongodb://mock_connection_string",
            ("MONGO_DB", "MONGO_DATABASE", str): "mock_database",
            ("MONGO_DB", "TTS_FILES_COLLECTION", str): "tts_files",
        }.get((section, key, value_type), default)

        # Patch GridFS
        self.patcher_gridfs = patch("backend.app.utils.util_mongo_manager.gridfs.GridFS")
        self.mock_gridfs = self.patcher_gridfs.start()

        # Patch CryptoManager
        self.patcher_crypto_manager = patch("backend.app.utils.util_mongo_manager.CryptoManager")
        self.mock_crypto_manager = self.patcher_crypto_manager.start()

        # Instantiate MongoDBManager with the required parameter
        self.manager = MongoDBManager(self.mock_crypto_manager)
        self.manager.client = self.mock_client
        self.manager.db = self.mock_db

        # Mock collections & GridFS
        self.mock_collection = MagicMock()
        self.mock_db.__getitem__.return_value = self.mock_collection
        self.mock_db.list_collection_names.return_value = ["test_collection", "test_gridfs_collection"]

    def tearDown(self):
        """
        Stops all patches after each test.
        """
        self.patcher_mongo_client.stop()
        self.patcher_config_manager.stop()
        self.patcher_gridfs.stop()
        self.patcher_crypto_manager.stop()

    def test_get_collection_success(self):
        """Ensures that get_collection() retrieves an existing collection."""
        collection_name = "test_collection"
        self.mock_db.list_collection_names.return_value = [collection_name]

        collection = self.manager.get_collection(collection_name)
        self.assertEqual(collection, self.mock_db[collection_name])

    def test_get_collection_nonexistent(self):
        """Ensures that get_collection() creates a new collection if it does not exist."""
        collection_name = "new_collection"
        self.mock_db.list_collection_names.return_value = ["test_collection"]

        collection = self.manager.get_collection(collection_name)
        self.assertEqual(collection, self.mock_db[collection_name])

    def test_insert_document(self):
        """Ensures that insert_document() correctly stores a document."""
        collection_name = "test_collection"
        document = {"key": "value"}

        self.manager.insert_document(collection_name, document)

        self.mock_collection.insert_one.assert_called_once_with(document)


    def test_find_documents(self):
        """Ensures that find_documents() correctly retrieves documents."""
        collection_name = "test_collection"
        query = {"key": "value"}
        expected_documents = [{"key": "value1"}, {"key": "value2"}]
        self.mock_collection.find.return_value = expected_documents

        result = self.manager.find_documents(collection_name, query)

        self.mock_collection.find.assert_called_once_with(query)
        self.assertEqual(result, expected_documents)

    def test_delete_documents(self):
        """Ensures that delete_documents() correctly deletes documents."""
        collection_name = "test_collection"
        query = {"key": "value"}
        mock_delete_result = MagicMock()
        mock_delete_result.deleted_count = 3
        self.mock_collection.delete_many.return_value = mock_delete_result

        result = self.manager.delete_documents(collection_name, query)

        self.mock_collection.delete_many.assert_called_once_with(query)
        self.assertEqual(result, None)


if __name__ == "__main__":
    unittest.main()