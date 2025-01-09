### tests/test_translators/test_translator_libre.py ###
import pytest
from unittest.mock import patch, MagicMock
from backend.app.translators.translator_libre import LibreTranslateTranslator
from backend.app.utils import CacheManager

@pytest.fixture
def mock_config_manager():
    class MockConfigManager:
        def get_libre_translate_url(self):
            return 'http://mock-api/translate'
        def get_libre_translate_headers(self):
            return {"Content-Type": "application/json"}
    return MockConfigManager()

@pytest.fixture
def mock_cache_manager():
    return CacheManager(maxsize=100)


def test_translate_text_libre(mock_config_manager, mock_cache_manager):
    with patch("requests.post") as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"translatedText": "Hola"}
        mock_post.return_value = mock_response

        translator = LibreTranslateTranslator('en', 'es', mock_cache_manager,
                                             mock_config_manager.get_libre_translate_url(),
                                             mock_config_manager.get_libre_translate_headers())

        result = translator.translate("Hello")

        assert result == ["Hola"]
        assert mock_cache_manager.get("Libre-Hello") == "Hola"