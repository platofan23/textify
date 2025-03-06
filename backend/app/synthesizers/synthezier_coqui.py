from typing import List, Union

import torch
from io import BytesIO
from TTS.api import TTS
import soundfile as sf
import numpy as np
from debugpy.launcher import channel

from backend.app.utils.util_logger import Logger
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
        self.device = self.config_manager.get_torch_device()
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

            Logger.debug(f"{text}")

            Logger.info("Audio synthesis running")

            # Split the text into chunks of 252 characters
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
                    # Synthesize the text up to the last punctuation mark
                    audio_buffers.append(self._tts_for_synthesize(text[:last_punctuation_mark], model, speaker, language))
                    Logger.info(f" {i/len(text)}% of the text has been synthesized.")
                    text = text[last_punctuation_mark:]
                    char_count = 0
                    i = 0
                    last_punctuation_mark = 0
                    continue
                i += 1
            # If the text is shorter than 252 characters, synthesize it directly
            if len(audio_buffers) == 0:
                audio_buffers.append(self._tts_for_synthesize(text, model, speaker, language))

            Logger.debug(f"Synthesizing {len(audio_buffers)} audio chunks...")

            Logger.info("Audio synthesis completed successfully.")


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
            Logger.error(f"Error during synthesis: {str(e)}")
            raise

    @staticmethod
    def _chunk_text(text: str) -> List[str]:
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
            sf.write(audio_buffer, np.array(audio_array), samplerate=self.config_manager.get_tts_samplerate(), format='WAV')
            audio_buffer.seek(0)
            return audio_buffer
        except Exception as e:
            Logger.error(f"Error during synthesis for text: '{text_sentence[:30]}...' - {str(e)}")
            return None

    @staticmethod
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
