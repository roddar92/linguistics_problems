# coding: utf-8

"""
POS-tagging for Swedish Stanford Treebank
"""
import re

from string import punctuation

import pandas as pd
from seqlearn.datasets import load_conll
from seqlearn.evaluation import whole_sequence_accuracy
from seqlearn.perceptron import StructuredPerceptron
from sklearn.metrics.classification import accuracy_score, f1_score, classification_report

# real_num_pattern = re.compile('\d+(([\.\,]\d+)+|\.)')
# time_num_pattern = re.compile('\d{2}([\:\/]\d{2})+')
eng_pattern = re.compile(r'^[a-z]+$', re.I)
abbr_pattern = re.compile(r'([A-Z]{2,}|([A-Z]\.)+)')
# currency_pattern = re.compile('[\$€£¢¥₽\+\-\*\/\^\=]')


FI_VOWELS = "aeäöiouy"


def is_vowel(symbol):
    return symbol in FI_VOWELS


def get_word_len(seq):
    return str(len(seq))


def digits_count(seq):
    return len([j.isdigit() for j in seq])


def non_alphabet_count(seq):
    return sum(1 for j in seq if j not in punctuation and not eng_pattern.match(j))


def get_word_shape(seq):
    return ''.join([
        'C' if s in 'BCGFWXZ' else
        'c' if s in 'bcgfwxz' else
        'X' if re.match(r'^[AD-VYÄÖ]$', s) else
        'x' if re.match(r'^[ad-vyäö]$', s) else
        'd' if s.isdigit() else s
        for s in seq
    ])


def get_short_word_shape(seq):
    return re.sub("(\\w)(\\1)+", "\\1", get_word_shape(seq))


def features(sequence, i):
    """
        Generate features from inputs
        :param sequence: columns set
        :param i: word number
        :return: features set
    """
    seq = sequence[i].split("\t")[0]

    # first position in the sentence
    if i == 0:
        yield "first"

    if i == len(sequence) - 1:
        yield "last"

    # word's length
    yield "len=" + get_word_len(seq)

    # first 4 letters
    yield "first_letters=" + seq[:4] if len(seq) > 4 else seq

    # last 4 letters
    yield "last_letters=" + seq[-4:] if len(seq) > 4 else seq

    # word shape
    yield "word_shape=" + str(get_word_shape(seq))
    yield "short_word_shape=" + get_short_word_shape(seq)
    # yield "non_en_alphabet_count=" + str(non_alphabet_count(seq))
    yield "digits_count=" + str(digits_count(seq))

    # if abbr_pattern.search(seq):
    #     yield "abbr"

    # if seq.istitle():
    #     yield 'is_title'

    if seq.endswith('en') or seq.endswith('et'):
       yield "has_det_noun_ending"

    if i > 0:
        prev = sequence[i - 1].split("\t")[0]
        # previous word's length
        yield "prev_len=" + str(get_word_len(prev))

        # last letters of the previous word
        yield "prev_last_letters=" + (prev[-4:] if len(prev) > 4 else prev)
        yield "prev_word_shape=" + get_word_shape(prev)
        yield "prev_short_word_shape=" + get_short_word_shape(prev)

    if i < len(sequence) - 1:
        next_ = sequence[i + 1].split("\t")[0]
        # next word's length
        yield "next_len=" + str(get_word_len(next_))

        # last letters of the next word
        yield "next_last_letters=" + (next_[-4:] if len(next_) > 4 else next_)
        yield "next_word_shape=" + get_word_shape(next_)
        yield "next_short_word_shape=" + get_short_word_shape(next_)


# читаем обучающее множество
X_train, y_train, lengths_train = load_conll(
    open("resources/talbanken-stanford-1.2/talbanken-stanford-train.tsv", "r"), features)

clf = StructuredPerceptron(decode="viterbi", verbose=1, random_state=0)

print("Fitting model " + str(clf))
clf.fit(X_train, y_train, lengths_train)

print("\nPredictions on test set")

# читаем тестовое множество
X_test, y_test, lengths_test = load_conll(
    open("resources/talbanken-stanford-1.2/talbanken-stanford-test.tsv", "r"), features)
y_pred = clf.predict(X_test, lengths_test)
print("Whole seq accuracy    ", whole_sequence_accuracy(y_test, y_pred, lengths_test))
print("Element-wise accuracy ", accuracy_score(y_test, y_pred))
print("Mean F1-score macro   ", f1_score(y_test, y_pred, average="macro"))
print(classification_report(y_test, y_pred))

print(pd.Series(y_pred).value_counts())
