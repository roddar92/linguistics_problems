import string

from abc import ABC, abstractmethod
from math import log2, sqrt
from collections import Counter

from nltk import bigrams, word_tokenize
from sortedcontainers import SortedList


class Metric(ABC):
    @abstractmethod
    def evaluate(self, freq_w1, freq_w2, freq_w12, vocab_size):
        pass


class PMI(Metric):
    def evaluate(self, freq_w1, freq_w2, freq_w12, vocab_size):
        p_w1 = freq_w1 / vocab_size
        p_w2 = freq_w2 / vocab_size
        p_w12 = freq_w12 / vocab_size
        return log2(p_w12 / (p_w1 * p_w2))


class MD(Metric):
    def evaluate(self, freq_w1, freq_w2, freq_w12, vocab_size):
        p_w1 = freq_w1 / vocab_size
        p_w2 = freq_w2 / vocab_size
        p_w12 = freq_w12 / vocab_size
        return log2((p_w12 ** 2) / (p_w1 * p_w2))


class TScore(Metric):
    def evaluate(self, freq_w1, freq_w2, freq_w12, vocab_size):
        p_w1 = freq_w1 / vocab_size
        p_w2 = freq_w2 / vocab_size
        p_w12 = freq_w12 / vocab_size
        diff = p_w12 - p_w1 * p_w2
        s = p_w12 * (1 - p_w12)
        return diff / sqrt(s / vocab_size)


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


class Ratio(Metric):
    def evaluate(self, freq_w1, freq_w2, freq_w12, vocab_size):
        p_w1 = freq_w1 / vocab_size
        p_w2 = freq_w2 / vocab_size
        p_w12 = freq_w12 / vocab_size
        return p_w12 / (p_w1 * p_w2)


class Dice(Metric):
    def evaluate(self, freq_w1, freq_w2, freq_w12, vocab_size):
        return (2 * freq_w12) / (freq_w1 + freq_w2)


class LanguageModel:
    def __init__(self, ngram_size=2, lowercase=False):
        """
            Initialization of N-gram model
            :param ngram_size: size of n-gram, optional
        """

        if ngram_size < 2:
            raise Exception

        self.ngram_size = ngram_size

        self.unigram_counts = None
        self.bigram_counts = None

        self.words_set_size = None
        self.lowercase = lowercase

    def fit(self, text):
        """
            Training of the model on texts
            :param text: sentences list
        """

        if self.lowercase:
            text = text.lower()

        print("Tokenize sentences...")
        tokens = word_tokenize(text)

        self.words_set_size = len(set(tokens))

        print("Collecting of ngram counters...")

        self.unigram_counts = Counter(tokens)
        self.bigram_counts = Counter(bigrams(tokens))

        return self
    
    def get_vocab_size(self):
        return self.words_set_size
    
    def get_unigrams(self):
        return self.unigram_counts
    
    def get_bigrams(self):
        return self.bigram_counts


class CollocationExtractor:
    CONJ_RU = set('и а да но'.split())
    PROPOSITIONS_RU = set('с со на из за в к ко по про о у об обо под над от до'.split())
    PUNCT = set(string.punctuation) | {'--', '...'}

    def __init__(self, lm, exclude_punctuation=True, exclude_conj=True, exclude_props=True):
        self.language_model = lm
        self.exclude_punctuation = exclude_punctuation
        self.exclude_conj = exclude_conj
        self.exclude_props = exclude_props

    def extract_collocations(self, metric_class):
        assert issubclass(metric_class, Metric)
        metric = metric_class()
        collocations = SortedList(key=lambda x: -x[0])
        
        unigram_counts = self.language_model.get_unigrams()
        bigram_counts = self.language_model.get_bigrams()

        for (first, last), freq_bigram in bigram_counts.items():

            if self.exclude_punctuation:
                if first in self.PUNCT or last in self.PUNCT:
                    continue

            if self.exclude_conj:
                if first in self.CONJ_RU or last in self.CONJ_RU:
                    continue

            if self.exclude_props:
                if first in self.PROPOSITIONS_RU or last in self.PROPOSITIONS_RU:
                    continue

            freq_first, freq_last = unigram_counts[first], unigram_counts[last]
            
            metric_val = metric.evaluate(freq_first, freq_last, freq_bigram,
                                         self.language_model.get_vocab_size())
            collocations.add((metric_val, freq_first,
                              freq_last, freq_bigram,
                              first, last))
            
        return collocations


if __name__ == '__main__':
    fname = "resources/corpus/Dostoevsky.txt"
    with open(fname, 'r', encoding='utf-8') as fin:
        data = fin.read()

        model = LanguageModel(lowercase=True)
        model.fit(data)

        collocations_extractor = CollocationExtractor(lm=model)

        print("Mutual Information results...")
        collocations_list = collocations_extractor.extract_collocations(PMI)
        for collocation in collocations_list[:100]:
            print(collocation)

        print("Mutual Dependence results...")
        collocations_list = collocations_extractor.extract_collocations(MD)
        for collocation in collocations_list[:100]:
            print(collocation)

        print("T-Score results...")
        collocations_list = collocations_extractor.extract_collocations(TScore)
        for collocation in collocations_list[:100]:
            print(collocation)

        print("Likelihood Ratio results...")
        collocations_list = collocations_extractor.extract_collocations(LikelihoodRatio)
        for collocation in collocations_list[:100]:
            print(collocation)

        print("Ratio results...")
        collocations_list = collocations_extractor.extract_collocations(Ratio)
        for collocation in collocations_list[:100]:
            print(collocation)

        print("Dice results...")
        collocations_list = collocations_extractor.extract_collocations(Dice)
        for collocation in collocations_list[:100]:
            print(collocation)
