### translators/__init__.py ###
from .translator_opus import OpusMTTranslator
from .translator_libre import LibreTranslateTranslator

__all__ = ["OpusMTTranslator", "LibreTranslateTranslator"]
