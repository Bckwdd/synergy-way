import logging
import os
from logging.handlers import TimedRotatingFileHandler

from core.config import settings

LOG_DIR = settings.LOG_DIR
LOG_FILE = os.path.join(LOG_DIR, "logs.log")

os.makedirs(LOG_DIR, exist_ok=True)


def setup_logging():
    """
    Configure application-wide logging with both file and console output.

    Logging configuration:
    - Level: INFO
    - Format: `YYYY-MM-DD HH:MM:SS [LEVEL] logger_name: message`
    - File handler: Rotates daily at midnight, keeps 30 backups, UTF-8 encoding
    - Console handler: Mirrors the same format to stdout

    Returns:
        logging.Logger: The root logger instance configured with handlers.
    """
    logger = logging.getLogger()

    log_level = logging.DEBUG if settings.DEBUG else logging.INFO
    logger.setLevel(log_level)

    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )

    file_handler = TimedRotatingFileHandler(
        LOG_FILE, when="midnight", interval=1, backupCount=30, encoding="utf-8"
    )
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
