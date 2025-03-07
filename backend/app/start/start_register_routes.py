from backend.app.routes.docker import HealthCheck
from backend.app.routes.file import DownloadFile, GetBookInfo, UploadFile, DeleteFile, GetBookPage, GetBookTranslations, \
    GetBookLanguage, DeleteBook
from backend.app.routes.ocr import ReadFile
from backend.app.routes.stt import SpeechToText
from backend.app.routes.translation import TranslatePage, TranslateAllPages, TranslateFile, TranslateText, \
    ModelTranslation
from backend.app.routes.tts import TTSPage, TTS, LanguageTTS, ModelTTS, SpeakerTTS
from backend.app.routes.user import LoginUser, RegisterUser
from backend.app.utils import Logger


def register_routes(api, config_manager, cache_manager, mongo_manager, crypto_manager):
    """
    Registers all endpoints with the Flask-RESTful API.

    Args:
        api (Api): Flask-RESTful API instance.
        config_manager (ConfigManager): Configuration manager instance.
        cache_manager (CacheManager): Cache manager instance.
    """
    Logger.info("Registering routes with the Flask-RESTful API.")

    # File-related endpoints
    api.add_resource(
        DownloadFile,
        '/download_file',
        resource_class_kwargs={'config_manager': config_manager, 'mongo_manager': mongo_manager, 'crypto_manager':crypto_manager}
    )
    Logger.info("Registered route: /download_file -> DownloadFile")

    api.add_resource(
        UploadFile,
        '/upload_files',
        resource_class_kwargs={'config_manager': config_manager, 'mongo_manager': mongo_manager, 'crypto_manager':crypto_manager}
    )
    Logger.info("Registered route: /upload_files -> UploadFile")

    api.add_resource(
        ReadFile,
        '/read_file',
        resource_class_kwargs = {'config_manager': config_manager, 'mongo_manager': mongo_manager, 'crypto_manager':crypto_manager}
    )
    Logger.info("Registered route: /read_file -> ReadFile")

    api.add_resource(
        DeleteFile,
        '/delete_file',
        resource_class_kwargs={'config_manager': config_manager, 'mongo_manager': mongo_manager}
    )
    Logger.info("Registered route: /delete_file -> DeleteFile")

    api.add_resource(
        DeleteBook,
        '/delete_book',
        resource_class_kwargs={'config_manager': config_manager, 'mongo_manager': mongo_manager}
    )
    Logger.info("Registered route: /delete_book -> DeleteBook")

    api.add_resource(
        GetBookTranslations,
        '/get_book_translations',
        resource_class_kwargs = {'config_manager': config_manager, 'mongo_manager': mongo_manager }
    )
    Logger.info("Registered route: /get_book_translations -> GetBookTranslations")

    api.add_resource(
        GetBookLanguage,
        '/get_book_language',
        resource_class_kwargs = {'config_manager': config_manager, 'mongo_manager': mongo_manager }
    )
    Logger.info("Registered route: /get_book_language -> GetBookLanguage")

    # Book-related endpoints
    api.add_resource(
        GetBookInfo,
        '/get_books',
        resource_class_kwargs={'config_manager': config_manager, 'mongo_manager': mongo_manager}
    )
    Logger.info("Registered route: /get_books -> GetBookInfo")

    api.add_resource(
        TranslatePage,
        '/translate/page',
        resource_class_kwargs={'config_manager': config_manager, 'cache_manager': cache_manager, 'mongo_manager':mongo_manager, 'crypto_manager':crypto_manager}
    )
    Logger.info("Registered route: /translate/page -> TranslatePage")

    api.add_resource(
        TranslateAllPages,
        '/translate/page_all',
        resource_class_kwargs={'config_manager': config_manager, 'cache_manager': cache_manager,
                               'mongo_manager': mongo_manager, 'crypto_manager': crypto_manager}
    )
    Logger.info("Registered route: /translate/page_all -> TranslateAllPages")

    api.add_resource(
        TTSPage,
        '/tts/page',
        resource_class_kwargs={'config_manager': config_manager, 'cache_manager': cache_manager, 'mongo_manager':mongo_manager, 'crypto_manager':crypto_manager}
    )
    Logger.info("Registered route: /tts/page -> TTSPage")

    api.add_resource(
        GetBookPage,
        '/get_book_page',
        resource_class_kwargs = {'config_manager': config_manager, 'mongo_manager': mongo_manager, 'crypto_manager':crypto_manager}
    )
    Logger.info("Registered route: /get_book_page -> GetBookPage")

    # Translation Endpoints
    api.add_resource(
        TranslateFile,
        '/translate/file',
        resource_class_kwargs={'config_manager': config_manager, 'cache_manager': cache_manager}
    )
    Logger.info("Registered route: /translate/file -> TranslateFile")

    api.add_resource(
        TranslateText,
        '/translate/text',
        resource_class_kwargs={'config_manager': config_manager, 'cache_manager': cache_manager}
    )
    Logger.info("Registered route: /translate/text -> TranslateText")

    api.add_resource(
        ModelTranslation,
        '/translation/models',
        resource_class_kwargs={'config_manager': config_manager, 'cache_manager': cache_manager}
    )
    Logger.info("Registered route: /translation/models -> ModelTranslation")

    # TTS Endpoints
    api.add_resource(
        TTS,
        '/tts',
        resource_class_kwargs={'config_manager': config_manager, 'cache_manager': cache_manager}
    )
    Logger.info("Registered route: /tts -> TTS")
    api.add_resource(
        LanguageTTS,
        '/tts/languages',
        resource_class_kwargs={'config_manager': config_manager, 'cache_manager': cache_manager}
    )
    Logger.info("Registered route: /tts/languages -> LanguageTTS")
    api.add_resource(
        ModelTTS,
        '/tts/models',
        resource_class_kwargs={'config_manager': config_manager, 'cache_manager': cache_manager}
    )
    Logger.info("Registered route: /tts/models -> ModelTTS")

    api.add_resource(
        SpeakerTTS,
        '/tts/speakers',
        resource_class_kwargs={'config_manager': config_manager, 'cache_manager': cache_manager}
    )
    Logger.info("Registered route: /tts/speakers -> SpeakerTTS")

    ## STT Endpoint
    api.add_resource(
        SpeechToText,
        '/stt',
        resource_class_kwargs={'config_manager': config_manager, 'cache_manager': cache_manager}
    )
    Logger.info("Registered route: /stt -> SpeechToText")

    # Docker Healthcheck Endpoint
    api.add_resource(
        HealthCheck,
        '/health',
        resource_class_kwargs={'config_manager': config_manager, 'cache_manager': cache_manager}
    )
    Logger.info("Registered route: /health -> HealthCheck")

    # User-related endpoints
    api.add_resource(
        LoginUser,
        '/login',
        resource_class_kwargs={'config_manager': config_manager, 'mongo_manager': mongo_manager, 'crypto_manager':crypto_manager}
        )
    Logger.info("Registered route: /login -> LoginUser")


    api.add_resource(
        RegisterUser,
        '/register',
        resource_class_kwargs = {'config_manager': config_manager, 'mongo_manager': mongo_manager, 'crypto_manager':crypto_manager}
        ),
    Logger.info("Registered route: /register -> RegisterUser")
