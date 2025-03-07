import unittest
from unittest.mock import patch
import numpy as np
import noisereduce as nr
from backend.app.utils import preprocess_audio, bandpass_filter, normalize_audio

class TestAudioProcessing(unittest.TestCase):
    def setUp(self):
        """
        Set up test audio data.
        """
        self.sr = 16000  # Sample rate
        self.audio = np.random.randn(self.sr)  # Simulated 1-second audio signal

    def test_bandpass_filter(self):
        """
        Test that the bandpass filter function returns an array of the same shape.
        """
        filtered_audio = bandpass_filter(self.audio, self.sr)
        self.assertEqual(filtered_audio.shape, self.audio.shape)

    def test_normalize_audio(self):
        """
        Test that the normalize_audio function scales values correctly.
        """
        normalized_audio = normalize_audio(self.audio)
        self.assertAlmostEqual(np.max(np.abs(normalized_audio)), 1.0, places=5)

    @patch("noisereduce.reduce_noise")
    def test_preprocess_audio(self, mock_reduce_noise):
        """
        Test full audio preprocessing pipeline with noise reduction mock.
        """
        # Mock the noise reduction to return the input unchanged
        mock_reduce_noise.return_value = self.audio

        processed_audio = preprocess_audio(self.audio, self.sr)
        self.assertEqual(processed_audio.shape, self.audio.shape)
        self.assertAlmostEqual(np.max(np.abs(processed_audio)), 1.0, places=5)

if __name__ == "__main__":
    unittest.main()