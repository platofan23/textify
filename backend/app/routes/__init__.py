from .route_file_manager import DownloadFile, UploadFile, GetBookInfo
from .route_ocr import ReadFile
from .route_translation_file import TranslateFile
from .route_translation_text import TranslateText
from .route_user_management import RegisterUser, LoginUser
from .route_tts import TTS
from .route_translation_models import ModelTranslation
from .route_tts_models import ModelTTS
from .route_tts_speakers import  SpeakerTTS
from .route_translate_page import TranslatePage
from .route_tts_page import TTSPage
from .route_docker_healthcheck import HealthCheck


__all__ = [
    "DownloadFile",
    "UploadFile",
    "ReadFile",
    "TranslateFile",
    "TranslateText",
    "RegisterUser",
    "LoginUser",
    "GetBookInfo",
    "TTS",
    "ModelTranslation",
    "ModelTTS",
    "SpeakerTTS",
    "HealthCheck",
    "TranslatePage",
    "TTSPage"
]
