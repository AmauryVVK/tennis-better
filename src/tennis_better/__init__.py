import logging
from pathlib import Path

import colorlog

__all__ = ["logger", "root_folder"]


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


logger = _setup_logger()
root_folder = _get_root()
