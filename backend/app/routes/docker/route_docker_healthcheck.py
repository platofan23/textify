from flask_restful import Resource

from backend.app.utils import MongoDBManager
from backend.app.utils.util_logger import Logger


class HealthCheck(Resource):
    """
    HealthCheck endpoint for Docker and Load Balancer.
    Checks the application's status and returns HTTP 200 (OK) or HTTP 500 (Error).
    """

    def __init__(self, config_manager, cache_manager):
        """
        Initialize HealthCheck resource with configuration and cache managers.
        """
        self.config_manager = config_manager
        self.cache_manager = cache_manager
        Logger.info("HealthCheck service initialized.")

    def get(self):
        """
        Perform health checks on the database and cache.

        Returns:
            tuple: A dictionary with health status information and the HTTP status code.
        """
        health_status = {
            "status": "healthy",
            "database": "unknown",
            "cache": "unavailable",
            "cache_read_write": "error"
        }

        try:
            # Check Database Connection
            health_status["database"] = self._check_database_health()

            # Check Cache and Cache Read/Write operations
            cache_status = self._check_cache_health()
            health_status.update(cache_status)

            Logger.info(f"Healthcheck passed: {health_status}")
            return health_status, 200  # JSON Response with HTTP 200

        except Exception as e:
            Logger.error(f"Healthcheck failed: {str(e)}")
            return {"status": "unhealthy", "error": str(e)}, 500

    @staticmethod
    def _check_database_health():
        """
        Check the health of the MongoDB database.

        Returns:
            str: The database status, either 'unknown', 'error', or the healthy status.
        """
        try:
            db_manager = MongoDBManager()
            db_health = db_manager.check_health()
            return db_health.get("database", "unknown")
        except Exception as db_error:
            Logger.error(f"Database healthcheck failed: {str(db_error)}")
            return "error"

    def _check_cache_health(self):
        """
        Check the health of the cache including read/write operations.

        Returns:
            dict: A dictionary containing the cache status and read/write status.
        """
        cache_result = {
            "cache": "unavailable",
            "cache_read_write": "error"
        }
        try:
            if self.cache_manager.is_available():
                cache_result["cache"] = "available"

                # Test cache read/write
                test_key = "healthcheck_test"
                test_value = "test_value"
                self.cache_manager.set(test_key, test_value)
                cached_value = self.cache_manager.get(test_key)

                cache_result["cache_read_write"] = "working" if cached_value == test_value else "error"

                # Remove test key from cache
                self.cache_manager.clear_cache()
        except Exception as cache_error:
            cache_result["cache"] = "error"
            cache_result["cache_read_write"] = "error"
            Logger.error(f"Cache healthcheck failed: {str(cache_error)}")
        return cache_result
