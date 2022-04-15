"""
This module contains the enums for the verdicts types
"""

from enum import Enum


class ResultTypeEnum(Enum):
    CONDENATORIA = 1
    ABSOLUTORIA = 2
    NEUTRA = 3


class CrimeTypeEnum(Enum):
    OUTROS = 1
    PATRIMONIO = 2


if __name__ == "__main__":
    pass
