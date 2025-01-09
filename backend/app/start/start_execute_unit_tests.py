import pytest
import sys

def run_tests():
    """
    Executes unit tests before starting the application.

    Exits the application if any test fails.
    """
    print("Running unit tests before application start...")
    exit_code = pytest.main(["-q", "../tests/"])
    if exit_code != 0:
        print("❌ Unit tests failed. Application will not start.")
        sys.exit(exit_code)
    else:
        print("✅ All tests passed. Starting application...")
