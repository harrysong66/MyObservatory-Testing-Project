import logging
import os
from pathlib import Path
from typing import Optional


class LoggerManager:

    _loggers = {}

    @staticmethod
    def get_logger(name: str, log_level: Optional[str] = None) -> logging.Logger:

        if name in LoggerManager._loggers:
            return LoggerManager._loggers[name]

        # Create logger
        logger = logging.getLogger(name)
        
        # Set log level
        level = log_level or os.getenv("LOG_LEVEL", "INFO")
        logger.setLevel(getattr(logging, level.upper(), logging.INFO))

        # Prevent duplicate handlers
        if not logger.handlers:
            # Console handler
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            console_formatter = logging.Formatter(
                "%(asctime)s [%(levelname)8s] %(name)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )
            console_handler.setFormatter(console_formatter)
            logger.addHandler(console_handler)

            # File handler
            log_dir = Path(os.getenv("LOG_DIR", "logs"))
            log_dir.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.FileHandler(log_dir / "test_execution.log", encoding="utf-8")
            file_handler.setLevel(logging.DEBUG)
            file_formatter = logging.Formatter(
                "%(asctime)s [%(levelname)8s] %(name)s:%(lineno)d - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)

        LoggerManager._loggers[name] = logger
        return logger


def get_logger(name: str) -> logging.Logger:
    return LoggerManager.get_logger(name)
