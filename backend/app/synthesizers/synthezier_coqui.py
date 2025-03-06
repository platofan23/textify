import torch
from io import BytesIO
from TTS.api import TTS
import soundfile as sf
import numpy as np
import wave
from backend.app.utils.util_logger import Logger

class TTSSynthesizer:
    """
    Synthesizes text into speech using the Coqui TTS library with in-memory caching support.
    """
    def __init__(self, config_manager, cache_manager):
        """
        Initializes the TTS synthesizer with caching support.

        Args:
            config_manager: Configuration manager instance.
            cache_manager: Cache manager instance.
        """
        self.dont_spam_model = False
        self.config_manager = config_manager
        self.cache_manager = cache_manager
        self.device = "cuda" if self.config_manager.get_torch_device() == "cuda" else "cpu"
        Logger.info(f"TTSSynthesizer initialized. Running on {self.device.upper()}.")

    def get_model(self, model_name: str):
        """
        Loads a TTS model from RAM cache if available; otherwise, loads and caches it.

        Args:
            model_name (str): The name of the model to load.

        Returns:
            TTS: The loaded model instance.
        """
        cached_model = self.cache_manager.load_cached_tts_model(model_name)
        if cached_model:
            if not self.dont_spam_model:
                self.dont_spam_model = True
                Logger.info(f"Using preloaded TTS model from RAM: {model_name}")
            return cached_model

        Logger.warning(f"No cached TTS model found for '{model_name}', loading fresh...")
        model = TTS(model_name)
        model.to(self.device)

        # Store model in RAM cache.
        self.cache_manager.cache_tts_model(model_name, model)
        Logger.info(f"Model '{model_name}' successfully stored in RAM.")
        return model

    def synthesize(self, text: str, model: str, speaker: str = None, language: str = None) -> BytesIO:
        """
        Synthesizes text into speech and returns the result as an in-memory WAV file.

        Args:
            text (str): The text to synthesize.
            model (str): The TTS model to use.
            speaker (str, optional): The speaker voice to use, if applicable.
            language (str, optional): The language to use.

        Returns:
            BytesIO: An in-memory WAV file containing the synthesized speech.

        Raises:
            ValueError: If no valid text segments or audio buffers are generated.
            Exception: Propagates any other exceptions encountered during synthesis.
        """
        try:
            Logger.info(f"Synthesizing text with model='{model}', speaker='{speaker}', language='{language}'...")

            # Split text into manageable chunks.
            text_segments = self._chunk_text(text)
            if not text_segments:
                Logger.error("No valid text segments to synthesize. Aborting.")
                raise ValueError("No valid text segments to synthesize.")

            Logger.info(f"Text split into {len(text_segments)} chunk(s) for synthesis.")

            audio_buffers = []
            for i, segment in enumerate(text_segments):
                Logger.debug(f"Synthesizing chunk {i + 1}/{len(text_segments)}: '{segment[:30]}...'")
                buffer = self._tts_for_synthesize(segment, model, speaker, language)
                if buffer and buffer.getbuffer().nbytes > 0:
                    Logger.info(f"Chunk {i + 1} synthesized successfully. Buffer size: {buffer.getbuffer().nbytes} bytes.")
                    audio_buffers.append(buffer)
                else:
                    Logger.warning(f"TTS returned an empty buffer for chunk {i + 1}: '{segment[:30]}...'")
            if not audio_buffers:
                Logger.error("No valid audio buffers generated. TTS synthesis failed.")
                raise ValueError("No valid audio buffers generated.")

            Logger.info("All text chunks synthesized successfully. Merging audio buffers...")
            combined_audio = self._combine_audio_buffers(audio_buffers)
            Logger.info(f"Final synthesized audio size: {combined_audio.getbuffer().nbytes} bytes.")
            return combined_audio

        except Exception as e:
            Logger.error(f"Error during synthesis: {str(e)}")
            raise

    def _chunk_text(self, text: str) -> List[str]:
        """
        Splits text into smaller segments for synthesis based on a character limit.

        Args:
            text (str): The full text to split.

        Returns:
            List[str]: A list of text segments.
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
        Logger.info(f"Text chunking complete: {len(segments)} segment(s) created.")
        return segments

    def _tts_for_synthesize(self, text_sentence: str, model: str, speaker: str = None, language: str = None) -> Union[BytesIO, None]:
        """
        Synthesizes a text segment into speech and returns an in-memory WAV file.

        Args:
            text_sentence (str): The text segment to synthesize.
            model (str): The TTS model to use.
            speaker (str, optional): The speaker voice to use.
            language (str, optional): The language to use.

        Returns:
            BytesIO or None: An in-memory WAV file containing the synthesized speech, or None on failure.
        """
        try:
            tts = self.get_model(model)
            with torch.no_grad():
                audio_array = tts.tts(text=text_sentence, speaker=speaker, language=language)
            if len(audio_array) == 0:
                Logger.error("TTS returned an empty audio array.")
                raise ValueError("TTS returned an empty audio array.")
            # Convert synthesized audio array to a WAV file in memory.
            audio_buffer = BytesIO()
            sf.write(audio_buffer, np.array(audio_array), samplerate=22050, format='WAV')
            audio_buffer.seek(0)
            return audio_buffer
        except Exception as e:
            Logger.error(f"Error during synthesis for text: '{text_sentence[:30]}...' - {str(e)}")
            return None

    def _combine_audio_buffers(self, audio_buffers: List[BytesIO]) -> BytesIO:
        """
        Combines multiple audio buffers into a single WAV file.

        Args:
            audio_buffers (List[BytesIO]): A list of audio buffers to merge.

        Returns:
            BytesIO: A single WAV file buffer containing the combined audio.

        Raises:
            ValueError: If no audio buffers are provided.
        """
        if not audio_buffers:
            Logger.error("No audio buffers provided for merging.")
            raise ValueError("No audio buffers provided for merging.")

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
        Logger.info("Audio buffers successfully merged into a single WAV file.")
        return combined_audio
