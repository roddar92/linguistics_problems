# coding: utf-8

"""
NER-tagging for Finnish news
https://arxiv.org/abs/1908.04212
"""
import re

from string import punctuation

from seqlearn.datasets import load_conll
from seqlearn.evaluation import whole_sequence_accuracy
from seqlearn.perceptron import StructuredPerceptron
from sklearn.metrics.classification import accuracy_score, f1_score

real_num_pattern = re.compile('\d+([\.\,]\d)+')
time_num_pattern = re.compile('\d+([\:\/]\d)+')
eng_pattern = re.compile('^[a-z]+$', re.I)
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
    return sum(1 for j in seq if j not in punctuation and not re.match('^[a-z\d]$', j, re.I))


def get_word_shape(seq):
    return ''.join([
        'X' if re.search('[A-ZÄÖ]', s) else
        'x' if re.search('[a-zäö]', s) else
        'd' if re.search('\d', s) else s
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
        
    yield "is_eos=" + str(seq == ".")

    # word's length
    yield "len=" + get_word_len(seq)

    # first 4 letters
    yield "first_letters=" + seq[:4] if len(seq) > 4 else seq

    # last 5 letters
    yield "last_letters=" + seq[-5:] if len(seq) > 5 else seq

    # word shape
    yield "word_shape=" + str(get_word_shape(seq))
    yield "short_word_shape=" + get_short_word_shape(seq)
    yield "non_en_alphabet_count=" + str(non_alphabet_count(seq))
    # yield "digits_count=" + str(digits_count(seq))

    # is date descriptor
    if any(seq.lower().endswith(date_descr) for date_descr in FI_DATE_DESCRIPTORS):
        yield "date_descriptor"

    if seq[-2:] in (':n', 'en', 'in', 'an', 'un', 'on'):
        yield "ends_with_n"

    if seq[-2:] == 'us':
        yield "ends_with_us"

    if 'ch' in seq.lower() or 'ck' in seq.lower() or any(l in seq.lower() for l in 'bcgwz'):
        yield "contains_c_ck_ch_z"

    # if seq[-1] in 'aeiou':
    #     yield "ends_with_vowel"

    if real_num_pattern.search(seq):
        yield "num_with_point"

    if eng_pattern.match(seq):
        yield "contains_latin_chars"

    # is organization descriptor
    # if any(seq == org_descr for org_descr in FI_ORG_DESCRIPTORS):
    #     yield "org_descriptor"

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
        yield "prev_last_letters=" + (prev[-5:] if len(prev) > 5 else prev)

    if i > 0:
        prev = sequence[i - 1].split("\t")[0]
        yield "prev_short_word_shape=" + get_short_word_shape(prev)
        
    if i > 0:
        prev = sequence[i - 1].split("\t")[0]
        yield "prev_is_eos=" + str(prev == ".")

    if i < len(sequence) - 1:
        next_ = sequence[i + 1].split("\t")[0]
        # next word's length
        yield "next_len=" + str(get_word_len(next_))

    if i < len(sequence) - 1:
        next_ = sequence[i + 1].split("\t")[0]
        # last letters of the next word
        yield "next_last_letters=" + (next_[-5:] if len(next_) > 5 else next_)

    if i < len(sequence) - 1:
        next_ = sequence[i + 1].split("\t")[0]
        yield "next_short_word_shape=" + get_short_word_shape(next_)
        
    if i < len(sequence) - 1:
        next_ = sequence[i + 1].split("\t")[0]
        yield "next_is_eos=" + str(next_ == ".")

    if i < len(sequence) - 2:
        nnext = sequence[i + 2].split("\t")[0]
        yield "nnext_short_word_shape=" + get_short_word_shape(nnext)


# читаем обучающее множество
X_train, y_train, lengths_train = load_conll(open("finer-data/data/digitoday.2014.train.csv", "r"), features)

clf = StructuredPerceptron(decode="bestfirst", lr_exponent=.05, max_iter=10, verbose=1)

print("Fitting model " + str(clf))
clf.fit(X_train, y_train, lengths_train)

print("\nPredictions on dev set")

# читаем отладочное множество
X_dev, y_dev, lengths_dev = load_conll(open("finer-data/data/digitoday.2014.dev.csv", "r"), features)
y_pred = clf.predict(X_dev, lengths_dev)

print("Whole seq accuracy    ", whole_sequence_accuracy(y_dev, y_pred, lengths_dev))
print("Element-wise accuracy ", accuracy_score(y_dev, y_pred))
print("Mean F1-score macro   ", f1_score(y_dev, y_pred, average="macro"))

"""
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
"""
