# coding: utf-8

"""
Pos-tagging for Russian Translit
https://www.kaggle.com/c/pos-punk
"""

import pandas as pd

import re
import string

from seqlearn.datasets import load_conll
from seqlearn.evaluation import whole_sequence_accuracy
from seqlearn.perceptron import StructuredPerceptron
from sklearn.metrics.classification import accuracy_score, f1_score

real_num_pattern = re.compile('\d+([\.\,\:\/]\d)+')
currency_pattern = re.compile('[\$€£¢¥₽\+\-\*\/\^\=]')


FI_GEO_DESCRIPTORS = [
    "kylä", "katu", "tie", "järvi", "joki", "mäki", "vuori", "salmi",
    "vaara", "lahti", "linna", "koski", "niemi", "ranta", "suu"
]
FI_VOWELS = "aeäöiouy"


def is_vowel(symbol):
    return symbol in FI_VOWELS


def get_word_len(seq):
    return str(len(seq) if len(seq) < 5 else "long")


def digits_count(seq):
    return len([j.isdigit() for j in seq])


def get_word_shape(seq):
    return ''.join([
        'X' if re.search('[A-ZÄÖ]', s) else
        'x' if re.search('[a-zäö]', s) else
        'd' if re.search('\d', s) else
        'p' if s in string.punctuation else s
        for s in seq
    ])


def get_short_word_shape(seq):
    return re.sub("(\w)(\1)+", "\1", get_word_shape(seq))


def features(sequence, i):
    """
        Generate features from inputs
        :param sequence: columns set
        :param i: word number
        :return: features set
    """
    seq = sequence[i].split("\t")[1]

    # first position in the sentence
    if i == 0:
        yield "first"

    if i == len(sequence) - 1:
        yield "last"
        
    yield "is_eos=" + str(seq == ".")

    # word's length
    yield "len=" + get_word_len(seq)

    # first 4 letters
    yield "first_four_letters=" + seq[:4] if len(seq) > 4 else seq

    # last 3 letters
    yield "last_three_letters=" + seq[-3:] if len(seq) > 3 else seq

    # word shape
    yield "word_shape=" + str(get_word_shape(seq))
    yield "short_word_shape=" + get_short_word_shape(seq)
    yield "digits_count=" + str(digits_count(seq))

    # currency
    if currency_pattern.search(seq):
        yield "currency"

    # ends with -'n' and a vowel behind 'n'
    if any(seq.endswith(f"{l}n") for l in FI_VOWELS) and not seq.endswith("nen"):
        yield "ends_with_vowel_n"
        
    # ends with -'nen'
    if seq.endswith("nen"):
        yield "ends_with_vowel_nen"

    # ends with -'ssa'
    if seq.endswith("ssa") or seq.endswith("ssä"):
        yield "ends_with_ssa"
        
    # ends with -'sta'
    if seq.endswith("sta") or seq.endswith("stä"):
        yield "ends_with_sta"

    # ends with -'lta'
    if seq.endswith("lta") or seq.endswith("ltä"):
        yield "ends_with_lta"

    # ends with -'lla'
    if seq.endswith("lla") or seq.endswith("llä"):
        yield "ends_with_lla"
        
    # ends with -'katu' or -'tie' or -'järvi' or -'joki' or -'saari' or -'mäki' or -'vuori'
    if any(seq.endswith(geo_descr) for geo_descr in FI_GEO_DESCRIPTORS):
        yield "ends_with_geo"

    if i > 0:
        prev = sequence[i - 1].split("\t")[1]
        # previous word's length
        yield "prev_len=" + str(get_word_len(prev))

    if i > 0:
        prev = sequence[i - 1].split("\t")[1]
        # last letters of the previous word
        yield "prev_last_letters=" + (prev[-3:] if len(prev) > 3 else prev)

    if i > 0:
        prev = sequence[i - 1].split("\t")[1]
        yield "prev_short_word_shape=" + get_short_word_shape(prev)
        
    if i > 0:
        prev = sequence[i - 1].split("\t")[1]
        yield "prev_is_eos=" + str(prev == ".")

    if i < len(sequence) - 1:
        next = sequence[i + 1].split("\t")[1]
        # next word's length
        yield "next_len=" + str(get_word_len(next))

    if i < len(sequence) - 1:
        next = sequence[i + 1].split("\t")[1]
        # last letters of the next word
        yield "next_last_letters=" + (next[-3:] if len(next) > 3 else next)

    if i < len(sequence) - 1:
        next = sequence[i + 1].split("\t")[1]
        yield "next_short_word_shape=" + get_short_word_shape(next)
        
    if i < len(sequence) - 1:
        next = sequence[i + 1].split("\t")[1]
        yield "next_is_eos=" + str(next == ".")

# читаем обучающее множество
X_train, y_train, lengths_train = load_conll(open("../resources/train.data", "r"), features)

clf = StructuredPerceptron(decode="viterbi", lr_exponent=.05, max_iter=30)

print("Fitting model " + str(clf))
clf.fit(X_train, y_train, lengths_train)

print("\nPredictions on dev set")

# читаем отладочное множество
X_dev, y_dev, lengths_dev = load_conll(open("../resources/dev.data", "r"), features)
y_pred = clf.predict(X_dev, lengths_dev)

print("Whole seq accuracy    ", whole_sequence_accuracy(y_dev, y_pred, lengths_dev))
print("Element-wise accuracy ", accuracy_score(y_dev, y_pred))
print("Mean F1-score macro   ", f1_score(y_dev, y_pred, average="macro"))

print("\nPredictions on test set")

# читаем тестовое множество
X_test, _, lengths_test = load_conll(open("../resources/test.data", "r"), features)
y_pred = clf.predict(X_test, lengths_test)

print(pd.Series(y_pred).value_counts())

print("Saving predicted as a submission")

with open("submission.csv", "w") as wf:
    wf.write("id,tag\n")
    for id, tag in enumerate(list(y_pred)):
        wf.write(str(id + 1) + "," + tag + "\n")
