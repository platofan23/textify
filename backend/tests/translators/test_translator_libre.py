import logging
import pytest
from unittest.mock import patch, MagicMock
from backend.app.translators.translator_libre import LibreTranslateTranslator
from backend.app.utils import CacheManager

# Configure logging to capture DEBUG, WARNING, and ERROR messages.
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@pytest.fixture
def mock_config_manager():
    """
    Fixture that returns a mock configuration manager.
    The manager returns a preset Libre Translate URL and headers.
    """

    class MockConfigManager:
        def get_libre_translate_url(self):
            logger.debug("MockConfigManager: Returning mock Libre Translate URL.")
            return 'http://mock-api/translate'

        def get_libre_translate_headers(self):
            logger.debug("MockConfigManager: Returning mock Libre Translate headers.")
            return {"Content-Type": "application/json"}

    logger.debug("Creating a MockConfigManager instance.")
    return MockConfigManager()


@pytest.fixture
def mock_cache_manager():
    """
    Fixture that returns a CacheManager instance with a maximum size of 100.
    """
    logger.debug("Creating CacheManager instance with maxsize=100.")
    return CacheManager(maxsize=100)


def test_translate_text_libre(mock_config_manager, mock_cache_manager):
    """
    Test that the LibreTranslateTranslator correctly translates text using a
    mocked requests.post call and stores the result in the cache.
    """
    logger.debug("Starting test_translate_text_libre.")

    # Patch the 'requests.post' method used by the translator.
    with patch("requests.post") as mock_post:
        # Arrange: Set up the mock response for the HTTP POST request.
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"translatedText": "Hola"}
        mock_post.return_value = mock_response
        logger.debug("Mocked requests.post is configured to return 'Hola' in its JSON response.")

        # Create the LibreTranslateTranslator using the mocked config and cache manager.
        translator = LibreTranslateTranslator(
            'en', 'es', "",
            mock_cache_manager,
            mock_config_manager.get_libre_translate_url(),
            mock_config_manager.get_libre_translate_headers()
        )
        logger.debug("LibreTranslateTranslator instance created.")

        # Act: Perform the translation.
        result = translator.translate("Hello")
        logger.debug("Translation result obtained: %s", result)

        # Assert: Validate the translation result and that the result is cached.
        assert result == ["Hola"], "Expected translation result to be ['Hola']."
        logger.debug("Translation result assertion passed.")

        # Assert that the cache contains the translated text under the key "Libre-Hello".
        assert mock_cache_manager.get("Libre-Hello") == "Hola", "Expected cache to store 'Hola' for key 'Libre-Hello'."
        logger.debug("Cache assertion passed.")


if __name__ == '__main__':
    # Start method: Run the tests if this file is executed directly.
    import pytest

    pytest.main()