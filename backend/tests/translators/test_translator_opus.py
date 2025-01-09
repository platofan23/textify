from unittest.mock import patch, MagicMock
from backend.app.translators.translator_opus import OpusMTTranslator
import pytest
from backend.app.utils import CacheManager

@pytest.fixture
def mock_cache_manager():
    return CacheManager(maxsize=1000, clear_cache_on_start=True)


from unittest.mock import patch, MagicMock
from backend.app.translators.translator_opus import OpusMTTranslator


def test_translate_text_opus(mock_cache_manager):
    with patch("backend.app.translators.translator_opus.MarianMTModel") as mock_model, \
            patch("backend.app.translators.translator_opus.MarianTokenizer") as mock_tokenizer, \
            patch.object(mock_cache_manager, 'get', return_value=None) as mock_cache_get:
        # Setup Mocks
        mock_tokenizer.from_pretrained.return_value = mock_tokenizer
        mock_model.from_pretrained.return_value = mock_model
        mock_model.generate.return_value = ["Translated Text"]
        mock_tokenizer.batch_decode.return_value = ["Translated Text"]

        # Cache immer zurücksetzen, um alte Werte zu vermeiden
        mock_cache_manager.clear_cache()

        # Initialisiere den Übersetzer
        translator = OpusMTTranslator('en', 'de', mock_cache_manager, 'cpu')

        # Übersetzen
        result = translator.translate("Hello")

        # Verifiziere das Ergebnis
        assert result == ["Translated Text"]

