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

        Args:
            model_name (str): The TTS model to load.

        Returns:
            TTS: Loaded TTS model instance.
        """
        if model_name in self.loaded_models:
            Logger.info(f"✅ Using cached model: {model_name}")
            return self.loaded_models[model_name]

        Logger.info(f"⚠️ Loading model: {model_name}...")
        try:
            model = TTS(model_name=model_name)
            model.to(self.device)
            self.loaded_models[model_name] = model  # Cache model in memory
            Logger.info(f"✅ Model '{model_name}' loaded successfully.")
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

            # Dynamically load the correct model
            tts = self.get_model(model)

            # Create a temporary file for output
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmpfile:
                temp_filename = tmpfile.name

            # Generate speech
            tts.tts_to_file(
                text=text,
                file_path=temp_filename,
                speaker=speaker,
                language=language
            )

            # Load generated audio into memory
            with open(temp_filename, "rb") as f:
                audio_buffer = BytesIO(f.read())

            # Clean up temp file
            os.remove(temp_filename)

            Logger.info("✅ Audio synthesis completed successfully.")
            audio_buffer.seek(0)
            return audio_buffer
        except Exception as e:
            Logger.error(f"❌ Error during synthesis: {str(e)}")
            raise
