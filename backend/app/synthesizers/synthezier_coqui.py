import tempfile
import os
import torch
from io import BytesIO
from TTS.api import TTS
from backend.app.utils.util_logger import Logger


class TTSSynthesizer:
    """
    Synthesizes text into speech using the Coqui TTS library with GPU support.
    """

    def __init__(self, model_name="tts_models/de/thorsten/tacotron2-DCA"):
        """
        Initializes the TTS synthesizer with a specified model.

        Args:
            model_name (str): The name of the Coqui TTS model to use.
        """
        # Prüfe, ob eine GPU verfügbar ist
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model_name = model_name

        # Lade das Modell mit GPU-Unterstützung
        self.tts = TTS(model_name=model_name, gpu=(self.device == "cuda"))
        Logger.info(f"TTSSynthesizer initialized with model={model_name} on {self.device}.")

    def synthesize(self, text):
        """
        Synthesizes the given text into a WAV file in memory.

        Args:
            text (str): The text to synthesize.

        Returns:
            BytesIO: In-memory WAV file.
        """
        try:
            Logger.info(f"Synthesizing text with Coqui TTS on {self.device}...")

            # Temporäre Datei erstellen (Windows-kompatibel)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmpfile:
                temp_filename = tmpfile.name  # Speichere den Dateipfad

            # Synthese in die Datei schreiben (mit GPU-Unterstützung)
            self.tts.tts_to_file(text=text, file_path=temp_filename)

            # Datei in BytesIO einlesen
            with open(temp_filename, "rb") as f:
                audio_buffer = BytesIO(f.read())

            # Datei manuell löschen (weil delete=False)
            os.remove(temp_filename)

            Logger.info("Audio synthesis completed successfully.")
            audio_buffer.seek(0)
            return audio_buffer
        except Exception as e:
            Logger.error(f"Error during synthesis: {str(e)}")
            raise
