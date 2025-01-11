import pytest
from unittest.mock import patch
from backend.app.utils import CacheManager
from backend.app.translators.translator_opus import OpusMTTranslator


@pytest.fixture
def mock_cache_manager():
    """
    Fixture for initializing a CacheManager instance for testing.
    """
    return CacheManager(maxsize=1000, clear_cache_on_start=True)


def test_translate_text_opus(mock_cache_manager):
    """
    Tests the OpusMTTranslator using mocks for MarianMTModel and MarianTokenizer.
    """
    with patch("backend.app.translators.translator_opus.MarianMTModel") as mock_model, \
            patch("backend.app.translators.translator_opus.MarianTokenizer") as mock_tokenizer, \
            patch.object(mock_cache_manager, 'get', return_value=None) as mock_cache_get:
        # Setup Mocks
        mock_tokenizer.from_pretrained.return_value = mock_tokenizer
        mock_model.from_pretrained.return_value = mock_model
        mock_model.generate.return_value = ["Translated Text"]
        mock_tokenizer.batch_decode.return_value = ["Translated Text"]

        # Clear cache to avoid stale values
        mock_cache_manager.clear_cache()

        # Initialize translator
        translator = OpusMTTranslator('en', 'de', mock_cache_manager, 'cpu')

        # Translate text
        result = translator.translate("Hello")

        # Verify the result
        assert result == ["Translated Text"]
