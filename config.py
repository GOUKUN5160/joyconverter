import os

PROGRAM_NAME = "joyconverter"
EXTENSION = "jcd"
SAVE_DIR = os.path.join(os.path.expanduser("~"), f".{PROGRAM_NAME}")

def get_path(path: str) -> str:
    return os.path.join(os.path.dirname(__file__), path)
