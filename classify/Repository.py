"""
This module provides the Repository class used to group up Verdicts.
"""

from __future__ import annotations
from typing import List
from typing import Set
import os

from classify.Verdict import Verdict
from constants import TXT_DIR


class Repository:

    def __init__(self, fileids: List[str], enum_value: int):
        self.repository = self.reader(fileids)
        self.enum_value = enum_value

    def reader(self, fileids: List[str]) -> Set[Verdict]:
        repo = set()
        for fileid in set(fileids):
            filepath = os.path.join(TXT_DIR, f"{fileid}.txt")
            with open(filepath) as f:
                content = f.read()
            repo.add(Verdict(content))
        return repo

    @property
    def tokens(self):
        tokens = []
        for s in self.repository:
            tokens.extend(s.tokens)
        return tokens
