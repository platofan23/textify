from backend.app.utils import Logger  # Import the Logger class
Logger.info("Starting the application initialization process.")
# Setting up Logger
Logger.SHOW_ERRORS = True
Logger.SHOW_WARNINGS = True
Logger.SHOW_INFO = True
Logger.SHOW_DEBUG = True


from flask_restful import Api
from backend.app.start import register_routes, preload_models, run_tests, create_app

Logger.info("Initializing application components...")

# Initialize the Flask application and its dependencies.
app, config_manager, cache_manager, mongo_manager, crypto_manager = create_app()
Logger.info("Flask application and dependencies initialized successfully.")

# Initialize the API and register the endpoints.
api = Api(app)
register_routes(api, config_manager, cache_manager, mongo_manager, crypto_manager)
Logger.info("API routes registered successfully.")

# Run unit tests before starting the application (uncomment the next line if tests should run).
Logger.info("Running unit tests before application startup.")
# run_tests()

# Preload translation and TTS models.
Logger.info("Preloading models for translation and TTS services.")
preload_models(config_manager, cache_manager)

Logger.info("Application startup process completed successfully.")

# Start the Flask application.
if __name__ == '__main__':
    Logger.info("Starting the Flask application.")
    port = config_manager.get_config_value('REST', 'PORT', int, default=5555)
    host = config_manager.get_config_value('REST', 'HOST', str, default='127.0.0.1')
    Logger.info(f"Flask application running on {host}:{port}")
    app.run(host=host, port=port, debug=False)
