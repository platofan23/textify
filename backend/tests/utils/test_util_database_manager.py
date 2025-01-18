import unittest
import logging
from unittest.mock import patch, MagicMock, call

from backend.app.utils.util_mongo_manager import MongoDBManager

# Configure the built-in logger to output DEBUG and WARNING messages.
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class TestMongoDBManager(unittest.TestCase):
    def setUp(self):
        """
        Set up a single mock MongoDB instance and associated dependencies.
        This is executed before every test.
        """
        logger.debug("Setting up test environment for TestMongoDBManager.")
        # Patch MongoClient in the module where it is used.
        self.patcher_mongo_client = patch("backend.app.utils.util_mongo_manager.MongoClient")
        self.mock_mongo_client = self.patcher_mongo_client.start()

        # Create a mock for the MongoClient and its database access.
        self.mock_client = MagicMock()
        self.mock_db = MagicMock()

        # Use a dictionary to manage mocked collections.
        self.collection_dict = {}

        # Define a side-effect function so that __getitem__ returns the appropriate
        # collection mock from our dictionary (if available).
        def get_collection(name):
            logger.debug("Accessing collection: %s", name)
            return self.collection_dict.get(name, MagicMock())

        self.mock_db.__getitem__.side_effect = get_collection

        # Set up the MongoClient mock to return our mock_db when a database is requested.
        self.mock_mongo_client.return_value = self.mock_client
        self.mock_client.__getitem__.return_value = self.mock_db

        # Patch the ConfigManager.
        self.patcher_config_manager = patch("backend.app.utils.util_mongo_manager.ConfigManager")
        self.mock_config_manager = self.patcher_config_manager.start()
        self.mock_config_manager.get_config_value.side_effect = lambda section, key, _: {
            ("MONGO_DB", "CONNECTION_STRING", str): "mongodb://mock_connection_string",
            ("MONGO_DB", "MONGO_DATABASE", str): "mock_database",
        }[(section, key, _)]

        # Create an instance of MongoDBManager.
        self.manager = MongoDBManager(self.mock_config_manager)
        logger.debug("Test environment setup complete.")

    def tearDown(self):
        """
        Stop all patches after every test.
        """
        logger.debug("Tearing down test environment for TestMongoDBManager.")
        self.patcher_mongo_client.stop()
        self.patcher_config_manager.stop()

    def prepare_mock_collection(self, collection_name):
        """
        Simulate the presence of a collection in the mock database.
        The collection is stored in a dictionary so that every subsequent __getitem__
        call with this collection name returns the same mock.
        """
        logger.debug("Preparing mock collection: %s", collection_name)
        # Create a specific mock for this collection.
        mock_collection = MagicMock()
        # Store the collection mock in the dictionary.
        self.collection_dict[collection_name] = mock_collection
        # Simulate that list_collection_names returns this collection name.
        self.mock_db.list_collection_names.return_value = list(self.collection_dict.keys())
        return mock_collection

    @patch("backend.app.utils.util_logger.Logger.info")
    def test_find_documents(self, mock_logger_info):
        """
        Verify that find_documents returns the expected documents,
        calls find with the correct query, and logs the operation properly.
        """
        logger.debug("Starting test_find_documents.")
        # Arrange: Define test parameters.
        test_collection = "test_collection"
        query = {"key": "value"}
        expected_documents = [{"key": "value"}, {"key": "value2"}]
        # The expected logger messages.
        expected_call_1 = call(f"Retrieved collection '{test_collection}'.")
        expected_call_2 = call(f"Found {len(expected_documents)} documents in collection '{test_collection}' matching query: {query}.")
        expected_calls = [expected_call_1, expected_call_2]

        # Prepare the collection by adding its mock to the dictionary.
        mock_collection = self.prepare_mock_collection(test_collection)
        # Re-instantiate the manager so that it picks up current mocks.
        self.manager = MongoDBManager(self.mock_config_manager)
        # Force the manager to use our updated mock_db.
        self.manager.db = self.mock_db

        # Define the behavior of find: return the expected documents.
        mock_collection.find.return_value = expected_documents

        # Act: Call find_documents.
        result = self.manager.find_documents(test_collection, query)
        logger.debug("Result from find_documents: %s", result)

        # Assert:
        mock_collection.find.assert_called_once_with(query)
        self.assertEqual(result, expected_documents)
        # Verify two logger calls have been made.
        self.assertEqual(mock_logger_info.call_count, 2)
        mock_logger_info.assert_has_calls(expected_calls)
        logger.debug("test_find_documents passed.")

    @patch("backend.app.utils.util_logger.Logger.info")
    def test_delete_documents(self, mock_logger_info):
        """
        Verify that delete_documents returns the expected count of deleted documents,
        that delete_many is called with the correct query, and that proper logging occurs.
        """
        logger.debug("Starting test_delete_documents.")
        # Arrange: Prepare the collection.
        test_collection = "test_collection"
        mock_collection = self.prepare_mock_collection(test_collection)
        self.manager = MongoDBManager(self.mock_config_manager)
        self.manager.db = self.mock_db

        # Simulate the outcome of delete_many.
        mock_delete_result = MagicMock()
        mock_delete_result.deleted_count = 3
        mock_collection.delete_many.return_value = mock_delete_result

        # Act: Call delete_documents.
        result = self.manager.delete_documents(test_collection, {"key": "value"})
        logger.debug("delete_documents result: %s", result.deleted_count)

        # Assert:
        mock_collection.delete_many.assert_called_once_with({"key": "value"})
        self.assertEqual(result.deleted_count, 3)
        # Two logger calls are expected:
        expected_calls = [
            call("Retrieved collection 'test_collection'."),
            call("Deleted 3 documents from collection 'test_collection' matching query: {'key': 'value'}.")
        ]
        self.assertEqual(mock_logger_info.call_count, 2)
        mock_logger_info.assert_has_calls(expected_calls)
        logger.debug("test_delete_documents passed.")

    @patch("backend.app.utils.util_logger.Logger.info")
    def test_get_collection_success(self, mock_logger_info):
        """
        Verify that get_collection returns the correct collection when it exists.
        """
        logger.debug("Starting test_get_collection_success.")
        # Arrange: Add the test collection to the dictionary.
        test_collection = "test_collection"
        self.prepare_mock_collection(test_collection)
        self.manager = MongoDBManager(self.mock_config_manager)
        self.manager.db = self.mock_db

        # Act: Call get_collection.
        collection = self.manager.get_collection(test_collection)
        logger.debug("get_collection returned: %s", collection)

        # Assert:
        self.assertTrue(isinstance(collection, MagicMock))
        mock_logger_info.assert_called_once_with("Retrieved collection 'test_collection'.")
        logger.debug("test_get_collection_success passed.")

    @patch("backend.app.utils.util_logger.Logger.warning")
    def test_get_collection_nonexistent(self, mock_logger_warning):
        """
        Verify that get_collection raises a ValueError when the requested collection does not exist.
        Also ensure that a warning is logged.
        """
        logger.debug("Starting test_get_collection_nonexistent.")
        # Arrange: Simulate that no collections exist.
        self.mock_db.list_collection_names.return_value = []
        # Set __getitem__ side-effect to return a new MagicMock for any name.
        self.mock_db.__getitem__.side_effect = lambda name: MagicMock()
        self.manager = MongoDBManager(self.mock_config_manager)
        self.manager.db = self.mock_db

        # Act & Assert:
        with self.assertRaises(ValueError) as context:
            self.manager.get_collection("nonexistent_collection")
        logger.debug("Caught expected ValueError: %s", context.exception)
        # Also ensure the warning is logged.
        mock_logger_warning.assert_called_once_with("Attempt to access non-existent collection 'nonexistent_collection'.")
        logger.debug("test_get_collection_nonexistent passed.")


if __name__ == "__main__":
    unittest.main()