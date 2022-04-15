"""
This is a module for csv related util functions.
"""

from datetime import datetime
from typing import List
import os

import pandas as pd

from constants import CSV_DATA_PATH
from constants import DATA_DIR
from constants import FULL_TRAIN_DATA_PATH
from constants import RAW_CSV_NAMES
from constants import RAW_DIR
from constants import TXT_DIR


def save_list_as_csv(folder: str, name_prefix: str, data: List[str]) -> str:
    """
    Saves a list of strings as a .csv file with a unique filename.
    Each element of the list will be written as a line in the file.
    Returns the saved file path.
    """
    now = str(datetime.utcnow().timestamp()).replace(".", "")
    filepath = os.path.join(folder, f"{name_prefix}_{now}.csv")
    with open(filepath, "w") as f:
        f.write("\n".join(data))
    return filepath


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


def get_dataframe() -> pd.DataFrame:
    """
    Reads the .csv file containing the scrapped verdicts information
    and loads it into a pandas dataframe. Filters the dataframe,
    removing any verdicts which text wasn't sucessfully downloaded.
    Returns the filtered dataframe.
    """
    downloaded_files = [f.replace(".txt", "") for f in os.listdir(TXT_DIR)]
    df = pd.read_csv(CSV_DATA_PATH, sep=";", names=RAW_CSV_NAMES)
    df = df[df["full_id"].isin(downloaded_files)]
    return df


def append_to_full_training_csv(data_path: str):
    """
    Appends verified data to the full training .csv file,
    checking if entry isn't already there.
    """
    new_entries = []

    with open(data_path) as f:
        new_csv_content = f.readlines()

    with open(FULL_TRAIN_DATA_PATH) as f:
        ids = [line.strip().split(";")[0] for line in f.readlines()]

    for line in new_csv_content:
        _id = line.strip().split(";")[0]
        if _id not in ids:
            new_entries.append(line.strip())

    if new_entries:
        with open(FULL_TRAIN_DATA_PATH, "a") as f:
            f.write("\n")
            f.write("\n".join(new_entries))
