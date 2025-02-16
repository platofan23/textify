import os
import pickle
from cachetools import LRUCache
from backend.app.utils.util_logger import Logger  # Import the Logger class


class CacheManager:
    """
    CacheManager handles in-memory caching with persistent storage.

    This class implements a singleton pattern to ensure only one instance of the cache exists.
    It uses an LRU (Least Recently Used) cache and can persist cached data to a file using pickle.

    Attributes:
        _instance (CacheManager): Singleton instance of the CacheManager.
        cache (LRUCache): In-memory cache with a maximum size limit.
        cache_file (str): Path to the file where the cache is persisted.
    """
    _instance = None  # Singleton instance

    def __new__(cls, cache_file="cache.pkl", maxsize=1000, clear_cache_on_start=False):
        if cls._instance is None:
            cls._instance = super(CacheManager, cls).__new__(cls)
            cls._instance._initialize(cache_file, maxsize, clear_cache_on_start)
        return cls._instance

    def _initialize(self, cache_file, maxsize, clear_cache_on_start):
        self.cache = LRUCache(maxsize=maxsize)
        self.cache_file = cache_file

        if clear_cache_on_start and os.path.exists(self.cache_file):
            os.remove(self.cache_file)
            Logger.info(f"[CACHE] Cleared cache file {self.cache_file} on start.")
        else:
            self._load_cache()

    def is_available(self):
        """
        Checks if the cache is functioning properly by performing a read/write test.
        Returns True if the cache works correctly, False otherwise.
        """
        try:
            test_key = "healthcheck_test"
            test_value = "test_value"

            # Write to cache
            self.set(test_key, test_value)

            # Read from cache
            cached_value = self.get(test_key)

            # Clean up test entry
            self.delete(test_key)

            # If the value matches, the cache is available
            result = cached_value == test_value
            Logger.info(f"[CACHE HEALTH] Availability check passed: {result}")
            return result
        except Exception as e:
            Logger.error(f"[CACHE ERROR] Availability check failed: {e}")
            return False

    def get(self, key):
        """Retrieves a value from the cache."""
        value = self.cache.get(key)
        if value is not None:
            Logger.info(f"[CACHE] Hit for key: {key}")
        else:
            Logger.info(f"[CACHE] Miss for key: {key}")
        return value

    def set(self, key, value):
        """Stores a key-value pair in the cache and attempts to persist it."""
        self.cache[key] = value
        Logger.info(f"[CACHE] Set key: {key}")
        self._save_cache()

    def delete(self, key):
        """Removes a key from the cache."""
        if key in self.cache:
            del self.cache[key]
            Logger.info(f"[CACHE] Deleted key: {key}")

    def clear_cache(self):
        """Clears all cache entries."""
        self.cache.clear()
        Logger.info("[CACHE CLEARED] In-memory cache cleared.")

    def _load_cache(self):
        """Loads the cache from the cache file, ensuring only serializable values are used."""
        if not os.path.exists(self.cache_file):
            Logger.info(f"[CACHE] No cache file found at {self.cache_file}, starting fresh.")
            return

        try:
            with open(self.cache_file, "rb") as f:
                cached_data = pickle.load(f)
                valid_data = {k: v for k, v in cached_data.items() if self._is_serializable(v)}

                self.cache.update(valid_data)
                Logger.info(f"[CACHE LOADED] Loaded {len(valid_data)} valid entries from {self.cache_file}.")
        except Exception as e:
            Logger.error(f"[CACHE ERROR] Failed to load cache: {e}")

    def _save_cache(self):
        """Saves only serializable cache entries to prevent issues with non-pickleable objects."""
        try:
            serializable_cache = {k: v for k, v in self.cache.items() if self._is_serializable(v)}
            with open(self.cache_file, "wb") as f:
                pickle.dump(serializable_cache, f)

            Logger.info(f"[CACHE SAVED] Successfully saved {len(serializable_cache)} serializable entries to {self.cache_file}.")
        except Exception as e:
            Logger.error(f"[CACHE ERROR] Failed to save cache: {e}")

    @staticmethod
    def _is_serializable(obj):
        """Checks if an object can be pickled."""
        try:
            pickle.dumps(obj)
            return True
        except (pickle.PickleError, AttributeError, TypeError):
            return False
