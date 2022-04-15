"""
This module initializes the classifiers wrapped in the
nltk api for sklearn classifiers and provides the CLASSIFIERS list
"""

from nltk.classify.scikitlearn import SklearnClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.naive_bayes import BernoulliNB
from sklearn.linear_model import SGDClassifier
from sklearn.svm import LinearSVC


def get_classifiers():
    mnb = SklearnClassifier(MultinomialNB())
    bnb = SklearnClassifier(BernoulliNB())
    sgd = SklearnClassifier(SGDClassifier())
    lsvc = SklearnClassifier(LinearSVC(dual=False))
    return [mnb, bnb, sgd, lsvc]


if __name__ == "__main__":
    pass
