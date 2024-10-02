import sys
import os
import logging


class AppLogger:
    """Creates a class for logging. The appropriate logging level can be set using the
    environmental variable APP_LOG_LEVEL."""

    _LOG_DEFAULT_LEVEL = "INFO"

    def __init__(self, logger_name: str, log_level: str = None) -> None:
        """Constructor for the App Logger. By default, the logging level is set to INFO.

        Args:
            logger_name (str): the name for the logger
            log_level (str): the logging level for the logger, e.g. DEBUG, INFO, etc. (Optional)
        """
        self.logger_name = logger_name

        if log_level is not None:
            self.log_level = log_level
        else:
            self.log_level = self.set_log_level_from_env()

    def set_log_level_from_env(self) -> str:
        """
        Sets the logging level. If logging level was provided, use that; Otherwise, sets the logging
        level from the environmental variable APP_LOG_LEVEL. If that is not set, uses the default logging level.

        Returns:
            str: the logging level
        """
        log_level = os.getenv("APP_LOG_LEVEL")

        if log_level is not None and log_level.upper() in logging._nameToLevel.keys():
            log_level = log_level.upper()
        else:
            log_level = AppLogger._LOG_DEFAULT_LEVEL.upper()
        return logging.getLevelName(log_level)

    def get_logger(self) -> logging.Logger:
        """Instantiates and returns a new logger. THe logger will send all of its output
        to sys.stdout.

        Returns:
            logging.Logger: an instance of the class logger
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
