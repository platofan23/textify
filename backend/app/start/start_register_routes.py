from backend.app.routes import UploadFile, DownloadFile, ReadFile, TranslateText, TranslateFile, RegisterUser, LoginUser

def register_routes(api, config_manager, cache_manager):
    """
    Registers all endpoints with the Flask-RESTful API.

    Args:
        api (Api): Flask-RESTful API instance.
        config_manager (ConfigManager): Configuration manager instance.
        cache_manager (CacheManager): Cache manager instance.
    """
    # File-related endpoints
    api.add_resource(UploadFile, '/upload_files')
    api.add_resource(DownloadFile, '/download_file')
    api.add_resource(ReadFile, '/read_file')

    # Translation endpoints
    api.add_resource(
        TranslateText,
        '/translate/text',
        resource_class_kwargs={'config_manager': config_manager, 'cache_manager': cache_manager}
    )
    api.add_resource(
        TranslateFile,
        '/translate/file',
        resource_class_kwargs={'config_manager': config_manager, 'cache_manager': cache_manager}
    )

    # User-related endpoints
    api.add_resource(RegisterUser, '/register')
    api.add_resource(LoginUser, '/login')
