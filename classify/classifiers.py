"""
This module initializes the classifiers wrapped in the
nltk api for sklearn classifiers and provides the CLASSIFIERS list
"""

from nltk.classify.scikitlearn import SklearnClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.naive_bayes import BernoulliNB
from sklearn.linear_model import SGDClassifier
from sklearn.svm import LinearSVC


MNB = SklearnClassifier(MultinomialNB())
BNB = SklearnClassifier(BernoulliNB())
SGD = SklearnClassifier(SGDClassifier())
LSVC = SklearnClassifier(LinearSVC(dual=False))
CLASSIFIERS = [MNB, BNB, SGD, LSVC]


if __name__ == "__main__":
    pass
