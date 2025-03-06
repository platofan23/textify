import inspect

class Logger:
    _instance = None

    # Flags for controlling which messages to display.
    SHOW_INFO = True
    SHOW_WARNINGS = True
    SHOW_ERRORS = True
    SHOW_DEBUG = True

    # ANSI escape codes for terminal colors.
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
        """
        Implements the singleton pattern for the Logger class.
        """
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        # No additional initialization required.
        pass

    @staticmethod
    def info(message, end="\n"):
        """
        Logs an informational message if SHOW_INFO is True.

        Args:
            message (str): The message to log.
            end (str, optional): The end character for the print statement. Defaults to "\n".
        """
        if not Logger.SHOW_INFO:
            return
        print(Logger()._colorize(Logger._log(message, "INFO"), Logger.OKBLUE), end=end)

    @staticmethod
    def debug(message):
        """
        Logs a debug message if SHOW_DEBUG is True.

        Args:
            message (str): The debug message to log.
        """
        if not Logger.SHOW_DEBUG:
            return
        print(Logger()._colorize(Logger._log(message, "DEBUG"), Logger.OKGREEN))

    @staticmethod
    def warning(message):
        """
        Logs a warning message.

        Args:
            message (str): The warning message to log.
        """
        print(Logger._colorize(Logger._log(message, "WARNING"), Logger.WARNING))

    @staticmethod
    def error(message):
        """
        Logs an error message.

        Args:
            message (str): The error message to log.
        """
        print(Logger._colorize(Logger._log(message, "ERROR"), Logger.FAIL))

    @staticmethod
    def set_show_messages(show_messages):
        """
        Sets whether informational messages should be displayed.

        Args:
            show_messages (bool): True to display info messages; False to hide them.
        """
        Logger.SHOW_INFO = show_messages

    @staticmethod
    def set_show_warnings(show_warnings):
        """
        Sets whether warning messages should be displayed.

        Args:
            show_warnings (bool): True to display warning messages; False to hide them.
        """
        Logger.SHOW_WARNINGS = show_warnings

    @staticmethod
    def set_show_errors(show_errors):
        """
        Sets whether error messages should be displayed.

        Args:
            show_errors (bool): True to display error messages; False to hide them.
        """
        Logger.SHOW_ERRORS = show_errors

    @staticmethod
    def set_show_all(show_messages, show_warnings, show_errors):
        """
        Sets whether informational, warning, and error messages should be displayed.

        Args:
            show_messages (bool): True to display info messages.
            show_warnings (bool): True to display warning messages.
            show_errors (bool): True to display error messages.
        """
        Logger.SHOW_INFO = show_messages
        Logger.SHOW_WARNINGS = show_warnings
        Logger.SHOW_ERRORS = show_errors

    @staticmethod
    def _log(message, prefix="LOG"):
        """
        Formats a log message with a given prefix and caller information.

        Args:
            message (str): The message to log.
            prefix (str): The log level prefix (e.g., INFO, DEBUG).

        Returns:
            str: The formatted log message.
        """
        caller_frame = inspect.stack()[2]
        caller_info = f"File \"{caller_frame.filename.replace(r'\\', '/')}\", line {caller_frame.lineno}"
        return f"{prefix}: {message} \t(called from {caller_info})"

    @staticmethod
    def _colorize(message, color):
        """
        Wraps a message in ANSI escape codes for terminal colorization.

        Args:
            message (str): The message to colorize.
            color (str): The ANSI color code.

        Returns:
            str: The colorized message.
        """
        return f"{color}{message}{Logger.ENDC}"
