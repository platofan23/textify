from backend.app.routes import DownloadFile, LoginUser, ModelTTS, ModelTranslation, ReadFile, RegisterUser, SpeakerTTS, \
    TranslateFile, TranslateText, TTS, UploadFile, HealthCheck
from backend.app.routes.route_tts_languages import LanguageTTS
from backend.app.utils.util_logger import Logger  # Import the Logger class
from backend.app.routes.route_get_books import GetBookInfo


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
        resource_class_kwargs={'config_manager': config_manager, 'mongo_manager': mongo_manager, 'crypto_manager':crypto_manager})
    Logger.info("Registered route: /download_file -> DownloadFile")

    api.add_resource(
        ReadFile,
        '/read_file',
        resource_class_kwargs = {'config_manager': config_manager, 'mongo_manager': mongo_manager, 'crypto_manager':crypto_manager}
    )
    Logger.info("Registered route: /read_file -> ReadFile")

    # Book-related endpoints
    api.add_resource(
        GetBookInfo,
        '/get_books',
        resource_class_kwargs={'config_manager': config_manager, 'mongo_manager': mongo_manager}
    )
    Logger.info("Registered route: /get_books -> GetBookInfo")

    # Translation endpoints
    api.add_resource(
        UploadFile,
        '/upload_files',
        resource_class_kwargs = {'config_manager': config_manager, 'mongo_manager': mongo_manager}
    )
    Logger.info("Registered route: /upload_files -> UploadFile")

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
        resource_class_kwargs={'config_manager': config_manager, 'mongo_manager': mongo_manager})
    Logger.info("Registered route: /login -> LoginUser")


    api.add_resource(
        RegisterUser,
        '/register',
        resource_class_kwargs = {'config_manager': config_manager, 'mongo_manager': mongo_manager}
        ),
    Logger.info("Registered route: /register -> RegisterUser")
