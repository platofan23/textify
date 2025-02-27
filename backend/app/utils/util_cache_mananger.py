import os
import pickle
from cachetools import LRUCache
from backend.app.utils.util_logger import Logger  # Import the Logger class

class CacheManager:
    _instance = None  # Singleton instance
    CACHE_DIR = "cache/tts_models"

    def __new__(cls, cache_file="cache.pkl", maxsize=1000, clear_cache_on_start=False):
        if cls._instance is None:
            cls._instance = super(CacheManager, cls).__new__(cls)
            cls._instance._initialize(cache_file, maxsize, clear_cache_on_start)
        return cls._instance

    def _initialize(self, cache_file, maxsize, clear_cache_on_start):
        self.cache = LRUCache(maxsize=maxsize)
        self.tts_in_memory_cache = {}  # For non-pickleable TTS models
        self.cache_file = cache_file
        os.makedirs(self.CACHE_DIR, exist_ok=True)
        if clear_cache_on_start and os.path.exists(self.cache_file):
            os.remove(self.cache_file)
            Logger.info(f"[CACHE] Cleared cache file {self.cache_file} on start.")
        else:
            self._load_cache()

    def get(self, key):
        """Retrieves a value from the persistent cache."""
        return self.cache.get(key)

    def set(self, key, value):
        """Stores a key-value pair in the persistent cache and persists it."""
        self.cache[key] = value
        self._save_cache()

    def get_tts_model(self, key):
        """Retrieve a TTS model from the in-memory cache."""
        return self.tts_in_memory_cache.get(key)

    def set_tts_model(self, key, value):
        """Store a TTS model in the in-memory cache."""
        self.tts_in_memory_cache[key] = value

    def _load_cache(self):
        if not os.path.exists(self.cache_file):
            return
        try:
            with open(self.cache_file, "rb") as f:
                self.cache.update(pickle.load(f))
        except Exception as e:
            Logger.error(f"[CACHE ERROR] Failed to load cache: {e}")

    def _save_cache(self):
        try:
            cache_to_save = {}
            for key, value in self.cache.items():
                try:
                    pickle.dumps(value)
                    cache_to_save[key] = value
                except Exception as e:
                    Logger.warning(f"[CACHE] Item '{key}' is not pickleable and will not be persisted.")
            with open(self.cache_file, "wb") as f:
                pickle.dump(cache_to_save, f)
        except Exception as e:
            Logger.error(f"[CACHE ERROR] Failed to save cache: {e}")

    # Methods for caching TTS models exclusively in memory.
    def load_cached_tts_model(self, model_name: str):
        """
        Retrieves the TTS model solely from the in-memory cache.

        :param model_name: Name or path of the TTS model.
        :return: The cached TTS model or None if not found.
        """
        cache_key = f"tts_model-{model_name}"
        model = self.get_tts_model(cache_key)
        if model is not None:
            Logger.info(f"[CACHE] TTS model '{model_name}' successfully retrieved from in-memory cache.")
        return model

    def cache_tts_model(self, model_name: str, tts_model):
        """
        Stores the TTS model exclusively in the in-memory cache.

        :param model_name: Name or path of the TTS model.
        :param tts_model: The TTS model to be cached.
        """
        cache_key = f"tts_model-{model_name}"
        self.set_tts_model(cache_key, tts_model)
        Logger.info(f"[CACHE] TTS model '{model_name}' successfully stored in in-memory cache.")

    def clear_cache(self):
        """
        Clears both the persistent and in-memory caches.
        """
        self.cache.clear()
        self.tts_in_memory_cache.clear()
        Logger.info("[CACHE] All caches have been cleared.")
