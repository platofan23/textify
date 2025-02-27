import hashlib
from io import BytesIO
from backend.app.synthesizers.synthezier_coqui import TTSSynthesizer
from backend.app.utils.util_logger import Logger

class TTSService:
    """
    Provides text-to-speech functionality with caching support.
    """

    def __init__(self, config_manager, cache_manager):
        self.config_manager = config_manager
        self.cache_manager = cache_manager
        # Optionally, a synthesizer can be injected (e.g. during testing)
        self.synthesizer = None
        Logger.info("TTSService initialized.")

    def synthesize_audio(self, text, model, speaker=None, language="de"):
        """
        Synthesizes text into speech and returns the result as a BytesIO object.

        Args:
            text (str): The text to convert to speech.
            model (str): The TTS model to use.
            speaker (str, optional): The speaker voice to use (if applicable).
            language (str, optional): The language to use for synthesis.

        Returns:
            BytesIO: The generated speech audio.
        """
        if not text or not text.strip():
            Logger.error("Invalid input: Text cannot be empty or whitespace only.")
            raise ValueError("Text cannot be empty or whitespace only.")

        # For multilingual models, only pass the language parameter.
        is_multi_lingual = "multilingual" in model or "xtts" in model
        language = language if is_multi_lingual else None

        Logger.info(f"🔍 Using model='{model}', speaker='{speaker}', language='{language}' for TTS.")

        # Build cache key based on model, speaker, language, and text hash.
        text_hash = hashlib.md5(text.encode()).hexdigest()
        cache_key = f"tts-{model}-{speaker}-{language}-{text_hash}"

        cached_audio = self.cache_manager.get(cache_key)
        if cached_audio:
            Logger.info(f"[CACHE HIT] Returning cached audio for key: {cache_key}")
            audio_buffer = BytesIO(cached_audio)
            audio_buffer.seek(0)
            return audio_buffer

        Logger.info(f"[CACHE MISS] No cache entry for key: {cache_key}")

        try:
            # Use an already assigned synthesizer if available (e.g. injected by tests)
            if self.synthesizer is not None:
                synthesizer = self.synthesizer
            else:
                synthesizer = TTSSynthesizer(self.config_manager, self.cache_manager)

            # Synthesize audio by passing text, model, speaker, and language.
            audio_buffer = synthesizer.synthesize(text, model, speaker, language)

            # Ensure the buffer is rewound before caching and returning.
            audio_buffer.seek(0)
            self.cache_manager.set(cache_key, audio_buffer.getvalue())
            Logger.info(f"[CACHE SET] Stored audio in cache for key: {cache_key}")

            return audio_buffer
        except Exception as e:
            Logger.error(f"❌ Error during TTS synthesis: {str(e)}")
            raise
