import sys
import os
import logging

class AppLogger:
    """Creates a class for logginig

    Returns:
        logger: an instance of a logger
    """    
    _APP_DEFAULT_LEVEL = "INFO"

    def __init__(self, logger_name, log_level=None) -> None:
        self.logger_name = logger_name

        if log_level is not None:
            self.log_level = log_level
        else:
            self.log_level = self.set_log_level_from_env()

    def set_log_level_from_env(self) -> str:
        """Returns the textual or numeric representation of logging level level.

        Returns:
            str: logging level name
        """        
        log_level = os.getenv("APP_LOG_LEVEL")

        if log_level is not None and log_level.upper() in logging._nameToLevel.keys():
            log_level = log_level.upper()
        else:
            log_level = AppLogger._APP_DEFAULT_LEVEL.upper()
        return logging.getLevelName(log_level)

    def get_logger(self) -> logging.Logger:
        """Instantiates a logger instanec and sets parameters

        Returns:
            logging.Logger: returns an instance of the class logger
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