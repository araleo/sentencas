"""
This module initializes the classifiers wrapped in the
nltk api for sklearn classifiers and provides the CLASSIFIERS list
"""

from nltk.classify.scikitlearn import SklearnClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import SGDClassifier
from sklearn.linear_model import RidgeClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC


def get_classifiers():
    mnb = SklearnClassifier(MultinomialNB())
    sgd = SklearnClassifier(SGDClassifier())
    lsvc = SklearnClassifier(LinearSVC(dual=False))
    rf = SklearnClassifier(RandomForestClassifier())
    ridge = SklearnClassifier(RidgeClassifier())
    return [mnb, sgd, lsvc, rf, ridge]


if __name__ == "__main__":
    pass
