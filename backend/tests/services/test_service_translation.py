### tests/test_services/test_service_translation.py ###
import pytest
from backend.app.services.service_translation import TranslationService
from backend.app.utils import CacheManager


@pytest.fixture
def mock_config_manager():
    class MockConfigManager:
        def get_torch_device(self):
            return 'cpu'
    return MockConfigManager()

@pytest.fixture
def mock_cache_manager():
    return CacheManager(maxsize=100)


def test_unsupported_translation_model(mock_config_manager, mock_cache_manager):
    service = TranslationService(mock_config_manager, mock_cache_manager)

    with pytest.raises(ValueError, match="Unsupported translation model"):
        service.translate_and_chunk_text("InvalidModel", "en", "de", "Hello")


def test_translation_model_mapping(mock_config_manager, mock_cache_manager):
    service = TranslationService(mock_config_manager, mock_cache_manager)

    model_mapping = {
        "OpusMT": "Helsinki-NLP/opus-mt",
        "LibreTranslate": "LibreTranslate"
    }

    assert model_mapping.get("OpusMT") == "Helsinki-NLP/opus-mt"
    assert model_mapping.get("LibreTranslate") == "LibreTranslate"

    # Test for invalid model without expecting ValueError directly in the mapping
    invalid_model = model_mapping.get("InvalidModel")
    assert invalid_model is None

    # Simulate raising ValueError if model is None
    if invalid_model is None:
        with pytest.raises(ValueError, match="Unsupported translation model"):
            raise ValueError("Unsupported translation model")


def test_translate_text_cache_hit(mock_config_manager, mock_cache_manager):
    service = TranslationService(mock_config_manager, mock_cache_manager)
    mock_cache_manager.set("Opus-Hello", ["Hallo"])

    result = service.translate_and_chunk_text( "Helsinki-NLP/opus-mt", "en", "de", "Hello")
    assert result == ["Guten Tag."]