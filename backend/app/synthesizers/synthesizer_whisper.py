import os
import io
import numpy as np
import whisper

from backend.app.utils import preprocess_audio
from backend.app.utils.util_logger import Logger

class STTSynthesizer:
    """
    Provides speech-to-text transcription using OpenAI Whisper.
    Applies preprocessing (noise reduction, bandpass filtering, normalization)
    before transcribing the audio.
    """

    def __init__(self, model_name: str = "turbo", cache_manager=None):
        """
        Initializes the STTSynthesizer with a specified model name and optional cache manager.

        Args:
            model_name (str): The Whisper model name to load (default is "turbo").
            cache_manager: Optional CacheManager instance for caching the model.
        """
        self.model = None
        self.model_name = model_name
        self.cache_manager = cache_manager
        Logger.info(f"STTSynthesizer initialized with model '{model_name}'. Model will be loaded on first use.")

    def transcribe(self, audio_buffer: io.BytesIO) -> str:
        """
        Transcribes the given audio file to text using the Whisper model.
        The audio is preprocessed before transcription and cast to float32 to match model requirements.

        Args:
            audio_buffer (io.BytesIO): A file-like object containing the audio data.

        Returns:
            str: The transcribed text.
        """
        # Lazy-load the model if it hasn't been loaded yet.
        if self.model is None:
            if self.cache_manager is not None:
                cached_model = self.cache_manager.get(f"stt_model-{self.model_name}")
                if cached_model is not None:
                    self.model = cached_model
                    Logger.info(f"STT model '{self.model_name}' loaded from cache.")
            if self.model is None:
                Logger.info(f"Loading Whisper model '{self.model_name}' (pretrained and cached locally)...")
                self.model = whisper.load_model(self.model_name)
                Logger.info(f"Whisper model '{self.model_name}' loaded successfully.")
                if self.cache_manager is not None:
                    self.cache_manager.set(f"stt_model-{self.model_name}", self.model)

        # Write the audio_buffer to a temporary WAV file.
        temp_wav = "temp_audio.wav"
        try:
            audio_buffer.seek(0)
            with open(temp_wav, "wb") as f:
                f.write(audio_buffer.read())
            # Load audio from the temporary file.
            audio = whisper.load_audio(temp_wav)
            # Preprocess the audio (noise reduction, filtering, normalization, etc.)
            processed_audio = preprocess_audio(audio, sr=16000)
            # Convert processed audio to float32 to match model expectations.
            processed_audio = processed_audio.astype(np.float32)
            # Transcribe the preprocessed audio.
            result = self.model.transcribe(processed_audio)
            Logger.info("Audio transcription completed successfully.")
            return result["text"]
        finally:
            if os.path.exists(temp_wav):
                os.remove(temp_wav)