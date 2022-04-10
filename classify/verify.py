from typing import Dict
import os
import sys

import pandas as pd


DATA_DIR = os.path.join("..", "data")
TXT_DIR = os.path.join("sentencas", "txt")


def main():
    try:
        filename = sys.argv[1]
    except IndexError:
        filename = "output.csv"

    data_path = os.path.join(DATA_DIR, filename)
    df = pd.read_csv(data_path, sep=";", names=["fileid", "type", "confidence"])
    df = df.astype({"type": str})
    df = df[df.type != "1"]
    files = [f"{f}.txt" for f in df["fileid"]]
    types = list(df["type"])
    confs = list(df["confidence"])

    output = {}

    for file, _type, conf in zip(files, types, confs):
        filepath = os.path.join(DATA_DIR, TXT_DIR, file)
        with open(filepath) as f:
            content = f.read()
        print(f"{content}\n\nSentença classificada como: {_type} com confiança de {conf}.")
        verified_type = int(input("Insira o tipo correto da sentença: 1. Condenatória   2. Absolutória  3. Neutra\n"))
        fileid = file.replace(".txt", "")
        output[fileid] = verified_type

    save_verified_csv(output)


def save_verified_csv(data: Dict[str, int]):
    prev_csvs = [f for f in os.listdir(DATA_DIR) if f.startswith("train") and f.endswith(".csv")]
    csvs_count = len(prev_csvs)
    outpath = os.path.join(DATA_DIR, f"train_{csvs_count}.csv")
    with open(outpath, "w") as f:
        f.write("\n".join([f"{fileid};{_type}" for fileid, _type in data.items()]))


if __name__ == "__main__":
    main()
