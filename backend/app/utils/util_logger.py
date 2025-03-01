import inspect
import sys

class Logger:
    _instance = None

    # Control which messages to show
    SHOW_INFO = True
    SHOW_WARNINGS = True
    SHOW_ERRORS = True
    SHOW_DEBUG = True

    # ANSI escape codes for colors
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    def __new__(cls):

        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        pass

    @staticmethod
    def info(message):
        if not Logger.SHOW_INFO:
            return
        print(Logger()._colorize(Logger._log(message, "INFO"), Logger.OKBLUE), end=end)

    @staticmethod
    def debug(message):
        if not Logger.SHOW_DEBUG:
            return
        print(Logger()._colorize(Logger._log(message, "DEBUG"), Logger.OKGREEN))

    @staticmethod
    def warning(message):
        print(Logger._colorize(Logger._log(message, "WARNING"), Logger.WARNING))

    @staticmethod
    def error(message):
        print(Logger._colorize(Logger._log(message, "ERROR"), Logger.FAIL))

    @staticmethod
    def set_show_messages(show_messages):
        Logger.SHOW_INFO = show_messages

    @staticmethod
    def set_show_warnings(show_warnings):
        Logger.SHOW_WARNINGS = show_warnings

    @staticmethod
    def set_show_errors(show_errors):
        Logger.SHOW_ERRORS = show_errors

    @staticmethod
    def set_show_all(show_messages, show_warnings, show_errors):
        Logger.SHOW_INFO = show_messages
        Logger.SHOW_WARNINGS = show_warnings
        Logger.SHOW_ERRORS = show_errors

    @staticmethod
    def _log(message, prefix="LOG"):
        caller_frame = inspect.stack()[2]
        caller_info = f"File \"{caller_frame.filename.replace(r'\\', '/')}\", line {caller_frame.lineno}"
        return f"{prefix}: {message} \t(called from {caller_info})"

    @staticmethod
    def _colorize(message, color):
        return f"{color}{message}{Logger.ENDC}"