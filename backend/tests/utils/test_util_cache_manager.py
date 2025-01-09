### tests/test_utils/test_util_cache_manager.py ###
from backend.app.utils import CacheManager

def test_cache_operations():
    cache_manager = CacheManager(maxsize=10)
    cache_manager.set("key1", "value1")
    assert cache_manager.get("key1") == "value1"

    cache_manager.clear_cache()
    assert cache_manager.get("key1") is None