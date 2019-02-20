"""
N-gram language model for detection human sentence opposite artificial-generted sentence
https://www.kaggle.com/c/csc-iinlp-2017-how-many-ngrams
"""

from collections import defaultdict

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer


class LanguageModel(object):
    def __init__(self, ngram_size=2):
        """
            Initialization of N-gram model
            :param ngram_size: size of n-gram, optional
        """

        if ngram_size < 2:
            raise Exception

        self.ngram_size = ngram_size

        self.bigram_vectorizer = CountVectorizer(token_pattern='(\\S+)', ngram_range=(ngram_size, ngram_size))
        self.ugram_vectorizer = CountVectorizer(token_pattern='(\\S+)', ngram_range=(ngram_size - 1, ngram_size - 1))

        self.unigram_counts = defaultdict(lambda: 0)
        self.bigram_counts = defaultdict(lambda: 0)

        self.p_continuation = defaultdict(lambda: 0)
        self.words_set_size = None

        self.d = 0.25
        self.coeff = None

    def fit(self, sentences):
        """
            Training of the model on text sentences
            :param sentences: sentences list
        """

        print("Fitting sentences")

        counts_matrix = self.bigram_vectorizer.fit_transform(sentences)
        counts_context_matrix = self.ugram_vectorizer.fit_transform(sentences)

        self.coeff = (self.d / len(self.bigram_vectorizer.vocabulary_))

        self.words_set_size = len(
            set([key for ngram in self.bigram_vectorizer.vocabulary_.keys() for key in ngram.split(" ")]))

        print("Summing...")

        sum_ngram = np.sum(counts_matrix, axis=0).A1
        sum_context = np.sum(counts_context_matrix, axis=0).A1

        print("shapes: ", sum_ngram.shape, sum_context.shape)
        print("Iterating through ngrams...")

        for one_gram, index in self.ugram_vectorizer.vocabulary_.items():
            self.unigram_counts[one_gram] = sum_context[index]

        for two_gram, index in self.bigram_vectorizer.vocabulary_.items():
            self.bigram_counts[two_gram] = sum_ngram[index]

        for bigram in self.bigram_vectorizer.vocabulary_:
            first, second = bigram.split()
            self.p_continuation[second] += 1

        for w in self.p_continuation:
            self.p_continuation[w] = self.p_continuation[w] / len(self.bigram_vectorizer.vocabulary_)

        return self

    def __calculate_prob(self, ngram):
        """
            Evaluate probability logarithm of a n-gram
            :param ngram: string with n words
            :return: probability logarithm
        """
        first, last = ngram.split()

        last_prob = (self.unigram_counts[last] / self.words_set_size)
        first_word_prob_in_end_of_bigram = self.p_continuation[first] * last_prob
        last_word_prob = self.p_continuation[last] * last_prob

        if self.unigram_counts[first] > 0:
            prob = (max(self.bigram_counts[ngram] - self.d, 0) / self.unigram_counts[first]) + self.d * last_word_prob
        else:
            prob = last_word_prob + first_word_prob_in_end_of_bigram

        return np.log2(self.coeff + prob)

    def __log_prob_sentence(self, sentence):
        """
            Evaluate probability logarithm of a sentence
        :param sentence:
        :return: sentene probability
        """
        splitted = sentence.split(" ")
        sum_log = 1.0

        for i in range(len(splitted) - self.ngram_size + 1):
            ngram = " ".join(splitted[i: i + self.ngram_size])
            sum_log += self.__calculate_prob(ngram)

        return sum_log

    def log_prob(self, sentence_list):
        """
            Probability logarithm for each sentence list
        """
        return list(map(lambda x: self.__log_prob_sentence(x), sentence_list))


df_train = pd.read_csv("train.tsv", sep='\t')
df_test = pd.read_csv("task.tsv", sep='\t')

print("Read ", df_train.shape, df_test.shape)

basic_lm = LanguageModel()
sentences_train = df_train["text"].tolist()
sentences_train = [' '.join(['^', sentence, '$']) for sentence in sentences_train]
basic_lm.fit(sentences=sentences_train)

print("Trained")

test1, test2 = df_test["text1"], df_test["text2"]

logprob1, logprob2 = np.array(basic_lm.log_prob(test1)), np.array(basic_lm.log_prob(test2))

res = pd.DataFrame()
res["id"] = df_test["id"]
res["which"] = 0
res.loc[logprob2 >= logprob1, ["which"]] = 1

res.to_csv("submission.csv", sep=",", index=None, columns=["id", "which"])
