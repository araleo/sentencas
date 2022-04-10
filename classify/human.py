"""
This is a module to perform human classification
of the verdicts. Verdicts are printed on the screen
and the user is prompted to answer whick kind they are.
Results are stored in a .csv file.
"""

import os

import pandas as pd

from constants import HUMAN_DIR
from constants import TXT_DIR
from csv_utils import get_dataframe
from csv_utils import save_list_as_csv


def human_classification(sample_size: int, random_state: int):
    """
    Gets a sample of sample_size of the scrapped data, from
    a random state of random_state and prompts the user to
    classify it manually, saving the results in a .csv file.
    """
    df = get_dataframe()
    sample = df.sample(n=sample_size, random_state=random_state)
    classify_files(sample)


def classify_files(df: pd.DataFrame):
    """
    Walks through a datafrane and prompts the user to
    classify all listed files.
    """
    files = list(df["full_id"])
    classified = []
    for fileid in files:
        _type = classify_single_file(fileid)
        classified.append(f"{fileid};{_type}")
    save_list_as_csv(HUMAN_DIR, "human", classified)


def classify_single_file(fileid: str) -> int:
    """
    Reads a file and prompts the user to classify it.
    """
    filepath = os.path.join(TXT_DIR, f"{fileid}.txt")
    print_file(filepath)
    _type = prompt_user()
    return _type


def print_file(filepath: str):
    """
    Prints the file content to stdout.
    """
    with open(filepath) as f:
        content = f.read()
        print(content)


def prompt_user() -> int:
    """
    Prompts user for the verdict type and returns the answer as int.
    """
    print("\nQual é o tipo da sentença apresentada?")
    print("1. Condenatória  2. Absolutória  3. Neutra")
    ans = int(input())
    return ans


if __name__ == "__main__":
    pass
