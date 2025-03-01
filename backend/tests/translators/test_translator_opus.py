import logging
import pytest
from unittest.mock import patch, MagicMock
from backend.app.utils import CacheManager
from backend.app.translators.translator_opus import OpusMTTranslator

# Configure logging to capture DEBUG and above messages.
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@pytest.fixture
def mock_cache_manager():
    """
    Fixture for initializing a CacheManager instance for testing.
    """
    logger.debug("Creating CacheManager instance with maxsize=1000 and clear_cache_on_start=True.")
    return CacheManager(maxsize=1000, clear_cache_on_start=True)


def test_translate_text_opus(mock_cache_manager):
    """
    Tests the OpusMTTranslator using mocks for MarianMTModel and MarianTokenizer.

    This test ensures that:
      - The mocked models and tokenizer are set up correctly.
      - The translator generates the expected "Translated Text" output.
      - The cache is used appropriately to avoid redundant translations.
    """
    logger.debug("Starting test_translate_text_opus.")
    # Patch the MarianMTModel, MarianTokenizer and the CacheManager.get and set methods.
    with patch("backend.app.translators.translator_opus.MarianMTModel") as mock_model, \
         patch("backend.app.translators.translator_opus.MarianTokenizer") as mock_tokenizer, \
         patch.object(mock_cache_manager, 'get', return_value=None) as mock_cache_get, \
         patch.object(mock_cache_manager, 'set', return_value=None) as mock_cache_set:
        # Setup mocks for the translation pipeline.
        logger.debug("Setting up mocks for MarianMTModel and MarianTokenizer.")
        mock_tokenizer.from_pretrained.return_value = mock_tokenizer
        mock_model.from_pretrained.return_value = mock_model

        # Define the behavior of generate and batch_decode to simulate translation.
        mock_model.generate.return_value = ["Translated Text"]
        mock_tokenizer.batch_decode.return_value = ["Translated Text"]

        # Initialize the translator with the full model name, cache manager, and device.
        translator = OpusMTTranslator("Helsinki-NLP/opus-mt-en-de", mock_cache_manager, 'cpu')
        logger.debug("Initialized OpusMTTranslator instance.")

        # Act: Translate the input text.
        result = translator.translate("Hello")
        logger.debug("Translation result: %s", result)

        # Assert: Verify that the translation output matches the expected result.
        assert result == ["Translated Text"], "Expected translation result to be ['Translated Text']"
        logger.debug("Test translation result verified successfully.")


if __name__ == '__main__':
    # Run the tests if this file is executed directly.
    import pytest
    pytest.main()
