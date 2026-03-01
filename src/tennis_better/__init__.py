import logging
import os
from pathlib import Path

import colorlog
from dotenv import load_dotenv

__all__ = ["logger", "root_folder", "dict_db_paths"]


load_dotenv()
env = os.getenv("ENV")


def _setup_logger():
    """Configures the package-level logger."""

    handler = colorlog.StreamHandler()

    # The 'log_color' keyword maps colors to levels automatically
    handler.setFormatter(
        colorlog.ColoredFormatter(
            "%(log_color)s%(levelname)-8s | %(asctime)s | %(name)s | %(filename)s:%(lineno)s | %(funcName)s() | %(message)s%(reset)s",
            log_colors={
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "red,bg_white",
            },
        )
    )

    logger = logging.getLogger("tennis-better")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)

    return logger


def _get_root():
    """Calculate the project root relative to this file."""
    return Path(__file__).parent.parent.parent.resolve().as_posix()


def _get_dict_databases():
    """Return a dict with database connection paths"""
    if env == "LOCAL":
        db_name = os.getenv("DATABASE_PLAYER_URLS")
        return {"player_urls": Path(root_folder) / db_name}

    if env == "REMOTE":
        db_name = os.getenv("MOTHERDUCK_DATABASE")
        token = os.getenv("MOTHERDUCK_TOKEN")
        return {"player_urls": f"{db_name}?motherduck_token={token}"}


logger = _setup_logger()
root_folder = _get_root()
dict_db_paths = _get_dict_databases()
