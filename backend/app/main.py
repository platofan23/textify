from backend.app.utils import Logger  # Importiere die Logger-Klasse
Logger.info("Starting the application initialization process.")
# Setting up Logger
Logger.SHOW_ERRORS = True
Logger.SHOW_WARNINGS = True
Logger.SHOW_INFO = False
Logger.SHOW_DEBUG = True


from flask_restful import Api

from backend.app.start import register_routes, preload_models, run_tests, create_app


# Initialize Flask app
app, config_manager, cache_manager = create_app()
Logger.info("Flask application and dependencies initialized successfully.")

# Initialize API and register endpoints
api = Api(app)
register_routes(api, config_manager, cache_manager)
Logger.info("API routes registered successfully.")


# Run unit tests
Logger.info("Running unit tests before application startup.")
#run_tests()

# Preload models
Logger.info("Preloading models for translation services.")
preload_models(config_manager, cache_manager)

Logger.info("Application startup process completed successfully.")

# Start the Flask application
if __name__ == '__main__':
    Logger.info("Starting the Flask application.")
    port = config_manager.get_config_value('REST', 'PORT', int, default=5555)
    host = config_manager.get_config_value('REST', 'HOST', str, default='127.0.0.1')
    Logger.info(f"Flask application running on {host}:{port}")
    app.run(host=host, port=port, debug=False)
