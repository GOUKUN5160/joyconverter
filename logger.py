import logging
from logging.handlers import TimedRotatingFileHandler
import os
from config import SAVE_DIR

def get_logger(name):
    logger = logging.getLogger("JoyConverter." + name)
    logger.setLevel(logging.DEBUG)
    if not logger.hasHandlers():
        formatter = logging.Formatter("[%(levelname)s] %(asctime)s - %(name)s - %(message)s")
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        save_dir = os.path.join(SAVE_DIR, "logs")
        os.makedirs(save_dir, exist_ok=True)
        fh = TimedRotatingFileHandler(os.path.join(save_dir, f"{name}.log"), when="midnight", backupCount=5)
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    return logger
