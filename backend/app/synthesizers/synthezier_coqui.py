import torch
from io import BytesIO
from TTS.api import TTS
import soundfile as sf
import numpy as np

from backend.app.utils.util_logger import Logger

class TTSSynthesizer:
    """
    Synthesizes text into speech using the Coqui TTS library with RAM caching support.
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

    def get_model(self, model_name):
        """
        Loads a TTS model from RAM cache if available, otherwise loads and caches it.
        """
        cached_model = self.cache_manager.load_cached_tts_model(model_name)

        if cached_model:
            Logger.info(f" [CACHE] Using preloaded TTS model from RAM: {model_name}")
            return cached_model

        # Only show the warning **once** (instead of repeating it twice)
        Logger.warning(f"⚠️ [CACHE] No cached TTS model found for '{model_name}', loading fresh...")

        model = TTS(model_name)
        model.to(self.device)

        # Store in RAM cache
        self.cache_manager.cache_tts_model(model_name, model)
        Logger.info(f"[CACHE] Model '{model_name}' successfully stored in RAM.")

        return model

    def synthesize(self, text, model, speaker=None, language=None):
        """
        Synthesizes text into speech directly in memory (optimized for speed).

        Args:
            text (str): The text to synthesize.
            model (str): The TTS model to use.
            speaker (str, optional): The speaker voice to use (if applicable).
            language (str, optional): The language to use.

        Returns:
            BytesIO: In-memory WAV file (RAM-optimized, no temp files).
        """
        try:
            Logger.info(f"Synthesizing text with model='{model}', speaker='{speaker}', language='{language}'...")

            # Load cached model or from memory
            tts = self.get_model(model)

            # Use `.tts()` to generate raw audio samples
            with torch.no_grad():
                audio_array = tts.tts(text=text, speaker=speaker, language=language)

            # convert NumPy array to WAV format (RAM-optimized)
            audio_buffer = BytesIO()
            sf.write(audio_buffer, np.array(audio_array), samplerate=22050, format='WAV')  # Adjust sample rate if needed

            # Ensure buffer is ready to read
            audio_buffer.seek(0)
            Logger.info(" Audio synthesis completed successfully (RAM-optimized).")

            return audio_buffer
        except Exception as e:
            Logger.error(f"Error during synthesis: {str(e)}")
            raise


