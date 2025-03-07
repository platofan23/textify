import os
import io
import torch
import numpy as np
import whisper

from backend.app.utils import preprocess_audio, ConfigManager
from backend.app.utils.util_logger import Logger


class STTSynthesizer:
    """
    Provides speech-to-text transcription using OpenAI Whisper.
    Applies preprocessing (noise reduction, bandpass filtering, normalization)
    before transcribing the audio.
    """

    def __init__(self, model_name: str = "turbo", cache_manager=None, config_manger=ConfigManager()):
        """
        Initializes the STTSynthesizer with a specified model name and optional cache manager.

        Args:
            model_name (str): The Whisper model name to load (default: "turbo").
            cache_manager: Optional CacheManager instance for caching the model.
        """
        self.model = None
        self.model_name = model_name
        self.cache_manager = cache_manager
        self.device = config_manger.get_torch_device()
        Logger.info(f"STTSynthesizer initialized with model '{model_name}' on {self.device}. Model will be loaded on first use.")

    def _load_model(self):
        """Loads the Whisper model from cache or disk."""
        if self.model is None:
            cache_key = f"stt_model-{self.model_name}"
            if self.cache_manager:
                self.model = self.cache_manager.get(cache_key)
                if self.model:
                    Logger.info(f"STT model '{self.model_name}' loaded from cache.")

            if self.model is None:
                Logger.info(f"Loading Whisper model '{self.model_name}' on {self.device}...")
                self.model = whisper.load_model(self.model_name, device=self.device, download_root="/models")  # 📌 GPU-Modus aktiv
                Logger.info(f"Whisper model '{self.model_name}' loaded successfully on {self.device}.")
                if self.cache_manager:
                    self.cache_manager.set(cache_key, self.model)

    def transcribe(self, audio_buffer: io.BytesIO) -> str:
        """
        Transcribes preprocessed audio to text using Whisper.

        Args:
            audio_buffer (io.BytesIO): Audio data.

        Returns:
            str: Transcribed text.
        """
        # 📌 Sicherstellen, dass das Modell geladen wurde
        if self.model is None:
            self._load_model()

        # 📌 Temporäre WAV-Datei für Whisper erstellen
        temp_wav = "temp_audio.wav"
        try:
            audio_buffer.seek(0)
            with open(temp_wav, "wb") as f:
                f.write(audio_buffer.read())

            # 📌 Audio laden & vorverarbeiten (Noise Reduction, Bandpass, Normalisierung)
            audio = whisper.load_audio(temp_wav)
            processed_audio = preprocess_audio(audio, sr=16000)
            processed_audio = processed_audio.astype(np.float32)  # 🔥 Float32 für Whisper

            # 📌 Transkription mit Whisper
            result = self.model.transcribe(processed_audio)

            Logger.info("Audio transcription completed successfully.")
            return result["text"]
        except Exception as e:
            Logger.error(f"Transcription failed: {str(e)}")
            return "Error in transcription"
        finally:
            if os.path.exists(temp_wav):
                os.remove(temp_wav)