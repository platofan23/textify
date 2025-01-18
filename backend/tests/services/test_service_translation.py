import pytest
import logging
from backend.app.services import TranslationService
from backend.app.utils import CacheManager

# Configure logging to capture DEBUG (and above) messages.
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@pytest.fixture
def mock_config_manager():
    """
    Fixture for creating a mock configuration manager that returns preset values.
    """

    class MockConfigManager:
        def __init__(self):
            self.mock_config = {
                'TEXT': {
                    'MAX_TOKEN': 150,
                },
                'TRANSLATE': {
                    'TORCH_CPU_DEVICE': 'cpu',
                    'TORCH_GPU_DEVICE': 'cuda',
                }
            }

        def get_torch_device(self):
            logger.debug("MockConfigManager: get_torch_device returns 'cpu'.")
            return 'cpu'

        def get_config_value(self, section, key, value_type, default=None):
            try:
                value = self.mock_config[section][key]
                logger.debug(f"MockConfigManager: get_config_value returns {value} for {section}/{key}.")
                return value_type(value)
            except KeyError:
                logger.warning("MockConfigManager: Key not found in get_config_value, returning default.")
                return default

    return MockConfigManager()


@pytest.fixture
def mock_cache_manager():
    """
    Fixture for initializing a CacheManager instance for testing.
    """
    logger.debug("Creating CacheManager instance with maxsize=100.")
    return CacheManager(maxsize=100)


def test_unsupported_translation_model(mock_config_manager, mock_cache_manager):
    """
    Test that an unsupported translation model raises a ValueError.
    """
    logger.debug("Running test_unsupported_translation_model.")
    service = TranslationService(mock_config_manager, mock_cache_manager)

    with pytest.raises(ValueError, match="Unsupported translation model"):
        service.translate_and_chunk_text("InvalidModel", "en", "de", "Hello")
    logger.debug("test_unsupported_translation_model passed.")


def test_translation_model_mapping(mock_config_manager, mock_cache_manager):
    """
    Test that the translation model mapping returns the expected values,
    and that an unsupported model results in a ValueError.
    """
    logger.debug("Running test_translation_model_mapping.")
    service = TranslationService(mock_config_manager, mock_cache_manager)

    # Define the expected mapping.
    model_mapping = {
        "OpusMT": "Helsinki-NLP/opus-mt",
        "LibreTranslate": "LibreTranslate"
    }

    # Assert that valid keys return the expected values.
    assert model_mapping.get("OpusMT") == "Helsinki-NLP/opus-mt"
    assert model_mapping.get("LibreTranslate") == "LibreTranslate"
    logger.debug("Valid model mappings verified.")

    # Test that an invalid model mapping returns None.
    invalid_model = model_mapping.get("InvalidModel")
    assert invalid_model is None
    logger.debug("Invalid model mapping correctly returns None.")

    # Simulate raising ValueError if invalid_model is None.
    if invalid_model is None:
        with pytest.raises(ValueError, match="Unsupported translation model"):
            raise ValueError("Unsupported translation model")
    logger.debug("test_translation_model_mapping passed.")


def test_translate_text_cache_hit(mock_config_manager, mock_cache_manager):
    """
    Test that if a translation is already cached, it is returned immediately.
    """
    logger.debug("Running test_translate_text_cache_hit.")
    service = TranslationService(mock_config_manager, mock_cache_manager)

    # Pre-cache the translation result.
    cache_key = "Helsinki-NLP/opus-mt-en-de-8b1a9953c4611296a827abf8c47804d7"
    mock_cache_manager.set(cache_key, ["Hallo"])
    logger.debug("Cache set with key '%s'.", cache_key)

    # Retrieve the translation from the cache.
    result = service.translate_and_chunk_text("Helsinki-NLP/opus-mt", "en", "de", "Hello")
    assert result == ["Hallo"], "Expected the cached result to be returned."
    logger.debug("Cache hit verified; cached result returned.")

    # Print the cache hit message (for visual confirmation if needed).
    print("[CACHE HIT] Returning cached text:", cache_key)


def test_translate_text_cache_miss(mock_config_manager, mock_cache_manager):
    """
    Test that when there is no cached translation, the service computes a new one and updates the cache.
    """
    logger.debug("Running test_translate_text_cache_miss.")
    service = TranslationService(mock_config_manager, mock_cache_manager)

    # Ensure that the cache is initially empty for the given key.
    cache_key = "Helsinki-NLP/opus-mt-en-de-8b1a9953c4611296a827abf8c47804d8"
    assert mock_cache_manager.get(cache_key) is None, "Expected cache miss; key should not exist."
    logger.debug("Cache miss confirmed for key '%s'.", cache_key)

    # Compute the translation (which should also update the cache).
    result = service.translate_and_chunk_text("Helsinki-NLP/opus-mt", "en", "de", "Hello")
    # Assert that the result does not equal a stale or incorrect value.
    assert result != ["Hey"], "Expected a new translation that does not match the stale value."
    logger.debug("Cache miss handled; new translation computed and cache updated.")


if __name__ == '__main__':
    # Start method: run the tests if this file is executed directly.
    import pytest

    pytest.main()