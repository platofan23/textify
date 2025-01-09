### tests/conftest.py ###
import pytest
from backend.app.utils import CacheManager

@pytest.fixture
def mock_cache_manager():
    return CacheManager(maxsize=100)

@pytest.fixture
def mock_config_manager():
    class MockConfigManager:
        def get_torch_device(self):
            return 'cpu'
    return MockConfigManager()


def test_mock_config_manager(mock_config_manager):
    config = mock_config_manager
    assert config.get_torch_device() == 'cpu'


def test_mock_cache_manager(mock_cache_manager):
    cache = mock_cache_manager
    cache.set("test_key", "test_value")
    assert cache.get("test_key") == "test_value"
    cache.clear_cache()
    assert cache.get("test_key") is None
