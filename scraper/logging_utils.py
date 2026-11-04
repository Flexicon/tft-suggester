import logging
import os

DEFAULT_LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s %(levelname)s %(name)s: %(message)s"


def _log_level() -> int:
    level_name = os.getenv("LOG_LEVEL", DEFAULT_LOG_LEVEL).upper()
    return getattr(logging, level_name, logging.INFO)


def configure_logging() -> None:
    """Configure process-wide logging from the LOG_LEVEL environment variable."""
    logging.basicConfig(level=_log_level(), format=LOG_FORMAT)
