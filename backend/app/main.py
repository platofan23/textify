from flask_restful import Api
from backend.app.start import register_routes, preload_models, run_tests, create_app

# Initialize Flask app
app, config_manager, cache_manager = create_app()

# Initialize API and register endpoints
api = Api(app)
register_routes(api, config_manager, cache_manager)


# Start the Flask application
if __name__ == '__main__':
    run_tests()  # 1. Run unit tests
    preload_models(config_manager, cache_manager)  # 2. Load models
    port = config_manager.get_config_value('REST', 'PORT', int, default=5555)
    host = config_manager.get_config_value('REST', 'HOST', str, default='127.0.0.1')
    app.run(host=host, port=port, debug=True)
