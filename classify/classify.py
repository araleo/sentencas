from typing import Dict
from typing import List
from typing import Tuple
import os
import random

import nltk
import pandas as pd

from classifiers import CLASSIFIERS
from classify import human
from constants import HUMAN_DIR, OUT_CSV_NAMES
from constants import OUT_DIR
from constants import TRAIN_CSV_NAMES
from constants import TRAIN_DATA_PATH
from constants import TXT_DIR
from csv_utils import get_dataframe
from csv_utils import save_list_as_csv
from Repository import Repository
from Verdict import Verdict
from VoteClassifier import VoteClassifier


CONFIDENCE = 0.5


def classify(command: str, sample_size: int = 0, random_state: int = 1):
    """
    Loads the training data, train the classifiers and classify
    either the whole available corpus or a sample.
    """
    condenatorias, absolutorias, neutras = load_training_data()

    all_words = nltk.FreqDist(condenatorias.tokens + absolutorias.tokens + neutras.tokens)
    word_features = list(all_words)[:3000]
    all_features = get_all_features(condenatorias, absolutorias, neutras, word_features)

    train, test = get_train_test_sets(all_features)
    vote_classifier = train_classifiers(train, test)

    if command == "corpus":
        output = classify_corpus(word_features, vote_classifier)
    if command == "sample":
        output = classify_sample(word_features, vote_classifier, sample_size, random_state)

    output_path = save_list_as_csv(OUT_DIR, "output", output)
    verify_output_sample(output_path)


def load_training_data() -> Tuple[Repository, Repository, Repository]:
    """
    Reads the training data .csv file and returns a tuple with 3
    verdicts repositories, one for each kind.
    """
    train = pd.read_csv(TRAIN_DATA_PATH, names=OUT_CSV_NAMES, sep=";")
    condenatorias = load_training_type(train, 1)
    absolutorias = load_training_type(train, 2)
    neutras = load_training_type(train, 3)
    return condenatorias, absolutorias, neutras


def load_training_type(df: pd.DataFrame, typeid: int) -> Repository:
    """
    Loads a specific training data type into a Repository.
    """
    fileids = list(df[df["type"] == typeid]["fileid"])
    sentencas = Repository(fileids=fileids)
    return sentencas


def get_train_test_sets(feature_set: List) -> Tuple[List, List]:
    """
    Shuffles the data, split it into two and returns
    two Lists, one for traning and one for testing.
    """
    print(feature_set)
    random.shuffle(feature_set)
    size = len(feature_set)
    train_set, test_set = feature_set[size//2:], feature_set[:size//2]
    return train_set, test_set


def train_classifiers(train: List, test: List) -> VoteClassifier:
    """
    Trains each classifier individually and
    then ensembles the VoteClassifier.
    """
    for classifier in CLASSIFIERS:
        classifier.train(train)
        print(classifier, nltk.classify.accuracy(classifier, test))
    vote_classifier = VoteClassifier(CLASSIFIERS)
    print("voted: ", nltk.classify.accuracy(vote_classifier, test))
    return vote_classifier


def get_all_features(
    condenatorias: Repository,
    absolutorias: Repository,
    neutras: Repository,
    word_features: List[str]
) -> List[Tuple[Dict[str, bool], int]]:
    """
    Gets the features from each Repository and
    add them all into one list.
    """
    con_features = get_corpus_features_list(condenatorias, 1, word_features)
    abs_features = get_corpus_features_list(absolutorias, 2, word_features)
    neu_features = get_corpus_features_list(neutras, 3, word_features)
    return con_features + abs_features + neu_features


def get_corpus_features_list(
    corpus: Repository,
    _type: int,
    word_features: List[str]
) -> List[Tuple[Dict[str, bool], int]]:
    """
    Gets the features list from a Repository.
    """
    return [(s.features(word_features), _type) for s in corpus.repository]


def classify_corpus(
    word_features: List[str],
    vote_classifier: VoteClassifier
) -> List[str]:
    """
    Classifies all of the available corpus.
    """
    output = []
    corpus = os.listdir(TXT_DIR)
    for i, sent in enumerate(corpus):
        print(f"Classifying document #{i}", end="\r")
        sent_id = sent.replace(".txt", "")
        sent_path = os.path.join(TXT_DIR, sent)
        _type, confidence = classify_document(sent_path, word_features, vote_classifier)
        output.append(";".join(sent_id, _type, confidence))
    return output


def classify_sample(
    word_features: List[str],
    vote_classifier: VoteClassifier,
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
        _type, confidence = classify_document(filepath, word_features, vote_classifier)
        output.append(";".join(fileid, _type, confidence))
    return output


def classify_document(
    filepath: str,
    word_features: List[str],
    vote_classifier: VoteClassifier
) -> Tuple[str, str]:
    """
    Reads the text content of a document
    and classifies it.
    """
    with open(filepath) as f:
        content = f.read()
    v = Verdict(content)
    v_features = v.features(word_features)
    _type, _confidence = vote_classifier.safe_classify(v_features, CONFIDENCE)
    return str(_type), str(_confidence)


def verify_output_sample(filepath: str):
    """
    Takes a sample from the AI classified input and
    prompts the user to manually verify them, saving
    the results among the training data to retro
    feed the model.
    """
    verified = []
    df = pd.read_csv(filepath, names=OUT_CSV_NAMES, sep=";")
    df: pd.DataFrame = df.sample(n=10)
    for row in df.itertuples():
        verified_type = human.classify_single_file(row.full_id)
        print(f"\nSentença originalmente classificada como: {row.type} com confiança de {row.confidence}.")
        verified.append(f"{row.full_id};{verified_type}")
    save_list_as_csv(HUMAN_DIR, "human", verified)


if __name__ == "__main__":
    pass
