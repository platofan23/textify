import hashlib
from io import BytesIO
from backend.app.synthesizers import TTSSynthesizer
from backend.app.utils.util_logger import Logger

class TTSService:
    """
    Provides text-to-speech functionality with caching support.
    """

    def __init__(self, config_manager, cache_manager):
        self.config_manager = config_manager
        self.cache_manager = cache_manager
        self.synthesizer = TTSSynthesizer()  # Coqui TTS verwenden
        Logger.info("TTSService initialized.")

    def synthesize_audio(self, text, voice, language):
        """
        Synthesizes text into speech and returns the result as a BytesIO object.

        Args:
            text (str): The text to synthesize.
            voice (str): Voice setting (currently unused for Coqui TTS).
            language (str): Language setting (currently unused for Coqui TTS).

        Returns:
            BytesIO: In-memory WAV file.
        """
        try:
            # Preprocess text
            text = text.strip()
            if not text.endswith("."):
                text += "."  # Sicherstellen, dass der Satz korrekt abgeschlossen ist

            # Erzeuge einen Hash als Cache-Schlüssel
            text_hash = hashlib.md5(text.encode()).hexdigest()
            cache_key = f"tts-{voice or 'default'}-{language or 'en'}-{text_hash}"

            # Überprüfen, ob die Audiodatei bereits im Cache ist
            cached_audio = self.cache_manager.get(cache_key)
            if cached_audio:
                Logger.info(f"[CACHE HIT] Returning cached audio for key: {cache_key}")
                audio_buffer = BytesIO(cached_audio)
                audio_buffer.seek(0)
                return audio_buffer

            Logger.info(f"[CACHE MISS] No cache entry for key: {cache_key}")

            # Generiere die Audiodatei
            audio_buffer = self.synthesizer.synthesize(text)

            # Cache die generierte Audiodatei
            self.cache_manager.set(cache_key, audio_buffer.getvalue())
            Logger.info(f"[CACHE SET] Stored audio in cache for key: {cache_key}")

            return audio_buffer
        except Exception as e:
            Logger.error(f"Error during TTS synthesis: {str(e)}")
            raise
