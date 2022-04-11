"""
This is the main module, which you should always run.

Usage:

python main.py <command>

Available commands:

- scrap
- merge
- download
- human
- classify
- verify
"""

from datetime import datetime
import argparse
import sys

from classify import classify
from classify import human
from constants import COURTS
from csv_utils import merge_csvs
from scrap import scrap


COMMANDS = ["scrap", "merge", "download", "human", "classify"]


def main():
    parser = argparse.ArgumentParser(description="Usage: python main.py command")
    parser = register_args(parser)
    args = validate_args(parser)
    switch_args(args)


def register_args(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    parser.add_argument("command", type=str, help=f"Available commands: {COMMANDS}")
    parser.add_argument("--court", type=str, help=f"Available courts: {list(COURTS.keys())}")
    parser.add_argument("--page", type=int, default=0, help=f"Starting page for the search, defaults to 0")
    parser.add_argument("--dir", type=str, default="", help=f"Target directory, relative to the cwd")
    parser.add_argument("--sample", type=int, default=50, help=f"Sample size")
    parser.add_argument("--state", type=int, default=int(datetime.utcnow().timestamp()), help=f"Random state")
    parser.add_argument("--train", type=str, default="", help=f"Name of the training data file")
    parser.add_argument("--trainsize", type=float, default=0.75, help=f"Size of the training set. Must be between 0 and 1")
    return parser


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

    if args.trainsize < 0 or args.trainsize > 1:
        print("Train size must be between 0 and 1")
        sys.exit(3)

    return args


def switch_args(args: argparse.Namespace):
    if args.command == "scrap":
        if args.court:
            scrap.search_court_from_page(args.court, args.page)
        else:
            scrap.search_all_courts()

    elif args.command == "merge":
        merge_csvs()

    elif args.command == "download":
        scrap.download_all_verdicts()

    elif args.command == "human":
        human.human_classification(args.sample, args.state)

    elif args.command == "classify":
        if args.sample != 0:
            classify.classify("sample", args.train, args.sample, args.state, args.trainsize)
        else:
            classify.classify("corpus", args.train)


if __name__ == "__main__":
    main()
