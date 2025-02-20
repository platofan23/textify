from .route_file_manager import DownloadFile, UploadFile, GetBookInfo
from .route_ocr import ReadFile
from .route_translation_file import TranslateFile
from .route_translation_text import TranslateText
from .route_user_management import RegisterUser, LoginUser

__all__ = [
    "DownloadFile",
    "UploadFile",
    "ReadFile",
    "TranslateFile",
    "TranslateText",
    "RegisterUser",
    "LoginUser",
    "GetBookInfo",
]
