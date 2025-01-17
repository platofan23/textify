import os
import pickle

from cachetools import LRUCache
from backend.app.utils.util_logger import Logger  # Importiere die Logger-Klasse

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
        """
        Creates or returns the singleton instance of CacheManager.

        Args:
            cache_file (str): Path to the cache file for persistence.
            maxsize (int): Maximum number of items to store in the cache.
            clear_cache_on_start (bool): If True, clears the cache at startup.

        Returns:
            CacheManager: Singleton instance of CacheManager.
        """
        if cls._instance is None:
            cls._instance = super(CacheManager, cls).__new__(cls)
            cls._instance._initialize(cache_file, maxsize, clear_cache_on_start)
        return cls._instance

    def _initialize(self, cache_file, maxsize, clear_cache_on_start):
        """
        Initializes the cache and handles optional cache clearing on start.

        Args:
            cache_file (str): Path to the cache file.
            maxsize (int): Maximum cache size.
            clear_cache_on_start (bool): Clears the cache if True.
        """
        self.cache = LRUCache(maxsize=maxsize)
        self.cache_file = cache_file

        if clear_cache_on_start and os.path.exists(self.cache_file):
            os.remove(self.cache_file)
            Logger.info(f"Cache file {self.cache_file} cleared on start.")
        else:
            self._load_cache()

    def get(self, key):
        """
        Retrieves a value from the cache.

        Args:
            key (str): The key to look up in the cache.

        Returns:
            Any: The cached value, or None if the key is not found.
        """
        value = self.cache.get(key)
        if value:
            Logger.debug(f"Cache hit for key: {key}")
        else:
            Logger.debug(f"Cache miss for key: {key}")
        return value

    def set(self, key, value):
        """
        Stores a key-value pair in the cache and persists the cache to file.

        Args:
            key (str): The key for the cache entry.
            value (Any): The value to cache.
        """
        self.cache[key] = value
        self._save_cache()
        Logger.info(f"Cache set for key: {key}")

    def clear_cache(self):
        """
        Clears all entries from the in-memory cache.
        """
        self.cache.clear()
        Logger.info("[CACHE CLEARED] In-memory cache cleared.")

    def _load_cache(self):
        """
        Loads the cache from the cache file, if it exists.

        Raises:
            Exception: If loading the cache fails.
        """
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, "rb") as f:
                    self.cache = pickle.load(f)
                Logger.info(f"[CACHE LOADED] Cache loaded from {self.cache_file}")
            except Exception as e:
                Logger.error(f"[CACHE ERROR] Failed to load cache: {e}")

    def _save_cache(self):
        """
        Saves the current state of the cache to the cache file.

        Raises:
            Exception: If saving the cache fails.
        """
        try:
            with open(self.cache_file, "wb") as f:
                pickle.dump(self.cache, f)
            Logger.info(f"[CACHE SAVED] Cache saved to {self.cache_file}")
        except Exception as e:
            Logger.error(f"[CACHE ERROR] Failed to save cache: {e}")
