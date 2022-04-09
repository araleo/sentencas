"""
This is the main module, which you should always run.

Usage:

python main.py <command>

Available commands:

- scrap
"""

import argparse
import os
import sys

from constants import COURTS
from csv_utils import merge_csvs
from scrap import scrap


COMMANDS = ["scrap", "merge"]


def main():

    parser = argparse.ArgumentParser(description="Usage: python main.py command")

    parser.add_argument("command", type=str, help=f"Available commands: {COMMANDS}")
    parser.add_argument("--court", type=str, help=f"Available courts: {list(COURTS.keys())}")
    parser.add_argument("--page", type=int, default=0, help=f"Starting page for the search")
    parser.add_argument("--dir", type=str, default="", help=f"Target directory, relative to the cwd")

    args = validate_args(parser)

    if args.command == "scrap":
        if args.court:
            scrap.search_court_from_page(args.court, args.page)
        else:
            scrap.search_all_courts()

    if args.command == "merge":
        merge_csvs()


def validate_args(parser: argparse.ArgumentParser) -> argparse.Namespace:
    args = parser.parse_args()

    if args.command not in COMMANDS:
        print("Usage: python main.py <command>")
        print("Available commands: ", COMMANDS)
        sys.exit(1)

    if args.court and args.court not in COURTS:
        print("Available courts: ", list(COURTS.keys()))
        sys.exit(2)

    if args.page < 0:
        print("Page must be greater than 0")
        sys.exit(3)

    return args


if __name__ == "__main__":
    main()
