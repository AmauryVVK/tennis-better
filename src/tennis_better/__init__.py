import logging

import colorlog

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
