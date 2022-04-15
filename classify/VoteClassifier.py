"""
This modules provides the VoteClassifier class which is used
to combine the classifications provided from different classifiers.
"""

from statistics import mode
from typing import Dict
from typing import List
from typing import Tuple
from typing import Union

from nltk.classify import ClassifierI
from nltk.classify.scikitlearn import SklearnClassifier


class VoteClassifier(ClassifierI):
    def __init__(self, classifiers: List[SklearnClassifier]):
        self._classifiers = classifiers

    def votes(self, features):
        return [c.classify(features) for c in self._classifiers]

    def safe_classify(
        self,
        features: Dict[str, bool],
        min_confidence: float
    ) -> Union[Tuple[int, float], Tuple[None, None]]:
        """
        Classifies the features with min_confidence.
        """
        votes = self.votes(features)
        most_voted = mode(votes)
        confidence = votes.count(most_voted) / len(votes)
        return (most_voted, confidence) if confidence >= min_confidence else (None, None)

    def classify(self, features: Dict[str, bool]) -> List[int]:
        """
        This method is only used in training to check accuracy.
        """
        return mode(self.votes(features))
