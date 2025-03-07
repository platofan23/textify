import logging
import pytest
from _pytest import unittest

from backend.app.utils import CacheManager

# Configure logging to capture DEBUG (and above) messages.
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@pytest.fixture
def mock_cache_manager():
    """
    Fixture to provide a CacheManager instance with a maxsize of 100.
    """
    logger.debug("Creating a CacheManager instance with maxsize 100.")
    return CacheManager(maxsize=100)


@pytest.fixture
def mock_config_manager():
    """
    Fixture to provide a simple mock configuration manager.
    This mock returns 'cpu' when get_torch_device() is called.
    """

    class MockConfigManager:
        def get_torch_device(self):
            logger.debug("MockConfigManager.get_torch_device called, returning 'cpu'.")
            return 'cpu'

    logger.debug("Creating a MockConfigManager instance.")
    return MockConfigManager()


def test_mock_config_manager(mock_config_manager):
    """
    Test that the mock configuration manager correctly returns 'cpu' as the device.
    """
    logger.debug("Running test_mock_config_manager.")
    config = mock_config_manager
    # Assert that the configuration returns the expected torch device.
    assert config.get_torch_device() == 'cpu'
    logger.debug("test_mock_config_manager passed.")


def test_mock_cache_manager(mock_cache_manager):
    """
    Test that the CacheManager instance can set, get, and clear cache entries properly.
    """
    logger.debug("Running test_mock_cache_manager.")
    cache = mock_cache_manager
    # Set a key-value pair.
    cache.set("test_key", "test_value")
    logger.debug("Cache key 'test_key' set to 'test_value'.")
    # Assert that the value can be retrieved.
    assert cache.get("test_key") == "test_value", "Expected 'test_value' for key 'test_key'."
    logger.debug("Cache retrieval for 'test_key' returned the expected value.")

    # Clear the cache.
    cache.clear_cache()
    logger.debug("Cache cleared; verifying that 'test_key' no longer exists.")
    # Assert that the key is now missing.
    assert cache.get("test_key") is None, "Expected None for key 'test_key' after clearing cache."
    logger.debug("test_mock_cache_manager passed.")


if __name__ == '__main__':
    # Start method: run the tests if this file is executed directly.
    # This allows running the tests manually with: python test_util_config_manager.py
    pytest.main()