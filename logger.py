"""
Application Logging Module

Provides a custom logging class for the LLM Voice Chat application with
configurable log levels via environment variables.

Features:
- Configurable logging level via APP_LOG_LEVEL environment variable
- Formatted output with timestamps to stdout
- Support for standard Python logging levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Automatic fallback to INFO level if no valid level is specified
- Per-module logger instances with consistent formatting
"""

import sys
import os
import logging


class AppLogger:
    """Custom logger class for the LLM Voice Chat application.

    Creates logger instances with configurable logging levels set via the
    APP_LOG_LEVEL environment variable. All log output is sent to stdout with
    a standardized timestamp format.

    Environment Variables:
        APP_LOG_LEVEL: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            Defaults to INFO if not set or if an invalid level is provided

    Attributes:
        logger_name (str): Name of the logger instance
        log_level (str): The logging level for this logger

    Example:
        >>> logger = AppLogger("my_module").get_logger()
        >>> logger.info("Application started")
        2025-11-19 12:00:00 INFO my_module: Application started
    """

    _LOG_DEFAULT_LEVEL = "INFO"

    def __init__(self, logger_name: str, log_level: str = None) -> None:
        """Initialize an AppLogger instance.

        Creates a logger with the specified name and optional log level. If no log
        level is provided, it will be loaded from the APP_LOG_LEVEL environment
        variable, defaulting to INFO if not set.

        Args:
            logger_name (str): Name identifier for the logger, typically the module name.
                Use os.path.splitext(os.path.basename(__file__))[0] to auto-generate
                from the current file.
            log_level (str, optional): Explicit logging level to use (DEBUG, INFO, WARNING,
                ERROR, CRITICAL). If None, reads from APP_LOG_LEVEL environment variable.
                Defaults to None.

        Example:
            >>> # Automatic module name
            >>> logger = AppLogger(os.path.splitext(os.path.basename(__file__))[0])
            >>> # Explicit name and level
            >>> logger = AppLogger("my_module", "DEBUG")
        """
        self.logger_name = logger_name

        if log_level is not None:
            self.log_level = log_level
        else:
            self.log_level = self.set_log_level_from_env()

    def set_log_level_from_env(self) -> str:
        """Determine the logging level from the APP_LOG_LEVEL environment variable.

        Reads the APP_LOG_LEVEL environment variable and validates it against Python's
        standard logging levels. Falls back to INFO if the variable is not set or
        contains an invalid value.

        Valid logging levels (case-insensitive):
            - DEBUG: Detailed information, typically for diagnosing problems
            - INFO: Confirmation that things are working as expected
            - WARNING: Indication of unexpected events or potential problems
            - ERROR: Serious problems that prevent functionality
            - CRITICAL: Critical problems that may cause the application to abort

        Returns:
            str: The validated logging level name (e.g., "DEBUG", "INFO", "WARNING")

        Environment Variables:
            APP_LOG_LEVEL: Desired logging level (case-insensitive). Falls back to
                INFO if not set or invalid.

        Example:
            >>> os.environ['APP_LOG_LEVEL'] = 'DEBUG'
            >>> logger = AppLogger("test")
            >>> logger.set_log_level_from_env()
            'DEBUG'
        """
        log_level = os.getenv("APP_LOG_LEVEL")

        if log_level is not None and log_level.upper() in logging._nameToLevel.keys():
            log_level = log_level.upper()
        else:
            log_level = AppLogger._LOG_DEFAULT_LEVEL.upper()
        return logging.getLevelName(log_level)

    def get_logger(self) -> logging.Logger:
        """Create and configure a Python logger instance.

        Instantiates a Python logging.Logger with the configured name and level,
        attached to a StreamHandler that outputs to stdout. The logger uses a
        standardized format with timestamps.

        Log Format:
            YYYY-MM-DD HH:MM:SS LEVEL logger_name: message

        Behavior:
            - Clears any existing handlers to prevent duplicate log messages
            - Sets propagate=False to prevent messages from bubbling up to root logger
            - Outputs an initial INFO message confirming the log level

        Returns:
            logging.Logger: Configured logger instance ready for use throughout
                the application

        Example:
            >>> logger = AppLogger("my_module").get_logger()
            >>> logger.debug("Debug message")
            >>> logger.info("Info message")
            >>> logger.warning("Warning message")
            >>> logger.error("Error message")

        Note:
            All log output is sent to sys.stdout, not stderr, for easier
            redirection and integration with other tools.
        """

        logger = logging.getLogger(self.logger_name)
        logger.setLevel(self.log_level)

        formatter = logging.Formatter(
            fmt="%(asctime)s %(levelname)s %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        if logger.hasHandlers():
            logger.handlers.clear()
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(self.log_level)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.propagate = False

        logger.info(f"Log level set to {logging.getLevelName(self.log_level)}.")

        return logger
