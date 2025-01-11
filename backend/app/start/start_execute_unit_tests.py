import pytest

def run_tests():
    """
    Executes unit tests before starting the application.

    Ensures all tests are run and results are fully displayed, even if some tests fail.
    """
    print("Running unit tests before application start...")
    # Run pytest without stopping on failures
    exit_code = pytest.main([
        "--tb=short",  # Short traceback for concise output
        "-v",          # Verbose output for all test results
        "--maxfail=0", # Prevent stopping after failures
        "./tests/"    # Path to the tests directory
    ])

    if exit_code != 0:
        print(f"❌ Some tests failed (exit code: {exit_code}). Review the results above.")
    else:
        print("✅ All tests passed. Starting application...")
