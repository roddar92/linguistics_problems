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


def is_vowel(symbol):
    return symbol in 'aeёiouy'


def get_word_len(seq):
    return str(len(seq) if len(seq) < 5 else "long")


def digits_count(seq):
    return len([j.isdigit() for j in seq])


def get_word_shape(seq):
    return ''.join([
        'X' if re.search('[A-ZЁ]', s) else 'x' if re.search('[a-zё]', s) else 'd' if re.search('\d', s) else s
        for s in seq
    ])


def get_short_word_shape(seq):
    return re.sub("(\w)(\1)+", "\1", get_word_shape(seq))


def is_punctuation(seq):
    return all([j in string.punctuation for j in seq])


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

    # word's length
    yield "len=" + get_word_len(seq)

    # first 4 letters
    yield "first_four_letters=" + seq[:4] if len(seq) > 4 else seq

    # last 3 letters
    yield "last_three_letters=" + seq[-3:] if len(seq) > 3 else seq

    # word shape
    yield "word_shape=" + str(get_word_shape(seq))
    yield "short_word_shape=" + get_short_word_shape(seq)

    if seq.istitle():
        yield "title"

    if seq.isupper():
        yield "upper"

    if is_punctuation(seq):
        yield "is_punct"

    if '-' in seq:
        yield "has_dash"

    yield "digits_count=" + str(digits_count(seq))

    # only alpha or digit
    if seq.isalpha():
        yield "alpha"

    # only digits
    if real_num_pattern.search(seq) or seq.isdigit():
        yield "num"

    # currency
    if currency_pattern.search(seq):
        yield "currency"

    # contains -'its'
    if 'its' in seq or re.search(r'\w+(tel|nik)', seq):
        yield "with_tel_its"

    # contains letter + 'к' suffix
    if re.search(r'\w+[bjlmnpstvz]k', seq):
        yield "with_k_suffix"

    # contains letter + 'в' suffix
    if re.search(r'\w+(st|z|o)v', seq):
        yield "with_v_suffix"

    if re.search(r'\w+[eio]k', seq):
        yield "with_eiok_suffix"

    if re.search(r'\w+stn', seq):
        yield "with_stn_suffix"

    if re.search(r'\w+[dk]r', seq):
        yield "with_dr_suffix"

    if re.search(r'\w+(sh|jj)k', seq):
        yield "with_shk_suffix"

    if re.search(r'\w+[ln]`k', seq):
        yield "with_lnk_suffix"

    # contains 'нн'
    if 'nn' in seq:
        yield "with_nn"

    # contains 'чн', 'чк'
    if 'chk' in seq or 'chn' in seq or 'schn' in seq:
        yield "with_chk"

    # contains letter + 'н' suffix
    if re.search(r'\w+[jlmrstvz]n', seq):
        yield "with_n_suffix"

    # contains suffixes 'ющ', 'ящ', 'ищ', 'вш'
    if re.search(r'\w+((y[au]|i)s?ch|vsh)', seq) or seq.endswith('v'):
        yield "with_part_sch_suffixes"

    # ends with 'ся'
    if seq.endswith("sya") or seq.endswith('s\''):
        yield "ends_with_sya"

    if i > 0:
        prev = sequence[i - 1].split("\t")[1]
        # previous word's length
        yield "prev_len=" + str(get_word_len(prev))

    if i > 0:
        prev = sequence[i - 1].split("\t")[1]
        # previous word is title
        yield "prev_title=" + str(prev.istitle())

    if i > 0:
        prev = sequence[i - 1].split("\t")[1]
        # last letters of the previous word
        yield "prev_last_letters=" + (prev[-3:] if len(prev) > 3 else prev)

    if i > 0:
        prev = sequence[i - 1].split("\t")[1]
        # previous word is alnum
        yield "prev_is_alnum=" + str(prev.isalnum())

    if i < len(sequence) - 1:
        next = sequence[i + 1].split("\t")[1]
        # next word's length
        yield "next_len=" + str(get_word_len(next))

    if i < len(sequence) - 1:
        next = sequence[i + 1].split("\t")[1]
        # next word is title
        yield "next_title=" + str(next.istitle())

    if i < len(sequence) - 1:
        next = sequence[i + 1].split("\t")[1]
        # last letters of the next word
        yield "next_last_letters=" + (next[-3:] if len(next) > 3 else next)

    if i < len(sequence) - 1:
        next = sequence[i + 1].split("\t")[1]
        # next word is alnum
        yield "next_is_alnum=" + str(next.isalnum())

# читаем обучающее множество
X_train, y_train, lengths_train = load_conll(open("../resources/train.data", "r"), features)

clf = StructuredPerceptron(decode="viterbi", lr_exponent=.05, max_iter=50)

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
