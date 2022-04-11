"""
This is a module for constants used in the whole project.
"""

import os


# Courts
COURTS = {
    "1": "24-58-2",
    "3": "24-5-3",
    "4": "24-5-4",
    "6": "24-5-6",
    "7": "24-5-7",
    "8": "24-5-8",
    "9": "24-5-9",
    "10": "24-5-10",
    "11": "24-5-11",
}

# Csv
OUT_CSV_NAMES = [
    "full_id",
    "type",
    "confidence"
]

RAW_CSV_NAMES = [
    "court",
    "old_num",
    "cnj_num",
    "judge",
    "pub_date",
    "full_id",
    "file_id",
    "file_hash",
    "url"
]

TRAIN_CSV_NAMES = [
    "full_id",
    "type",
]

# Dirs
DATA_DIR = os.path.join(".", "data")
RAW_DIR = os.path.join(DATA_DIR, "raw")
TXT_DIR = os.path.join(DATA_DIR, "txt")
HTML_DIR = os.path.join(DATA_DIR, "html")
LOGS_DIR = os.path.join(DATA_DIR, "logs")
HUMAN_DIR = os.path.join(DATA_DIR, "human")
TRAIN_DIR = os.path.join(DATA_DIR, "train")
OUT_DIR = os.path.join(DATA_DIR, "out")

# Files
CSV_DATA_PATH = os.path.join(DATA_DIR, "data.csv")
TRAIN_DATA_PATH = os.path.join(TRAIN_DIR, "train.csv")
FULL_TRAIN_DATA_PATH = os.path.join(TRAIN_DIR, "full.csv")


if __name__ == "__main__":
    pass
