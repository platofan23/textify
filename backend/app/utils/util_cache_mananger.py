import os
import pickle
from cachetools import LRUCache
from backend.app.utils.util_logger import Logger  # Import the Logger class

class CacheManager:
    _instance = None  # Singleton instance

    def __new__(cls, cache_file="cache.pkl", maxsize=1000, clear_cache_on_start=False):
        if cls._instance is None:
            cls._instance = super(CacheManager, cls).__new__(cls)
            cls._instance._initialize(cache_file, maxsize, clear_cache_on_start)
        return cls._instance

    def _initialize(self, cache_file, maxsize, clear_cache_on_start):
        """
        Initialize the persistent cache and in-memory caches for models.
        Args:
            cache_file (str): File path for persistent cache storage.
            maxsize (int): Maximum number of items for the LRU cache.
            clear_cache_on_start (bool): If True, clear the cache file on startup.
        """
        self.cache = LRUCache(maxsize=maxsize)
        self.tts_in_memory_cache = {}  # In-memory cache for TTS models
        self.stt_in_memory_cache = {}  # In-memory cache for STT models
        self.cache_file = cache_file

        if clear_cache_on_start and os.path.exists(self.cache_file):
            os.remove(self.cache_file)
            Logger.info(f"[CACHE] Cleared persistent cache file {self.cache_file} on startup.")
        else:
            self._load_cache()

    def is_available(self):
        """Check if the persistent cache is available."""
        return self.cache is not None

    # General Persistent Cache Methods
    def get(self, key):
        """Retrieve a value from the persistent cache."""
        return self.cache.get(key)

    def set(self, key, value):
        """Store a key-value pair in the persistent cache and persist it."""
        self.cache[key] = value
        self._save_cache()

    def _load_cache(self):
        """Load only pickleable items from the persistent cache file."""
        if not os.path.exists(self.cache_file):
            return
        try:
            with open(self.cache_file, "rb") as f:
                self.cache.update(pickle.load(f))
        except Exception as e:
            Logger.error(f"[CACHE ERROR] Failed to load cache: {e}")

    def _save_cache(self):
        """Persist only pickleable cache items to the cache file."""
        try:
            cache_to_save = {}
            for key, value in self.cache.items():
                if key.startswith("tts_model-") or key.startswith("stt_model-"):
                    continue  # Skip model objects
                try:
                    pickle.dumps(value)
                    cache_to_save[key] = value
                except Exception:
                    Logger.warning(f"[CACHE] Skipping non-pickleable item: '{key}'")
            with open(self.cache_file, "wb") as f:
                pickle.dump(cache_to_save, f)
        except Exception as e:
            Logger.error(f"[CACHE ERROR] Failed to save cache: {e}")

    # In-Memory Cache Methods for TTS models
    def load_cached_tts_model(self, model_name: str):
        """Retrieve the TTS model exclusively from the in-memory cache."""
        cache_key = f"tts_model-{model_name}"
        model = self.tts_in_memory_cache.get(cache_key)
        if model is not None:
            Logger.info(f"[CACHE] TTS model '{model_name}' retrieved from RAM cache.")
        else:
            Logger.info(f"[CACHE] No cached TTS model found for '{model_name}'.")
        return model

    def cache_tts_model(self, model_name: str, tts_model):
        """Store the TTS model exclusively in the in-memory cache."""
        cache_key = f"tts_model-{model_name}"
        if cache_key in self.tts_in_memory_cache:
            Logger.info(f"[CACHE] TTS model '{model_name}' is already cached in RAM.")
            return
        self.tts_in_memory_cache[cache_key] = tts_model
        Logger.info(f"[CACHE] TTS model '{model_name}' successfully stored in RAM.")

    # In-Memory Cache Methods for STT models
    def load_cached_stt_model(self, model_name: str):
        """Retrieve the STT model exclusively from the in-memory cache."""
        cache_key = f"stt_model-{model_name}"
        model = self.stt_in_memory_cache.get(cache_key)
        if model is not None:
            Logger.info(f"[CACHE] STT model '{model_name}' retrieved from RAM cache.")
        else:
            Logger.info(f"[CACHE] No cached STT model found for '{model_name}'.")
        return model

    def cache_stt_model(self, model_name: str, stt_model):
        """Store the STT model exclusively in the in-memory cache."""
        cache_key = f"stt_model-{model_name}"
        if cache_key in self.stt_in_memory_cache:
            Logger.info(f"[CACHE] STT model '{model_name}' is already cached in RAM.")
            return
        self.stt_in_memory_cache[cache_key] = stt_model
        Logger.info(f"[CACHE] STT model '{model_name}' successfully stored in RAM.")

    def clear_cache(self):
        """Clear both the persistent cache and the in-memory model caches."""
        self.cache.clear()
        self.tts_in_memory_cache.clear()
        self.stt_in_memory_cache.clear()
        Logger.info("[CACHE] All caches have been cleared.")