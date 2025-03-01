from flask_restful import Resource
from flask import jsonify

from backend.app.utils import MongoDBManager
from backend.app.utils.util_logger import Logger


class HealthCheck(Resource):
    """
    HealthCheck endpoint for Docker and Load Balancer.
    Checks the application's status and returns HTTP 200 (OK) or HTTP 500 (Error).
    """
    def __init__(self, config_manager, cache_manager):
        self.config_manager = config_manager
        self.cache_manager = cache_manager
        Logger.info("HealthCheck service initialized.")

    def get(self):
        """
        Performs health checks on the database and cache.
        """
        health_status = {
            "status": "healthy",
            "database": "unknown",
            "cache": "unavailable",
            "cache_read_write": "error"
        }

        try:
            # Check Database Connection
            try:
                db_manager = MongoDBManager()
                db_health = db_manager.check_health()
                health_status["database"] = db_health.get("database", "unknown")
            except Exception as db_error:
                health_status["database"] = "error"
                Logger.error(f"❌ Database healthcheck failed: {str(db_error)}")

            # Check Cache
            try:
                if self.cache_manager.is_available():
                    health_status["cache"] = "available"

                    # Test cache read/write
                    test_key = "healthcheck_test"
                    test_value = "test_value"
                    self.cache_manager.set(test_key, test_value)
                    cached_value = self.cache_manager.get(test_key)

                    if cached_value == test_value:
                        health_status["cache_read_write"] = "working"
                    else:
                        health_status["cache_read_write"] = "error"

                    # Remove test key
                    self.cache_manager.clear_cache()

            except Exception as cache_error:
                health_status["cache"] = "error"
                health_status["cache_read_write"] = "error"
                Logger.error(f"❌ Cache healthcheck failed: {str(cache_error)}")

            Logger.info(f"✅ Healthcheck passed: {health_status}")
            return health_status, 200  # Fix für JSON Response

        except Exception as e:
            Logger.error(f"❌ Healthcheck failed: {str(e)}")
            return {"status": "unhealthy", "error": str(e)}, 500


