import tempfile
from io import BytesIO
from TTS.api import TTS
from backend.app.utils.util_logger import Logger


class TTSSynthesizer:
    """
    Synthesizes text into speech using the Coqui TTS library.
    """

    def __init__(self, model_name="tts_models/de/thorsten/tacotron2-DCA"):
        """
        Initializes the TTS synthesizer with a specified model.

        Args:
            model_name (str): The name of the Coqui TTS model to use.
        """
        self.model_name = model_name
        self.tts = TTS(model_name=model_name)
        Logger.info(f"TTSSynthesizer initialized with model={model_name}.")

    def synthesize(self, text):
        """
        Synthesizes the given text into a WAV file in memory.

        Args:
            text (str): The text to synthesize.

        Returns:
            BytesIO: In-memory WAV file.
        """
        try:
            Logger.info("Synthesizing text with Coqui TTS...")

            # Temporäre Datei erstellen
            with tempfile.NamedTemporaryFile(delete=True, suffix=".wav") as tmpfile:
                self.tts.tts_to_file(text=text, file_path=tmpfile.name)

                # Inhalt der temporären Datei in BytesIO laden
                tmpfile.seek(0)
                audio_buffer = BytesIO(tmpfile.read())

            Logger.info("Audio synthesis completed successfully.")
            audio_buffer.seek(0)
            return audio_buffer
        except Exception as e:
            Logger.error(f"Error during synthesis: {str(e)}")
            raise
