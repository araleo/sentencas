"""
Module to classify the textual content of the verdicts
using nltk and sklearn.
"""

from math import floor
from typing import Dict
from typing import List
from typing import Tuple
import os
import random

import nltk
import pandas as pd

from classify.classifiers import get_classifiers
from classify import human
from classify.Enums import CrimeTypeEnum
from classify.Enums import ResultTypeEnum
from classify.Repository import Repository
from classify.Verdict import Verdict
from classify.VoteClassifier import VoteClassifier
from constants import CONFIDENCE
from constants import DEFAULT_SAMPLE
from constants import FEATS_LEN
from constants import FULL_TRAIN_DATA_PATH
from constants import OUT_CSV_NAMES
from constants import OUT_DIR
from constants import TRAIN_CSV_NAMES
from constants import TRAIN_DIR
from constants import TXT_DIR
from csv_utils import append_to_full_training_csv
from csv_utils import get_dataframe
from csv_utils import save_list_as_csv


def classify(
    command: str,
    training_file: str = "",
    sample_size: int = 0,
    random_state: int = 1,
    train_size: float = 0.75
):
    """
    Loads the training data, train the classifiers and classify
    either the whole available corpus or a sample.
    """
    crime_data, result_data = load_training_data(training_file)

    print("\nTraining crime type classifier.")
    crime_words, crime_classifier = get_words_and_trained_classifier(crime_data, train_size)

    print("\nTraining result type classifier.")
    result_words, result_classifier = get_words_and_trained_classifier(result_data, train_size)

    if command == "corpus":
        output = classify_corpus(
            crime_words,
            crime_classifier,
            result_words,
            result_classifier
        )

    if command == "sample":
        output = classify_sample(
            crime_words,
            crime_classifier,
            result_words,
            result_classifier,
            sample_size,
            random_state
        )

    output_path = save_list_as_csv(OUT_DIR, "output", output)
    verify_output_sample(output_path)


def load_training_data(filename: str) -> Tuple[List[Repository], List[Repository]]:
    """
    Reads the training data .csv file and returns a tuple with 3
    verdicts repositories, one for each kind.
    """
    tp = FULL_TRAIN_DATA_PATH if filename == "" else os.path.join(TRAIN_DIR, filename)
    print(f"Loading training data from {tp}")
    train = pd.read_csv(tp, names=TRAIN_CSV_NAMES, sep=";")
    crime = [load_training_type(train, "crime_type", m.value) for m in CrimeTypeEnum]
    result = [load_training_type(train, "result_type", m.value) for m in ResultTypeEnum]
    return crime, result


def load_training_type(df: pd.DataFrame, type_field: str, type_value: int) -> Repository:
    """
    Loads a specific training data type into a Repository.
    """
    fileids = list(df[df[type_field] == type_value]["full_id"])
    repo = Repository(fileids=fileids, enum_value=type_value)
    return repo


def get_words_and_trained_classifier(
    training_data: List[Repository],
    train_size:float
) -> Tuple[List[str], VoteClassifier]:
    """
    Gets a list with the top FEATS_LEN words
    of each type (crime or result) and a trained
    vote classifier trained on the training_data.
    """
    tokens = []
    for repo in training_data:
        tokens.extend(repo.tokens)
    fdist = nltk.FreqDist(tokens)
    words = list(fdist)[:FEATS_LEN]
    features = get_all_features(training_data, words)
    train, test = get_train_test_sets(features, train_size)
    vote_classifier = train_classifiers(train, test)
    return words, vote_classifier


def get_train_test_sets(
    features: List[Tuple[Dict[str, bool], int]],
    train_size: float,
) -> Tuple[List[Tuple[Dict[str, bool], int]], List[Tuple[Dict[str, bool], int]]]:
    """
    Shuffles the data, split it into two and returns
    two Lists, one for traning and one for testing.
    """
    random.shuffle(features)
    features_size = len(features)
    boundary = floor(train_size * features_size)
    train, test = features[:boundary], features[boundary:]
    return train, test


def train_classifiers(
    train: List[Tuple[Dict[str, bool], int]],
    test: List[Tuple[Dict[str, bool], int]]
) -> VoteClassifier:
    """
    Trains each classifier individually and
    then ensembles the VoteClassifier.
    """
    classifiers = get_classifiers()
    for classifier in classifiers:
        classifier.train(train)
        print(classifier, nltk.classify.accuracy(classifier, test))
    vote_classifier = VoteClassifier(classifiers)
    print("voted: ", nltk.classify.accuracy(vote_classifier, test))
    return vote_classifier


def get_all_features(
    training_data: List[Repository],
    word_features: List[str]
) -> List[Tuple[Dict[str, bool], int]]:
    """
    Gets the features from each Repository and
    add them all into one list.
    """
    features = []
    for repo in training_data:
        features.extend(get_corpus_features_list(repo, word_features))
    return features


def get_corpus_features_list(
    repo: Repository,
    word_features: List[str]
) -> List[Tuple[Dict[str, bool], int]]:
    """
    Gets the features list from a Repository.
    """
    return [(v.features(word_features), repo.enum_value) for v in repo.repository]


def classify_sample(
    crime_words: List[str],
    crime_classifier: VoteClassifier,
    result_words: List[str],
    result_classifier: VoteClassifier,
    size: int,
    state: int
) -> List[str]:
    """
    Classifies a sample of the available corpus.
    """
    df = get_dataframe()
    df = df.sample(n=size, random_state=state)
    output = []
    for i, fileid in enumerate(list(df["full_id"])):
        print(f"Classifying document #{i}", end="\r")
        filepath = os.path.join(TXT_DIR, f"{fileid}.txt")
        crime, result = classify_document(
            filepath,
            crime_words,
            crime_classifier,
            result_words,
            result_classifier
        )
        output.append(f"{fileid};{';'.join(crime)};{';'.join(result)}")
    return output


def classify_corpus(
    crime_words: List[str],
    crime_classifier: VoteClassifier,
    result_words: List[str],
    result_classifier: VoteClassifier
) -> List[str]:
    """
    Classifies all of the available corpus.
    """
    output = []
    corpus = os.listdir(TXT_DIR)
    for i, _file in enumerate(corpus):
        print(f"Classifying document #{i}", end="\r")
        fileid = _file.replace(".txt", "")
        sent_path = os.path.join(TXT_DIR, _file)
        crime, result = classify_document(
            sent_path,
            crime_words,
            crime_classifier,
            result_words,
            result_classifier
        )
        output.append(f"{fileid};{';'.join(crime)};{';'.join(result)}")
    return output


def classify_document(
    filepath: str,
    crime_words: List[str],
    crime_classifier: VoteClassifier,
    result_words: List[str],
    result_classifier: VoteClassifier,
) -> Tuple[Tuple[str, str], Tuple[str, str]]:
    """
    Reads the text content of a document and classifies it.
    """
    with open(filepath) as f:
        content = f.read()
    v = Verdict(content)
    crime = classify_type(v, crime_words, crime_classifier)
    result = classify_type(v, result_words, result_classifier)
    return crime, result


def classify_type(
    verdict: Verdict,
    words: List[str],
    classifier: VoteClassifier
) -> Tuple[str, str]:
    """
    Classifies the verdict and returns the classification and confidence.
    """
    features = verdict.features(words)
    _type, _confidence = classifier.safe_classify(features, CONFIDENCE)
    return str(_type), str(_confidence)


def verify_output_sample(filepath: str):
    """
    Takes a sample from the AI classified input and
    prompts the user to manually verify them, saving
    the results among the training data to retro
    feed the model.
    """
    can_verify = input(f"\nVerificar uma amostra de {DEFAULT_SAMPLE} sentenças? Y/n\n")
    if can_verify == "n":
        return

    df = pd.read_csv(filepath, names=OUT_CSV_NAMES, sep=";")
    df: pd.DataFrame = df.sample(n=DEFAULT_SAMPLE)
    print(df.to_string())
    outpath = human.classify_files(df)
    append_to_full_training_csv(outpath)


if __name__ == "__main__":
    pass
