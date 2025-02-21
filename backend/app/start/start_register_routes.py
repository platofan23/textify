from backend.app.routes import UploadFile, DownloadFile, ReadFile, TranslateText, TranslateFile, RegisterUser, \
    LoginUser, GetBookInfo
from backend.app.utils.util_logger import Logger  # Importiere die Logger-Klasse

def register_routes(api, config_manager, cache_manager):
    """
    Registers all endpoints with the Flask-RESTful API.

    Args:
        api (Api): Flask-RESTful API instance.
        config_manager (ConfigManager): Configuration manager instance.
        cache_manager (CacheManager): Cache manager instance.
    """
    Logger.info("Registering routes with the Flask-RESTful API.")

    # File-related endpoints
    api.add_resource(UploadFile, '/upload_files')
    Logger.info("Registered route: /upload_files -> UploadFile")

    api.add_resource(DownloadFile, '/download_file')
    Logger.info("Registered route: /download_file -> DownloadFile")

    api.add_resource(ReadFile, '/read_file')
    Logger.info("Registered route: /read_file -> ReadFile")

    api.add_resource(GetBookInfo, '/get_books')
    Logger.info("Registered route: /get_books -> GetBookInfo")

    # Translation endpoints
    api.add_resource(
        TranslateText,
        '/translate/text',
        resource_class_kwargs={'config_manager': config_manager, 'cache_manager': cache_manager}
    )
    Logger.info("Registered route: /translate/text -> TranslateText")

    api.add_resource(
        TranslateFile,
        '/translate/file',
        resource_class_kwargs={'config_manager': config_manager, 'cache_manager': cache_manager}
    )
    Logger.info("Registered route: /translate/file -> TranslateFile")

    # User-related endpoints
    api.add_resource(RegisterUser, '/register')
    Logger.info("Registered route: /register -> RegisterUser")

    api.add_resource(LoginUser, '/login')
    Logger.info("Registered route: /login -> LoginUser")
