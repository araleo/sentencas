"""
This module provides the Verdict class which is used to wrap
each verdict text, tokens and features.
"""

from typing import Dict
from typing import List
import string

import nltk


STOP = nltk.corpus.stopwords.words("portuguese") + list(string.punctuation)


class Verdict:

    def __init__(self, text: str):
        self.text = self.preprocess_text(text)

    def preprocess_text(self, text: str) -> str:
        return " ".join(w.lower().strip() for w in text.split())

    @property
    def tokens(self) -> List[str]:
        return [t.lower() for t in nltk.word_tokenize(self.text) if t.lower() not in STOP]

    def features(self, word_features: List[str]) -> Dict[str, bool]:
        tokens_set = set(self.tokens)
        return {word: word in tokens_set for word in word_features}
