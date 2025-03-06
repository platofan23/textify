import hashlib
from io import BytesIO
from backend.app.synthesizers.synthezier_coqui import TTSSynthesizer
from backend.app.utils.util_logger import Logger

class TTSService:
    """
    Provides text-to-speech functionality with caching support.
    """
    def __init__(self, config_manager, cache_manager):
        """
        Initializes the TTSService with configuration and cache managers.

        Args:
            config_manager: Manages configuration settings.
            cache_manager: Manages caching of TTS outputs.
        """
        self.config_manager = config_manager
        self.cache_manager = cache_manager
        # Optionally, a synthesizer can be injected (e.g., during testing)
        self.synthesizer = None
        Logger.info("TTSService initialized.")

    def synthesize_audio(self, text, model, speaker=None, language="de"):
        """
        Synthesizes text into speech and returns the result as a BytesIO object.

        Args:
            text (str): The text to convert to speech.
            model (str): The TTS model to use.
            speaker (str, optional): The speaker voice to use (if applicable).
            language (str, optional): The language for synthesis (default is "de").

        Returns:
            BytesIO: The generated speech audio.

        Raises:
            ValueError: If the input text is empty or contains only whitespace.
            Exception: Propagates any exception encountered during synthesis.
        """
        if not text or not text.strip():
            Logger.error("Invalid input: Text cannot be empty or whitespace only.")
            raise ValueError("Text cannot be empty or whitespace only.")

        # For multilingual models, pass the language parameter; otherwise, set language to None.
        is_multi_lingual = "multilingual" in model or "xtts" in model
        language_param = language if is_multi_lingual else None

        Logger.info(f"Using model='{model}', speaker='{speaker}', language='{language_param}' for TTS.")

        # Build cache key based on model, speaker, language, and text hash.
        text_hash = hashlib.md5(text.encode()).hexdigest()
        cache_key = f"tts-{model}-{speaker}-{language_param}-{text_hash}"

        cached_audio = self.cache_manager.get(cache_key)
        if cached_audio:
            Logger.info(f"[CACHE HIT] Returning cached audio for key: {cache_key}")
            audio_buffer = BytesIO(cached_audio)
            audio_buffer.seek(0)
            return audio_buffer

        Logger.info(f"[CACHE MISS] No cache entry for key: {cache_key}")

        try:
            # Use an already assigned synthesizer if available (e.g., injected by tests),
            # otherwise create a new TTSSynthesizer instance.
            synthesizer = self.synthesizer if self.synthesizer is not None else TTSSynthesizer(self.config_manager, self.cache_manager)

            # Synthesize audio using text, model, speaker, and language.
            audio_buffer = synthesizer.synthesize(text, model, speaker, language_param)

            # Rewind the buffer before caching and returning.
            audio_buffer.seek(0)
            self.cache_manager.set(cache_key, audio_buffer.getvalue())
            Logger.info(f"[CACHE SET] Stored audio in cache for key: {cache_key}")

            return audio_buffer
        except Exception as e:
            Logger.error(f"Error during TTS synthesis: {str(e)}")
            raise
