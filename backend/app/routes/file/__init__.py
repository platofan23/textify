from .route_file_bookinfo import GetBookInfo
from .route_file_delete import DeleteFile
from .route_file_download import DownloadFile
from .route_file_get_book_translations import GetBookTranslations
from .route_file_upload import UploadFile
from .route_file_bookpage import GetBookPage

__all__ = [
    "GetBookInfo",
    "DeleteFile",
    "DownloadFile",
    "UploadFile",
    "GetBookPage",
    "GetBookTranslations"
]