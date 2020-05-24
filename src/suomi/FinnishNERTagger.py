# coding: utf-8

"""
NER-tagging for Finnish news
https://arxiv.org/abs/1908.04212
"""
import re

from string import punctuation

import pandas as pd
from seqlearn.datasets import load_conll
from seqlearn.evaluation import whole_sequence_accuracy
from seqlearn.perceptron import StructuredPerceptron
from sklearn.metrics.classification import accuracy_score, f1_score, classification_report

real_num_pattern = re.compile('\d+(([\.\,]\d+)+|\.)')
time_num_pattern = re.compile('\d{2}([\:\/]\d{2})+')
eng_pattern = re.compile(r'^[a-z]+$', re.I)
abbr_pattern = re.compile(r'([A-Z]{2,}|([A-Z]\.)+)')
currency_pattern = re.compile('[\$€£¢¥₽\+\-\*\/\^\=]')


FI_DATE_DESCRIPTORS = {
    "kuun", "kuu", "kuuta", "kuussa", "kuulta", "vuoden", "vuonna", "vuoteen", "vuodesta", "vappu"
}
FI_GEO_DESCRIPTORS = {
    "kylä", "katu", "tie", "järvi", "joki", "mäki", "vuori", "salmi",
    "vaara", "lahti", "linna", "koski", "niemi", "ranta", "suu", "maa"
}
FI_ORG_DESCRIPTORS = {"Oy"}
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
    """if i == 0:
        yield "first"

    if i == len(sequence) - 1:
        yield "last\""""
        
    # yield "is_eos=" + str(seq == ".")

    # word's length
    yield "len=" + get_word_len(seq)

    # first 4 letters
    yield "first_letters=" + seq[:4] if len(seq) > 4 else seq

    # last 5 letters
    yield "last_letters=" + seq[-4:] if len(seq) > 4 else seq

    # word shape
    yield "word_shape=" + str(get_word_shape(seq))
    # yield "short_word_shape=" + get_short_word_shape(seq)
    yield "non_en_alphabet_count=" + str(non_alphabet_count(seq))
    yield "digits_count=" + str(digits_count(seq))

    # is date descriptor
    # if any(seq.lower().endswith(date_descr) for date_descr in FI_DATE_DESCRIPTORS):
    if 'kuu' in seq.lower() or 'voun' in seq.lower() or 'vout' in seq.lower() \
            or 'voud' in seq.lower() or 'vous' in seq.lower():
        yield "date_descriptor"

    # if seq.endswith(':n'):
    #     yield "ends_with_n"

    if abbr_pattern.search(seq):
        yield "abbr"

    # if re.search(r'\d{4}', seq):
    #     yield "prob_year"

    # if seq.isdigit():
    #     yield 'is_digit'

    if 'ch' in seq.lower() or 'ck' in seq.lower() or 'ph' in seq.lower() or \
            'ew' in seq.lower() or 'ow' in seq.lower():
        yield "contains_ck_ch_ph_ew"

    if real_num_pattern.search(seq):
        yield "num_with_point"

    if eng_pattern.match(seq):
        yield "contains_latin_chars"

    # is organization descriptor
    if any(seq == org_descr for org_descr in FI_ORG_DESCRIPTORS):
        yield "org_descriptor"

    if i > 0:
        prev = sequence[i - 1].split("\t")[0]
        # previous word's length
        yield "prev_len=" + str(get_word_len(prev))

    if i > 1:
        pprev = sequence[i - 2].split("\t")[0]
        yield "pprev_short_word_shape=" + get_short_word_shape(pprev)

    if i > 0:
        prev = sequence[i - 1].split("\t")[0]
        # last letters of the previous word
        yield "prev_last_letters=" + (prev[-3:] if len(prev) > 3 else prev)

    if i > 0:
        prev = sequence[i - 1].split("\t")[0]
        yield "prev_short_word_shape=" + get_short_word_shape(prev)
        
    # if i > 0:
    #     prev = sequence[i - 1].split("\t")[0]
    #     yield "prev_is_eos=" + str(prev == ".")

    if i < len(sequence) - 1:
        next_ = sequence[i + 1].split("\t")[0]
        # next word's length
        yield "next_len=" + str(get_word_len(next_))

    if i < len(sequence) - 1:
        next_ = sequence[i + 1].split("\t")[0]
        # last letters of the next word
        yield "next_last_letters=" + (next_[-4:] if len(next_) > 4 else next_)

    if i < len(sequence) - 1:
        next_ = sequence[i + 1].split("\t")[0]
        yield "next_short_word_shape=" + get_short_word_shape(next_)
        
    # if i < len(sequence) - 1:
    #     next_ = sequence[i + 1].split("\t")[0]
    #     yield "next_is_eos=" + str(next_ == ".")

    if i < len(sequence) - 2:
        nnext = sequence[i + 2].split("\t")[0]
        yield "nnext_short_word_shape=" + get_short_word_shape(nnext)


# читаем обучающее множество
X_train, y_train, lengths_train = load_conll(open("finer-data/data/digitoday.2014.train.csv", "r"), features)

clf = StructuredPerceptron(decode="bestfirst", lr_exponent=.1, max_iter=10, verbose=1, random_state=0)

print("Fitting model " + str(clf))
clf.fit(X_train, y_train, lengths_train)

print("\nPredictions on dev set")

# читаем отладочное множество
X_dev, y_dev, lengths_dev = load_conll(open("finer-data/data/digitoday.2014.dev.csv", "r"), features)
y_pred = clf.predict(X_dev, lengths_dev)

print("Whole seq accuracy    ", whole_sequence_accuracy(y_dev, y_pred, lengths_dev))
print("Element-wise accuracy ", accuracy_score(y_dev, y_pred))
print("Mean F1-score macro   ", f1_score(y_dev, y_pred, average="macro"))
print(classification_report(y_dev, y_pred))

print(pd.Series(y_pred).value_counts())

print("\nPredictions on test set")

# читаем тестовое множество
X_test, y_test, lengths_test = load_conll(open("finer-data/data/digitoday-fixed.2015.test.csv", "r"), features)
y_pred = clf.predict(X_test, lengths_test)
print("Whole seq accuracy    ", whole_sequence_accuracy(y_test, y_pred, lengths_test))
print("Element-wise accuracy ", accuracy_score(y_test, y_pred))
print("Mean F1-score macro   ", f1_score(y_test, y_pred, average="macro"))
print(classification_report(y_test, y_pred))

print(pd.Series(y_pred).value_counts())


"""
Quality with random state=0
Dev:
Whole seq accuracy     0.9746450304259635
Element-wise accuracy  0.998083161309
/Library/Frameworks/Python.framework/Versions/3.6/lib/python3.6/site-packages/sklearn/metrics/classification.py:1135: UndefinedMetricWarning: F-score is ill-defined and being set to 0.0 in labels with no predicted samples.
  'precision', 'predicted', average, warn_for)
Mean F1-score macro    0.726506267891
/Library/Frameworks/Python.framework/Versions/3.6/lib/python3.6/site-packages/sklearn/metrics/classification.py:1135: UndefinedMetricWarning: Precision and F-score are ill-defined and being set to 0.0 in labels with no predicted samples.
  'precision', 'predicted', average, warn_for)
             precision    recall  f1-score   support

      B-LOC       0.93      0.55      0.69        47
      B-ORG       1.00      1.00      1.00         3
      B-PER       1.00      0.50      0.67         4
      I-LOC       1.00      1.00      1.00        12
      I-PER       0.00      0.00      0.00         1
          O       1.00      1.00      1.00     13497

avg / total       1.00      1.00      1.00     13564

O        13519
B-LOC       28
I-LOC       12
B-ORG        3
B-PER        2
dtype: int64

Test:
Whole seq accuracy     0.9695740365111561
Element-wise accuracy  0.996721452914
Mean F1-score macro    0.437923842113
             precision    recall  f1-score   support

     B-DATE       0.00      0.00      0.00         2
      B-LOC       0.95      0.39      0.55        90
      B-ORG       0.92      0.64      0.75       154
      B-PER       0.75      0.22      0.34        27
     I-DATE       0.00      0.00      0.00         1
      I-LOC       0.86      0.86      0.86        14
      I-PER       0.00      0.00      0.00         2
          O       1.00      1.00      1.00     46072

avg / total       1.00      1.00      1.00     46362

O        46197
B-ORG      106
B-LOC       37
I-LOC       14
B-PER        8
dtype: int64
"""
