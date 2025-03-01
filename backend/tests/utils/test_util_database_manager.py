import unittest
from unittest.mock import patch, MagicMock
from backend.app.utils.util_mongo_manager import MongoDBManager


class TestMongoDBManager(unittest.TestCase):
    def setUp(self):
        """
        Set up a single mock MongoDB instance and associated dependencies.
        This is executed before every test.
        """
        self.patcher_mongo_client = patch("backend.app.utils.util_mongo_manager.MongoClient")
        self.mock_mongo_client = self.patcher_mongo_client.start()

        # Create a mock for the MongoClient and its database access
        self.mock_client = MagicMock()
        self.mock_db = MagicMock()
        self.mock_mongo_client.return_value = self.mock_client
        self.mock_client.__getitem__.return_value = self.mock_db

        # Patch ConfigManager
        self.patcher_config_manager = patch("backend.app.utils.util_mongo_manager.ConfigManager")
        self.mock_config_manager = self.patcher_config_manager.start()
        self.mock_config_manager.return_value.get_config_value.side_effect = lambda section, key, _: {
            ("MONGO_DB", "CONNECTION_STRING", str): "mongodb://mock_connection_string",
            ("MONGO_DB", "MONGO_DATABASE", str): "mock_database",
        }.get((section, key, _))

        # Patch GridFS
        self.patcher_gridfs = patch("backend.app.utils.util_mongo_manager.gridfs.GridFS")
        self.mock_gridfs = self.patcher_gridfs.start()

        # Create an instance of MongoDBManager
        self.manager = MongoDBManager()
        self.manager.client = self.mock_client  # Inject mock client
        self.manager.db = self.mock_db  # Inject mock database

        # Mock collections
        self.mock_collection = MagicMock()
        self.mock_db.__getitem__.return_value = self.mock_collection
        self.mock_db.list_collection_names.return_value = ["test_collection", "test_gridfs_collection"]

    def tearDown(self):
        """
        Stop all patches after every test.
        """
        self.patcher_mongo_client.stop()
        self.patcher_config_manager.stop()
        self.patcher_gridfs.stop()


    def test_get_collection_success(self):
        """
        Verify that get_collection returns the correct collection when it exists.
        """
        collection_name = "test_collection"
        mock_collection = MagicMock()
        self.mock_db.__getitem__.return_value = mock_collection
        self.mock_db.list_collection_names.return_value = [collection_name]

        collection = self.manager.get_collection(collection_name)

        self.assertEqual(collection, mock_collection)

    def test_get_collection_nonexistent(self):
        """
        Verify that get_collection raises a ValueError when the requested collection does not exist.
        """
        self.mock_db.list_collection_names.return_value = []

        with self.assertRaises(ValueError):
            self.manager.get_collection("nonexistent_collection")

    def test_insert_document(self):
        """
        Verify that insert_document calls insert_one with the correct document.
        """
        collection_name = "test_collection"
        document = {"key": "value"}
        mock_collection = MagicMock()
        self.mock_db.__getitem__.return_value = mock_collection

        self.manager.insert_document(collection_name, document)

        mock_collection.insert_one.assert_called_once_with(document)

    def test_insert_document_with_gridfs(self):
        """
        Verify that insert_document correctly stores a file using GridFS.
        """
        collection_name = "test_gridfs_collection"
        mock_fs = self.mock_gridfs.return_value
        file_data = b"binary_data"
        document = {"filename": "test.txt", "file": file_data}

        file_id = self.manager.insert_document(collection_name, document, use_GridFS=True)

        mock_fs.put.assert_called_once_with(file_data, filename="test.txt")
        self.assertEqual(file_id, mock_fs.put.return_value)

    def test_find_documents(self):
        """
        Verify that find_documents returns the correct list of documents.
        """
        collection_name = "test_collection"
        query = {"key": "value"}
        expected_documents = [{"key": "value1"}, {"key": "value2"}]
        mock_collection = MagicMock()
        mock_collection.find.return_value = expected_documents
        self.mock_db.__getitem__.return_value = mock_collection

        result = self.manager.find_documents(collection_name, query)

        mock_collection.find.assert_called_once_with(query)
        self.assertEqual(result, expected_documents)

    def test_find_documents_with_gridfs(self):
        """
        Verify that find_documents fetches files correctly from GridFS.
        """
        collection_name = "test_gridfs_collection"
        query = {"key": "value"}
        mock_fs = self.mock_gridfs.return_value
        mock_file = MagicMock()
        mock_fs.find.return_value = [mock_file]

        result = self.manager.find_documents(collection_name, query, use_GridFS=True)

        mock_fs.find.assert_called_once_with(query)
        self.assertEqual(result, [mock_file])

    def test_delete_documents(self):
        """
        Verify that delete_documents calls delete_many with the correct query.
        """
        collection_name = "test_collection"
        query = {"key": "value"}
        mock_collection = MagicMock()
        mock_delete_result = MagicMock()
        mock_delete_result.deleted_count = 3
        mock_collection.delete_many.return_value = mock_delete_result
        self.mock_db.__getitem__.return_value = mock_collection

        result = self.manager.delete_documents(collection_name, query)

        mock_collection.delete_many.assert_called_once_with(query)
        self.assertEqual(result.deleted_count, 3)

    def test_delete_documents_with_gridfs(self):
        """
        Verify that delete_documents correctly removes files from GridFS.
        """
        collection_name = "test_gridfs_collection"
        query = {"key": "value"}
        mock_fs = self.mock_gridfs.return_value
        mock_file = MagicMock()
        mock_file._id = "mock_id"
        mock_fs.find.return_value = [mock_file]

        self.manager.delete_documents(collection_name, query, use_GridFS=True)

        mock_fs.find.assert_called_once_with(query)
        mock_fs.delete.assert_called_once_with(mock_file._id)


if __name__ == "__main__":
    unittest.main()
