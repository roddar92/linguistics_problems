import numpy as np

from abc import ABC, abstractmethod
from math import log2, sqrt
from collections import defaultdict
from sklearn.feature_extraction.text import CountVectorizer

from sortedcontainers import SortedList


class Metric(ABC):
    @abstractmethod
    def evaluate(self, freq_w1, freq_w2, freq_w12, vocab_size):
        pass


class PMI(Metric):
    def evaluate(self, freq_w1, freq_w2, freq_w12, vocab_size):
        bigram_prob = freq_w12 / freq_w1
        return log2(bigram_prob * (vocab_size * freq_w2))


class TScore(Metric):
    def evaluate(self, freq_w1, freq_w2, freq_w12, vocab_size):
        p_w1 = freq_w1 / vocab_size
        p_w2 = freq_w2 / vocab_size
        p_w12 = freq_w12 / vocab_size
        diff = p_w12 - p_w1 * p_w2
        return diff / sqrt(p_w12 / vocab_size)


class LikelihoodRatio(Metric):
    def evaluate(self, freq_w1, freq_w2, freq_w12, vocab_size):
        def likelihood(k, n, x):
            u, v = x ** k, (1 - x) ** (n - k)
            return u * v

        p = freq_w2 / vocab_size
        p1 = freq_w12 / freq_w1
        p2 = (freq_w2 - freq_w12) / (vocab_size - freq_w1)
        first_L = likelihood(freq_w12, freq_w1, p)
        second_L = likelihood(freq_w2 - freq_w12, vocab_size - freq_w1, p)
        third_L = likelihood(freq_w12, freq_w1, p1)
        fourth_L = likelihood(freq_w2 - freq_w12, vocab_size - freq_w1, p2)
        return first_L + second_L - (third_L + fourth_L)


class Dice(Metric):
    def evaluate(self, freq_w1, freq_w2, freq_w12, vocab_size):
        p_w1 = freq_w1 / vocab_size
        p_w2 = freq_w2 / vocab_size
        p_w12 = freq_w12 / vocab_size
        return p_w12 / (p_w1 * p_w2)


class LanguageModel:
    def __init__(self, ngram_size=2):
        """
            Initialization of N-gram model
            :param ngram_size: size of n-gram, optional
        """

        if ngram_size < 2:
            raise Exception

        self.ngram_size = ngram_size

        self.bigram_vectorizer = CountVectorizer(token_pattern='(\\S+)', ngram_range=(ngram_size, ngram_size))
        self.onegram_vectorizer = CountVectorizer(token_pattern='(\\S+)',  ngram_range=(ngram_size - 1, ngram_size - 1))

        self.unigram_counts = defaultdict(lambda: 0)
        self.bigram_counts = defaultdict(lambda: 0)

        self.words_set_size = None

    def fit(self, sentences):
        """
            Training of the model on text sentences
            :param sentences: sentences list
        """

        print("Fitting sentences")

        counts_matrix = self.bigram_vectorizer.fit_transform(sentences)
        counts_context_matrix = self.onegram_vectorizer.fit_transform(sentences)

        self.words_set_size = len(
            set([key for ngram in self.bigram_vectorizer.vocabulary_.keys() for key in ngram.split(" ")]))

        print("Summing...")

        sum_ngram = np.sum(counts_matrix, axis=0).A1
        sum_context = np.sum(counts_context_matrix, axis=0).A1

        print("shapes: ", sum_ngram.shape, sum_context.shape)
        print("Iterating through ngrams...")

        for one_gram, index in self.onegram_vectorizer.vocabulary_.items():
            self.unigram_counts[one_gram] = sum_context[index]

        for two_gram, index in self.bigram_vectorizer.vocabulary_.items():
            self.bigram_counts[two_gram] = sum_ngram[index]

        return self
    
    def get_vocab_size(self):
        return self.words_set_size
    
    def get_unigrams(self):
        return self.unigram_counts
    
    def get_bigrams(self):
        return self.bigram_counts


class CollocationExtractor:
    def __init__(self, lm):
        self.language_model = lm

    def extract_collocations(self, metric_class):
        assert issubclass(metric_class, Metric)
        metric = metric_class()
        collocations = SortedList()
        
        unigrams = self.language_model.get_unigrams()
        bigrams = self.language_model.get_bigrams()

        for bigram, freq_bigram in bigrams.items():
            first, last = bigram.split()
            freq_first, freq_last = unigrams[first], unigrams[last]
            
            metric_val = metric.evaluate(freq_first, freq_last, freq_bigram, self.language_model.get_vocab_size())
            collocations.add((metric_val, freq_first, freq_last, freq_bigram, bigram))
            
        return collocations
