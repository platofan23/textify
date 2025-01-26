import pytest
from unittest.mock import MagicMock
from backend.app.services.service_tts import TTSService


@pytest.fixture
def cache_manager():
    """
    Erstellt einen Mock für den CacheManager.
    """
    mock_cache = MagicMock()
    mock_cache.get.return_value = None  # Standardmäßig kein Treffer im Cache
    return mock_cache


@pytest.fixture
def config_manager():
    """
    Erstellt einen Mock für den ConfigManager.
    """
    mock_config = MagicMock()
    return mock_config


@pytest.fixture
def tts_service(cache_manager, config_manager):
    """
    Erstellt eine Instanz des TTSService.
    """
    return TTSService(config_manager=config_manager, cache_manager=cache_manager)


def test_tts_service_cache_hit(tts_service, cache_manager):
    """
    Testet, ob der TTSService einen Treffer aus dem Cache korrekt zurückgibt.
    """
    cache_manager.get.return_value = b"cached_audio"
    text = "Hello, world."

    result = tts_service.synthesize_audio(text, voice="default", language="en")

    assert result.getbuffer().nbytes == len(b"cached_audio"), "The returned audio should match the cached audio."
    cache_manager.get.assert_called_once()


def test_tts_service_cache_miss(tts_service, cache_manager):
    """
    Testet, ob der TTSService korrekt Audio erzeugt und in den Cache speichert, wenn kein Treffer vorliegt.
    """
    text = "This is a test."
    cache_manager.get.return_value = None  # Cache-Miss

    result = tts_service.synthesize_audio(text, voice="default", language="en")

    assert result.getbuffer().nbytes > 0, "The returned audio buffer should not be empty."
    cache_manager.set.assert_called_once()


def test_tts_service_invalid_text(tts_service):
    """
    Testet, ob der TTSService bei leerem Text einen Fehler auslöst.
    """
    text = ""
    with pytest.raises(ValueError, match="Text cannot be empty or whitespace only."):
        tts_service.synthesize_audio(text, voice="default", language="en")


def test_tts_service_caching_logic(tts_service, cache_manager):
    """
    Testet, ob der Cache korrekt gesetzt wird, wenn ein neuer Text verarbeitet wird.
    """
    text = "Caching test."
    cache_manager.get.return_value = None  # Kein Cache-Treffer

    result = tts_service.synthesize_audio(text, voice="default", language="en")

    # Sicherstellen, dass der Cache mit dem richtigen Schlüssel aktualisiert wurde
    cache_manager.set.assert_called_once()
    cache_key = cache_manager.set.call_args[0][0]  # Der erste Parameter von set() ist der Schlüssel
    assert "tts-default-en" in cache_key, "The cache key should include the correct prefix."

if __name__ == '__main__':
    # Start method: Run the tests if this file is executed directly.
    import pytest

    pytest.main()