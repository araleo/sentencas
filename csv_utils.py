"""
This is a module for csv related util functions.
"""

from datetime import datetime
from typing import List
import os

from constants import DATA_DIR
from constants import RAW_DIR


def save_list_as_csv(folder: str, name_prefix: str, data: List[str]):
    """
    Saves a list of strings as a .csv file with a unique filename.
    Each element of the list will be written as a line in the file.
    """
    now = str(datetime.utcnow().timestamp()).replace(".", "")
    filepath = os.path.join(folder, f"{name_prefix}_{now}.csv")
    with open(filepath, "w") as f:
        f.write("\n".join(data))


def merge_csvs(folder: str = RAW_DIR, prefix: str = "raw"):
    """
    Merges the raw csv files scrapped from the search page
    into one output file.

    We are storing temporarily all the csvs data in memory to
    avoid performing tens of thousands of file operations.
    """
    files = [f for f in os.listdir(folder) if f.startswith(prefix) and f.endswith(".csv")]

    data = []
    for _file in files:
        filepath = os.path.join(folder, _file)
        with open(filepath) as f:
            data.append(f.read())

    data = remove_repeated_lines(data)
    outpath = os.path.join(DATA_DIR, "data.csv")
    with open(outpath, "w") as f:
        f.write("\n".join(data))


def remove_repeated_lines(data: List[str]) -> List[str]:
    """
    Removes repeated data entries from the data list.
    A data entry is considered equal to another if both
    have the same full_id field (position 5, 0 indexed).
    """
    found_ids = set()
    filtered_data = []

    for line in data:
        full_id = line.split(";")[5]
        if full_id in found_ids:
            continue
        found_ids.add(full_id)
        filtered_data.append(line)

    return filtered_data


