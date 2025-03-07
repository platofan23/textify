### translators/__init__.py ###
from .synthezier_coqui import TTSSynthesizer
from .synthesizer_whisper import STTSynthesizer

__all__ = ["TTSSynthesizer",
           "STTSynthesizer"
            ]
