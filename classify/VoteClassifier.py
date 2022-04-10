"""
This modules provides the VoteClassifier class which is used
to combine the classifications provided from different classifiers.
"""

from typing import Dict
from typing import List
from typing import Tuple
from typing import Union

from nltk.classify import ClassifierI
from nltk.classify.scikitlearn import SklearnClassifier


class VoteClassifier(ClassifierI):
    def __init__(self, classifiers: List[SklearnClassifier]):
        self._classifiers = classifiers
        self._categories = [i + 1 for i in range(len(classifiers))]

    def classify(self, features: Dict[str, bool]) -> List[int]:
        return [c.classify(features) for c in self._classifiers]

    def get_most_voted(self, votes: List[int]) -> int:
        v = {i: votes.count(i) for i in self._categories}
        return max(v, key=v.get)

    def confidence(self, votes: List[int], most_voted: int) -> float:
        return votes.count(most_voted) / len(votes)

    def safe_classify(self, features: Dict[str, bool], min_confidence: int) -> Union[Tuple[int, float], Tuple[None, None]]:
        votes = self.classify(features)
        most_voted = self.get_most_voted(votes)
        confidence = self.confidence(votes, most_voted)
        return most_voted, confidence if confidence >= min_confidence else None, None