import torch
from io import BytesIO
from TTS.api import TTS
import soundfile as sf
import numpy as np
import wave
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
        self.dont_spam_model = False
        self.config_manager = config_manager
        self.cache_manager = cache_manager
        self.device = "cuda" if self.config_manager.get_torch_device() == "cuda" else "cpu"

    def get_model(self, model_name):
        """
        Loads a TTS model from RAM cache if available, otherwise loads and caches it.

        Args:
            model_name (str): The name of the model to load.

        Returns:
            TTS: The loaded model instance.
        """
        cached_model = self.cache_manager.load_cached_tts_model(model_name)

        if cached_model:
            if not self.dont_spam_model:
                self.dont_spam_model = True
                Logger.info(f" [CACHE] Using preloaded TTS model from RAM: {model_name}")
            return cached_model

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

            # Chunking logic (ensures meaningful segments)
            text_segments = self._chunk_text(text)
            if not text_segments:
                raise ValueError("No valid text segments to synthesize.")

            audio_buffers = []
            for i, segment in enumerate(text_segments):
                buffer = self._tts_for_synthesize(segment, model, speaker, language)
                if buffer and buffer.getbuffer().nbytes > 0:
                    audio_buffers.append(buffer)
                else:
                    Logger.warning(f"❗ TTS returned an empty buffer for segment {i}: {segment}")

            if not audio_buffers:
                raise ValueError("❌ No valid audio buffers generated. TTS synthesis failed.")

            Logger.info("✅ Audio synthesis completed successfully.")

            # Merge all buffers into a single WAV file
            combined_audio = self._combine_audio_buffers(audio_buffers)
            return combined_audio

        except Exception as e:
            Logger.error(f"❌ Error during synthesis: {str(e)}")
            raise

    def _chunk_text(self, text):
        """
        Splits text into smaller segments for synthesis.

        Args:
            text (str): The full text to split.

        Returns:
            list: A list of segmented text chunks.
        """
        char_limit = 250
        segments = []
        current_segment = ""

        for word in text.split():
            if len(current_segment) + len(word) + 1 > char_limit:
                segments.append(current_segment.strip())
                current_segment = word
            else:
                current_segment += " " + word

        if current_segment.strip():
            segments.append(current_segment.strip())

        return segments

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
            tts = self.get_model(model)

            with torch.no_grad():
                audio_array = tts.tts(text=text_sentence, speaker=speaker, language=language)

            if len(audio_array) == 0:
                raise ValueError("TTS returned an empty audio array.")

            # Convert to WAV format
            audio_buffer = BytesIO()
            sf.write(audio_buffer, np.array(audio_array), samplerate=22050, format='WAV')

            audio_buffer.seek(0)
            return audio_buffer

        except Exception as e:
            Logger.error(f"Error during synthesis for text: {text_sentence[:30]}... - {str(e)}")
            return None

    def _combine_audio_buffers(self, audio_buffers):
        """
        Combines multiple audio buffers into a single WAV file.

        Args:
            audio_buffers (list of BytesIO): List of audio buffers to merge.

        Returns:
            BytesIO: A single WAV buffer containing all combined audio.
        """
        if not audio_buffers:
            raise ValueError("❌ No audio buffers provided for merging.")

        combined_audio = BytesIO()

        with wave.open(combined_audio, 'wb') as combined_wave:
            first_wave = None

            for buffer in audio_buffers:
                buffer.seek(0)
                with wave.open(buffer, 'rb') as wave_file:
                    params = wave_file.getparams()

                    if first_wave is None:
                        first_wave = params
                        combined_wave.setparams(params)

                    combined_wave.writeframes(wave_file.readframes(wave_file.getnframes()))

        combined_audio.seek(0)
        return combined_audio
