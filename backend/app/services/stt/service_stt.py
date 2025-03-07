import hashlib
from io import BytesIO

from backend.app.synthesizers import STTSynthesizer
from backend.app.utils.util_logger import Logger

class SpeechToTextService:
    """
    Provides speech-to-text functionality with caching support.
    """
    def __init__(self, config_manager, cache_manager):
        """
        Initializes the SpeechToTextService with configuration and cache managers.

        Args:
            config_manager: Manages configuration settings.
            cache_manager: Manages caching of STT outputs.
        """
        self.config_manager = config_manager
        self.cache_manager = cache_manager
        # Create a new instance of the Whisper synthesizer (pretrained model will be downloaded and cached locally)
        self.synthesizer = STTSynthesizer(self.config_manager.get_stt_models())
        Logger.info("SpeechToTextService initialized.")

    def transcribe_audio(self, audio_file) -> str:
        """
        Transcribes the provided audio file into text.

        This method reads the audio content once to compute its hash for caching.
        It then resets the file pointer and calls the synthesizer to obtain a transcription.
        The transcription is cached using the audio hash.

        Args:
            audio_file: A file-like object (or bytes or file path) containing the WAV audio data.

        Returns:
            str: The transcribed text.

        Raises:
            ValueError: If the audio content is empty.
            Exception: Propagates any exception encountered during transcription.
        """
        # Convert the input to a file-like BytesIO object if necessary.
        if isinstance(audio_file, bytes):
            audio_buffer = BytesIO(audio_file)
        elif isinstance(audio_file, str):
            with open(audio_file, "rb") as f:
                audio_buffer = BytesIO(f.read())
        else:
            # Even if it's already a file-like object, wrap its content in BytesIO.
            audio_buffer = BytesIO(audio_file.read())

        # Read the audio content and ensure it's not empty.
        audio_buffer.seek(0)
        audio_content = audio_buffer.read()
        if not audio_content:
            Logger.error("Invalid input: Audio content is empty.")
            raise ValueError("Audio content cannot be empty.")

        # Compute a hash for caching.
        audio_hash = hashlib.md5(audio_content).hexdigest()
        cache_key = f"stt-{audio_hash}"

        cached_transcription = self.cache_manager.get(cache_key)
        if cached_transcription:
            Logger.info(f"[CACHE HIT] Returning cached transcription for key: {cache_key}")
            return cached_transcription

        Logger.info(f"[CACHE MISS] No cache entry for key: {cache_key}")

        # Reset the buffer pointer so it can be processed.
        audio_buffer.seek(0)

        try:
            transcription = self.synthesizer.transcribe(audio_buffer)
            self.cache_manager.set(cache_key, transcription)
            Logger.info(f"[CACHE SET] Stored transcription in cache for key: {cache_key}")
            return transcription
        except Exception as e:
            Logger.error(f"Error during STT transcription: {str(e)}")
            raise