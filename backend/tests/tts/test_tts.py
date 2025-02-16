import pytest
from unittest.mock import MagicMock
import torch
from backend.app.services.service_tts import TTSService


class TestTTSService:
    """Unit tests for the TTSService class with local mocking."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Sets up a local instance of TTSService with mock components."""
        self.mock_tts_model = MagicMock()
        from io import BytesIO
        self.mock_tts_model.synthesize.return_value = BytesIO(b"generated_audio")

        self.cache_manager = MagicMock()
        self.cache_manager.get.return_value = None  # Default: No cache hit
        self.cache_manager.set.side_effect = lambda key, value: None  # Dummy cache set

        self.config_manager = MagicMock()
        self.config_manager.get_torch_device.return_value = "cuda" if torch.cuda.is_available() else "cpu"

        # ✅ Create a local TTSService instance
        self.tts_service = TTSService(
            config_manager=self.config_manager,
            cache_manager=self.cache_manager
        )

        # ✅ Explicitly mock the synthesizer before mocking its method
        self.tts_service.synthesizer = MagicMock()
        self.tts_service.synthesizer.synthesize.return_value = BytesIO(b"generated_audio")

    def test_tts_service_cache_hit(self):
        """Tests whether TTSService correctly returns an audio file from the cache."""
        cached_audio_data = b"cached_audio"
        self.cache_manager.get.return_value = cached_audio_data  # Simulated cache hit

        result = self.tts_service.synthesize_audio(
            text="Hello, world.",
            model="tts_models/en/ljspeech/tacotron2-DDC",
            speaker=None,
            language="en"
        )

        assert result.getvalue() == cached_audio_data, "The returned audio should match the cached audio."
        self.cache_manager.get.assert_called()

    def test_tts_service_cache_miss(self):
        """Tests whether a new audio file is generated and stored in the cache on a cache miss."""
        self.cache_manager.get.return_value = None  # Simulated cache miss

        result = self.tts_service.synthesize_audio(
            text="This is a test.",
            model="tts_models/de/thorsten/tacotron2-DCA",
            speaker=None,
            language="de"
        )

        assert result.getbuffer().nbytes > 0, "The generated audio should not be empty."
        assert self.cache_manager.set.call_count == 1, "Cache should be set twice (model + audio)"

    def test_tts_service_invalid_text(self):
        """Tests whether TTSService raises an error when the input text is empty."""
        with pytest.raises(ValueError, match="Text cannot be empty or whitespace only."):
            self.tts_service.synthesize_audio(
                text="",
                model="tts_models/en/ljspeech/tacotron2-DDC",
                speaker=None,
                language="en"
            )

    def test_tts_service_different_models(self):
        """Tests whether different models are correctly processed."""
        self.mock_tts_model.synthesize.side_effect = [b"audio_model_1", b"audio_model_2"]

        result_1 = self.tts_service.synthesize_audio(
            text="Different model test.",
            model="tts_models/de/thorsten/tacotron2-DCA",
            speaker=None,
            language="de"
        )
        result_2 = self.tts_service.synthesize_audio(
            text="Speaker test.",
            model="tts_models/multilingual/multi-dataset/xtts_v2",
            speaker="Tammie Ema",
            language="en"
        )

        assert result_1 != result_2, "Different models should produce different outputs."
        assert self.cache_manager.set.call_count == 2, "Both models should be cached separately."

    def test_tts_service_with_speaker(self):
        """Tests whether speaker selection is correctly processed."""

        result = self.tts_service.synthesize_audio(
            text="Speaker test.",
            model="tts_models/multilingual/multi-dataset/xtts_v2",
            speaker="Tammie Ema",
            language="en"
        )

        assert result.getbuffer().nbytes > 0, "The generated audio should not be empty."
        assert self.cache_manager.set.call_count >= 1, "The cache should have been updated."

    def test_tts_service_with_different_languages(self):
        """Tests whether different languages are correctly handled."""
        result_1 = self.tts_service.synthesize_audio(
            text="Hello world!",
            model="tts_models/multilingual/multi-dataset/xtts_v2",
            speaker="Tammie Ema",
            language="en"
        )
        result_2 = self.tts_service.synthesize_audio(
            text="Hallo Welt!",
            model="tts_models/multilingual/multi-dataset/xtts_v2",
            speaker="Tammie Ema",
            language="de"
        )

        assert result_1 != result_2, "Different languages should produce different outputs."
        assert self.cache_manager.set.call_count == 2, "Both language outputs should be cached separately."


if __name__ == '__main__':
    pytest.main()
