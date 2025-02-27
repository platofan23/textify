import tempfile
import os
from io import BytesIO
from TTS.api import TTS
from backend.app.utils.util_logger import Logger

class TTSSynthesizer:
    """
    Synthesizes text into speech using the Coqui TTS library with GPU support.
    """

    def __init__(self, config_manager, cache_manager):
        """
        Initializes the TTS synthesizer with caching support.

        Args:
            config_manager (ConfigManager): Configuration manager instance.
            cache_manager (CacheManager): Cache manager instance.
        """
        self.config_manager = config_manager
        self.cache_manager = cache_manager
        self.device = "cuda" if self.config_manager.get_torch_device() == "cuda" else "cpu"

        # Dictionary to store loaded models in memory
        self.loaded_models = {}

    def get_model(self, model_name):
        """
        Loads a model if not already cached.
        """
        if model_name in self.loaded_models:
            Logger.info(f"✅ Using cached model from memory: {model_name}")
            return self.loaded_models[model_name]

        Logger.info(f"⚠️ Checking if model '{model_name}' is cached...")
        try:
            Logger.info(f"🛠️ [CACHE DEBUG] Checking cache for model: tts_model-{model_name}")
            cached_model = self.cache_manager.load_cached_tts_model(model_name)
            if cached_model:
                Logger.info(f"✅ Loaded '{model_name}' from cache.")
                return cached_model
            else:
                Logger.info(f"🔍 Model '{model_name}' not found in cache, loading fresh...")
                model = TTS(model_name)
                model.to(self.device)
                self.cache_manager.cache_tts_model(model_name, model)
                Logger.info(f"✅ Model '{model_name}' loaded and cached successfully.")
                return model
        except Exception as e:
            Logger.error(f"❌ Failed to load model '{model_name}': {str(e)}")
            raise

    def synthesize(self, text, model, speaker=None, language=None):
        """
        Synthesizes the given text into a WAV file in memory.

        Args:
            text (str): The text to synthesize.
            model (str): The TTS model to use.
            speaker (str, optional): The speaker voice to use (if applicable).
            language (str, optional): The language to use.

        Returns:
            BytesIO: In-memory WAV file.
        """
        try:
            Logger.info(f"🔊 Synthesizing text using model='{model}', speaker='{speaker}', language='{language}'...")
            tts = self.get_model(model)

            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmpfile:
                temp_filename = tmpfile.name

            tts.tts_to_file(
                text=text,
                file_path=temp_filename,
                speaker=speaker,
                language=language
            )

            with open(temp_filename, "rb") as f:
                audio_buffer = BytesIO(f.read())
            os.remove(temp_filename)

            Logger.info("✅ Audio synthesis completed successfully.")
            audio_buffer.seek(0)
            return audio_buffer
        except Exception as e:
            Logger.error(f"❌ Error during synthesis: {str(e)}")
            raise