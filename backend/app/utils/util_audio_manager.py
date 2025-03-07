import noisereduce as nr
import numpy as np
from scipy.signal import butter, filtfilt
from backend.app.utils.util_logger import Logger


def bandpass_filter(audio: np.ndarray, sr: int, lowcut: float = 80, highcut: float = 8000,
                    order: int = 5) -> np.ndarray:
    """
    Applies a Butterworth bandpass filter to the audio signal.
    The function normalizes the critical frequencies such that 0 < Wn < 1.

    Args:
        audio (np.ndarray): The audio signal.
        sr (int): Sampling rate.
        lowcut (float): Lower cutoff frequency in Hz.
        highcut (float): Upper cutoff frequency in Hz.
        order (int): Filter order.

    Returns:
        np.ndarray: The filtered audio.
    """
    nyquist = 0.5 * sr
    low = lowcut / nyquist
    high = highcut / nyquist
    if high >= 1:
        # Ensure the upper cutoff frequency is strictly less than 1.
        high = 0.99
    Logger.info(f"Applying bandpass filter with low={low:.3f} and high={high:.3f}")
    b, a = butter(order, [low, high], btype="band")
    filtered_audio = filtfilt(b, a, audio)
    return filtered_audio


def normalize_audio(audio: np.ndarray) -> np.ndarray:
    """
    Normalizes the audio signal to have a maximum absolute value of 1.

    Args:
        audio (np.ndarray): The audio signal.

    Returns:
        np.ndarray: The normalized audio.
    """
    max_val = np.max(np.abs(audio))
    if max_val == 0:
        return audio
    normalized_audio = audio / max_val
    Logger.info("Audio normalized.")
    return normalized_audio


def preprocess_audio(audio: np.ndarray, sr: int = 16000) -> np.ndarray:
    """
    Preprocesses the audio signal by applying noise reduction, bandpass filtering,
    normalization, and whitespace cleanup if necessary.

    Args:
        audio (np.ndarray): The raw audio signal.
        sr (int): Sampling rate (default is 16000, common for Whisper).

    Returns:
        np.ndarray: The preprocessed audio.
    """
    Logger.info("Starting audio preprocessing...")
    # Reduce noise using spectral gating.
    audio_nr = nr.reduce_noise(y=audio, sr=sr)
    Logger.info("Noise reduction applied.")
    # Apply bandpass filter.
    audio_filtered = bandpass_filter(audio_nr, sr, lowcut=80, highcut=8000, order=5)
    Logger.info("Bandpass filtering applied.")
    # Normalize the audio.
    audio_normalized = normalize_audio(audio_filtered)
    Logger.info("Audio preprocessing completed.")
    return audio_normalized