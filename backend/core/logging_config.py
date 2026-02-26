import logging
import sys
import os
from colorlog import ColoredFormatter

def setup_logging():
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()

    # Define the color scheme and format
    # log_color specifies the color of the level name and message
    formatter = ColoredFormatter(
        "%(log_color)s%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        reset=True,
        log_colors={
            'DEBUG':    'cyan',
            'INFO':     'green',
            'WARNING':  'yellow',
            'ERROR':    'red',
            'CRITICAL': 'red,bg_white',
        },
        secondary_log_colors={},
        style='%'
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level))
    
    # Remove existing handlers to avoid duplicate logs
    if logger.hasHandlers():
        logger.handlers.clear()
        
    logger.addHandler(handler)

    # Prevent logs from libraries from being too noisy
    if log_level != "DEBUG":
        logging.getLogger("uvicorn").setLevel(logging.WARNING)
        logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

# Create a specific logger for our application
logger = logging.getLogger("evaluator")