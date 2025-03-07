import pytest
from unittest.mock import MagicMock
import torch
from backend.app.services.service_tts import TTSService
from io import BytesIO

class TestTTSService:
    """Unit tests for the TTSService class using only the xtts_v2 model."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Sets up a local instance of TTSService with mock components."""
        # Create a dummy TTS model synthesizer that returns non-empty audio.
        self.mock_tts_model = MagicMock()
        self.mock_tts_model.synthesize.return_value = BytesIO(b"generated_audio")

        self.cache_manager = MagicMock()
        self.cache_manager.get.return_value = None  # Simulated cache miss by default
        self.cache_manager.set.side_effect = lambda key, value: None  # Dummy cache set

        self.config_manager = MagicMock()
        self.config_manager.get_torch_device.return_value = "cuda" if torch.cuda.is_available() else "cpu"

        # Create a TTSService instance.
        self.tts_service = TTSService(
            config_manager=self.config_manager,
            cache_manager=self.cache_manager
        )

        # Inject the mocked synthesizer into the service.
        self.tts_service.synthesizer = MagicMock()
        self.tts_service.synthesizer.synthesize.return_value = BytesIO(b"generated_audio")

    def test_tts_service_cache_hit(self):
        """Tests that TTSService returns cached audio when available."""
        # Use xtts_v2 model for these tests.
        model = "tts_models/multilingual/multi-dataset/xtts_v2"
        speaker = "Tammie Ema"
        language = "en"
        text = "Hello, world."

        # Simulate a cache hit with pre-cached audio.
        cached_audio_data = b"cached_audio"
        self.cache_manager.get.return_value = cached_audio_data

        result = self.tts_service.synthesize_audio(
            text=text,
            model=model,
            speaker=speaker,
            language=language
        )

        # The returned audio should match the cached data.
        assert result.getvalue() == cached_audio_data, "The returned audio should match the cached audio."
        self.cache_manager.get.assert_called()

    def test_tts_service_cache_miss(self):
        """Tests that TTSService synthesizes new audio and caches it on a cache miss."""
        model = "tts_models/multilingual/multi-dataset/xtts_v2"
        speaker = "Tammie Ema"
        language = "en"
        text = "This is a test."

        # Simulate a cache miss.
        self.cache_manager.get.return_value = None

        result = self.tts_service.synthesize_audio(
            text=text,
            model=model,
            speaker=speaker,
            language=language
        )

        # Ensure that the generated audio is non-empty.
        assert result.getbuffer().nbytes > 0, "The generated audio should not be empty."
        # Expect one cache set call.
        assert self.cache_manager.set.call_count == 1, "Audio should be cached on a cache miss."

    def test_tts_service_invalid_text(self):
        """Tests that TTSService raises a ValueError when the input text is empty."""
        model = "tts_models/multilingual/multi-dataset/xtts_v2"
        with pytest.raises(ValueError, match="Text cannot be empty or whitespace only."):
            self.tts_service.synthesize_audio(
                text="   ",
                model=model,
                speaker="Tammie Ema",
                language="en"
            )

    def test_tts_service_with_speaker(self):
        """Tests that TTSService correctly processes requests with speaker selection."""
        model = "tts_models/multilingual/multi-dataset/xtts_v2"
        speaker = "Tammie Ema"
        language = "en"
        text = "Speaker test."

        result = self.tts_service.synthesize_audio(
            text=text,
            model=model,
            speaker=speaker,
            language=language
        )

        # Assert that the synthesized audio is non-empty.
        assert result.getbuffer().nbytes > 0, "The generated audio should not be empty."
        assert self.cache_manager.set.call_count >= 1, "The cache should have been updated."

    def test_tts_service_with_different_languages(self):
        """Tests that TTSService handles different language inputs for the same model and speaker."""
        model = "tts_models/multilingual/multi-dataset/xtts_v2"
        speaker = "Tammie Ema"
        text_en = "Hello world!"
        text_de = "Hallo du also an der Goethe uni!"

        # Setup the synthesizer to return different outputs based on the language parameter.
        def synthesize_side_effect(text, model, speaker, language):
            if language == "en":
                return BytesIO(b"generated_audio_en")
            elif language == "de":
                return BytesIO(b"generated_audio_de")
            else:
                return BytesIO(b"generated_audio")

        self.tts_service.synthesizer.synthesize.side_effect = synthesize_side_effect

        result_en = self.tts_service.synthesize_audio(
            text=text_en,
            model=model,
            speaker=speaker,
            language="en"
        )
        result_de = self.tts_service.synthesize_audio(
            text=text_de,
            model=model,
            speaker=speaker,
            language="de"
        )

        # Ensure that outputs for different languages are not identical.
        assert result_en.getvalue() != result_de.getvalue(), "Different languages should produce different outputs."
        # Expect two cache set calls (one per language).
        assert self.cache_manager.set.call_count == 2, "Both language outputs should be cached separately."


if __name__ == '__main__':
    pytest.main()
