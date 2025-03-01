import tempfile
import os
from io import BytesIO
from TTS.api import TTS
from backend.app.utils.util_logger import Logger
import wave

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
        self.dont_spam_model = False
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
            if not self.dont_spam_model:
                Logger.info(f"✅ Using cached model: {model_name}")
                self.dont_spam_model = True
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

    def synthesize(self, text: str, model, speaker=None, language=None):
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

            Logger.info("Audio synthesis running")
            # Make text chunks
            char_count = 0
            audio_buffers = []
            last_punctuation_mark = 0
            i = 0
            while len(text) > i:
                char_count += 1
                if text[i] in [".", "!", "?"]:
                    last_punctuation_mark = char_count
                if char_count >= 252:
                    if last_punctuation_mark == 0:
                        i += 1
                        continue
                    audio_buffers.append(self._tts_for_synthesize(text[:last_punctuation_mark], model, speaker, language))
                    Logger.info(f" {i/len(text)}% of the text has been synthesized.")
                    text = text[last_punctuation_mark:]
                    char_count = 0
                    i = 0
                    last_punctuation_mark = 0
                    continue
                i += 1


            Logger.info("✅ Audio synthesis completed successfully.")


            # Combine all audio buffers into one
            combined_audio = BytesIO()
            with wave.open(combined_audio, 'wb') as combined_wave:
                for buffer in audio_buffers:
                    with wave.open(buffer, 'rb') as wave_file:
                        if combined_wave.getnframes() == 0:
                            combined_wave.setparams(wave_file.getparams())
                        combined_wave.writeframes(wave_file.readframes(wave_file.getnframes()))
            combined_audio.seek(0)
            return combined_audio

        except Exception as e:
            Logger.error(f"❌ Error during synthesis: {str(e)}")
            raise


    def _tts_for_synthesize(self, text_sentence: str, model, speaker=None, language=None):
        """
        Synthesizes the given text into a WAV file in memory.

        Args:
            text_sentence (str): The text to synthesize.
            model (str): The TTS model to use.
            speaker (str, optional): The speaker voice to use (if applicable).
            language (str, optional): The language to use.

        Returns:
            BytesIO: In-memory WAV file.
        """
        try:
            # Create a temporary files for output
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmpfile:
                temp_filename = tmpfile.name

            # Dynamically load the correct model
            tts = self.get_model(model)

            # Generate speech
            tts.tts_to_file(
                text=text_sentence,
                file_path=temp_filename,
                speaker=speaker,
                language=language
            )

            # Load generated audio into memory
            with open(temp_filename, "rb") as f:
                audio_buffer = BytesIO(f.read())

            # Clean up temp file
            os.remove(temp_filename)


            audio_buffer.seek(0)
            return audio_buffer

        except Exception as e:
            Logger.error(f"❌ Error during synthesis: {str(e)}")
            raise
