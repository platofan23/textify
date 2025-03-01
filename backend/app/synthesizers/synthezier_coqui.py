import torch
from io import BytesIO
from TTS.api import TTS
import soundfile as sf
import numpy as np

from backend.app.utils.util_logger import Logger
import wave

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
        self.dont_spam_model = False
        self.config_manager = config_manager
        self.cache_manager = cache_manager
        self.device = "cuda" if self.config_manager.get_torch_device() == "cuda" else "cpu"

    def get_model(self, model_name):
        """
        Loads a TTS model from RAM cache if available, otherwise loads and caches it.
        """
        cached_model = self.cache_manager.load_cached_tts_model(model_name)

        if cached_model:
            if not self.dont_spam_model:
                self.dont_spam_model = True
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

    def synthesize(self, text: str, model, speaker=None, language=None):
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
            # Dynamically load the correct model
            tts = self.get_model(model)

            # Use `.tts()` to generate raw audio samples
            with torch.no_grad():
                audio_array = tts.tts(text=text_sentence, speaker=speaker, language=language)

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


