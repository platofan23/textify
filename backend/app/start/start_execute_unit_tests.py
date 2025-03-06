import pytest
from backend.app.utils.util_logger import Logger  # Import the Logger class

def run_tests():
    """
    Executes unit tests before starting the application.

    Ensures all tests run and results are fully displayed, even if some tests fail.
    """
    Logger.info("Starting unit tests before application launch...")

    # Run pytest with short tracebacks, verbose output, and do not stop on first failure.
    exit_code = pytest.main([
        "--tb=short",  # Use short tracebacks for concise output.
        "-v",          # Verbose output for detailed test results.
        "--maxfail=0", # Do not stop after the first failure.
        "./tests/"     # Directory containing the tests.
    ])

    if exit_code != 0:
        Logger.error(f"Unit tests failed (exit code: {exit_code}). Please review the test output above.")
    else:
        Logger.info("All unit tests passed. Proceeding with application startup...")
