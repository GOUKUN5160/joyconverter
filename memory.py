import os
import pickle
import hashlib
import logger as lg
from config import EXTENSION, SAVE_DIR

logger = lg.get_logger("memory")

def _get_hash(data: str) -> str:
    return hashlib.sha1(data.encode()).hexdigest()

def _check_save_dir() -> None:
    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)

def _get_path(file_name: str) -> str:
    _check_save_dir()
    return os.path.join(SAVE_DIR, file_name)

def save(key: str, obj: object) -> None:
    key = _get_hash(key)
    with open(_get_path(f"{key}.{EXTENSION}"), "wb") as f:
        pickle.dump(obj, f)
    logger.debug(f"Saved: {key}")

def load(key: str) -> object | None:
    key = _get_hash(key)
    path = _get_path(f"{key}.{EXTENSION}")
    logger.debug(f"Load: {key}")
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        return pickle.load(f)
