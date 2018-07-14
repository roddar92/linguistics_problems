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


def has_affixes(seq):
    return seq[0] in 'kodpsvn' or seq[:2] in ['za', 'iz'] or seq[:3] in ['bez', 'bes']


def features(sequence, i):
    """
        Функция, которая отображает входы сразу в фичи

        :param sequence: набор колонок
        :param i: номер слова
        :return: множество фич
    """
    seq = sequence[i].split("\t")[1]

    # позиция номер один в предложении
    if i == 0:
        yield "first"

    if i == len(sequence) - 1:
        yield "last"

    # длина слова, если оно короче 5 символов
    yield "len=" + get_word_len(seq)

    # первые три буквы слова
    yield "first_four_letters=" + seq[:4] if len(seq) > 4 else seq

    # последние три буквы слова
    yield "last_three_letters=" + seq[-3:] if len(seq) > 3 else seq

    # word shape
    yield "word_shape=" + str(get_word_shape(seq))
    yield "short_word_shape=" + get_short_word_shape(seq)

    # начинается с прописной
    if seq.istitle():
        yield "title"

    # все буквы прописные
    if seq.isupper():
        yield "upper"

    if is_punctuation(seq):
        yield "is_punct"

    if '-' in seq:
        yield "has_dash"

    # количество цифр
    yield "digits_count=" + str(digits_count(seq))

    # имеет приставки
    if has_affixes(seq):
        yield "starts_with_affixes"

    # состоит только из букв и чисел
    if seq.isalnum():
        yield "alnum"

    # состоит только из цифр
    if real_num_pattern.search(seq) or seq.isdigit():
        yield "num"

    # число с валютой
    if currency_pattern.search(seq):
        yield "currency"

    # последняя буква - гласная
    if is_vowel(seq[-1]):
        yield "last_vowel=" + "ya" if seq.endswith('ya') else "yu" if seq.endswith('yu') else seq[-1]

    # содержит -'иц'
    if 'its' in seq or re.search(r'\w+nik', seq):
        yield "with_its"

    # содержит некоторые суффиксы
    if re.search(r'\w+sk', seq):
        yield "with_sk_suffix"

    if re.search(r'\w+st?v', seq):
        yield "with_stv_suffix"

    if re.search(r'\w+ov', seq):
        yield "with_ov_suffix"

    if re.search(r'\w+[ei]k', seq):
        yield "with_eik_suffix"

    # содержит 'нн'
    if re.search(r'\w+[ei]nn', seq) or 'nn' in seq:
        yield "with_nn"

    # содержит 'чн', 'чк'
    if 'chk' in seq or 'chn' in seq:
        yield "with_chk"

    # содержит 'нк'
    if 'nk' in seq:
        yield "with_nk"

    # содержит 'что', 'это'
    if 'chtob' in seq or re.search(r'^aet[aiou]', seq, re.IGNORECASE):
        yield "with_sconj_subwords"

    if re.search(r'^(aet[aiou][jmt]?|svo[eij][jmy]?|[kt]ak[aio][jmy]?|kajjd|nekotor)', seq, re.IGNORECASE) or \
            re.search(r'^e(go|ё)$', seq, re.IGNORECASE) or seq in ['a', 'an', 'the', 'to', 'tom']:
        yield "with_det_subwords"

    # содержит 'был', 'явл', 'будет' ...
    if 'byl' in seq or seq.startswith('yavl') or re.search(r'^bud[eu]', seq, re.IGNORECASE):
        yield "with_aux_subwords"

    # частицы 'не-ни', 'бы', 'ли' ...
    if re.search(r'^(by|li|n[ei]|jje)$', seq, re.IGNORECASE):
        yield "is_part"

    # содержит суффиксы 'ющ', 'ящ', 'ищ', 'вш'
    if re.search(r'\w+(y[aiu]sch|vsh)', seq) or seq.endswith('v'):
        yield "with_part_sch_suffixes"

    # слово оканчивается на 'ся'
    if seq.endswith("sya") or seq.endswith('s\''):
        yield "ends_with_sya"

    if seq.endswith('j'):
        yield "ends_with_j"

    # последняя буква - согласная
    if seq.endswith('\'') and not is_vowel(seq[-2]):
        yield "ends_with_apo"

    if 'w' in seq.lower():
        yield "with_w_letter"

    if i > 0:
        prev = sequence[i - 1].split("\t")[1]
        # предыдущая с прописной
        yield "prev_title=" + str(prev.istitle())

    if i > 0:
        prev = sequence[i - 1].split("\t")[1]
        # последние буквы предыдущей
        yield "prev_last_letters=" + (prev[-3:] if len(prev) > 3 else prev)

    if i > 0:
        prev = sequence[i - 1].split("\t")[1]
        # предыдущая состоит из букв и цифр
        yield "prev_is_alnum=" + str(prev.isalnum())

    if i < len(sequence) - 1:
        next = sequence[i + 1].split("\t")[1]
        # следующая с прописной
        yield "next_title=" + str(next.istitle())

    if i < len(sequence) - 1:
        next = sequence[i + 1].split("\t")[1]
        # последние буквы следующей
        yield "next_last_letters=" + (next[-3:] if len(next) > 3 else next)

    if i < len(sequence) - 1:
        next = sequence[i + 1].split("\t")[1]
        # следующая состоит из букв и цифр
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
