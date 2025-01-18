import logging
from backend.app.utils import CacheManager

# Configure logging to capture DEBUG, WARNING, and ERROR messages.
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def test_cache_operations():
    """
    Test basic cache operations of CacheManager:
    - Setting a cache value,
    - Retrieving that value,
    - And clearing the cache.
    """
    logger.debug("Starting test_cache_operations.")

    # Create a CacheManager instance with a maximum size of 10.
    cache_manager = CacheManager(maxsize=10)

    # Set a cache entry for key "key1" with value "value1".
    logger.debug("Setting cache key 'key1' to 'value1'.")
    cache_manager.set("key1", "value1")

    # Retrieve the value for "key1" and log the result.
    retrieved_value = cache_manager.get("key1")
    logger.debug("Retrieved value for 'key1': %s", retrieved_value)

    # Assert that the retrieved value matches what was set.
    assert retrieved_value == "value1", "Cache did not return the expected value 'value1' for key 'key1'."

    # Clear the cache.
    logger.debug("Clearing the cache.")
    cache_manager.clear_cache()

    # After clearing the cache, retrieving "key1" should return None.
    retrieved_after_clear = cache_manager.get("key1")
    logger.debug("Retrieved value for 'key1' after clearing cache: %s", retrieved_after_clear)
    assert retrieved_after_clear is None, "Expected None after clearing cache, but a value was returned."

    logger.debug("test_cache_operations completed successfully.")


if __name__ == '__main__':
    # Start method: run the tests if this file is executed directly.
    # This allows running the tests manually using: python test_util_cache_manager.py
    import pytest

    pytest.main()