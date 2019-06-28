from pathlib import Path

import numpy as np
import pandas as pd

from collections import defaultdict
from nltk import bigrams, word_tokenize
from sklearn.feature_extraction.text import CountVectorizer


class WordFiller:
    START = '~'

    def __init__(self, ngram, weights, alpha=1.0):
        if ngram < 2:
            raise Exception('N-gram parameter should be at least 2 size!')
        if ngram != len(weights):
            raise Exception('N-gram and length of weights array should be the same size!')

        self.alpha = alpha
        self.ngram = ngram
        self.weights = weights
        self.vocab_size = None

        self.unigram_counts = defaultdict(lambda: 0)
        self.bigram_counts = defaultdict(lambda: 0)

        self.bigram_vectorizer = CountVectorizer(token_pattern='(\\S+)', ngram_range=(ngram - 1, ngram - 1))
        self.ugram_vectorizer = CountVectorizer(token_pattern='(\\S+)', ngram_range=(ngram - 2, ngram - 2))

        self.dict_list = None

    def fit(self, sentences):
        counts_context_matrix = self.ugram_vectorizer.fit_transform(sentences)

        self.vocab_size = len(
            set([key for ngram in self.ugram_vectorizer.vocabulary_.keys() for key in ngram.split(" ")]))

        sentences = [f'{self.START} {sent} {self.START}' for sent in sentences]
        counts_bi_matrix = self.bigram_vectorizer.fit_transform(sentences)

        sum_bi_ngram = np.sum(counts_bi_matrix, axis=0).A1
        sum_context = np.sum(counts_context_matrix, axis=0).A1

        print("shapes: ", sum_bi_ngram.shape, sum_context.shape)
        print("Iterating through ngrams...")

        for one_gram, index in self.ugram_vectorizer.vocabulary_.items():
            self.unigram_counts[one_gram] = sum_context[index]

        for two_gram, index in self.bigram_vectorizer.vocabulary_.items():
            self.bigram_counts[two_gram] = sum_bi_ngram[index]

        self.dict_list = [self.bigram_counts, self.unigram_counts]
        return self

    def __calculate_prob(self, ngram):
        """
            Evaluate probability logarithm of a n-gram
            :param ngram: string with n words
            :return: probability logarithm
        """
        tokens = ngram.split()
        prob = 0

        for i in range(self.ngram - 1):
            sub_gram = tokens[i:]
            sub_context = sub_gram[:-1]
            prob += self.weights[i] * (
                    (self.dict_list[i][' '.join(sub_gram)] + self.alpha) /
                    (self.alpha * self.vocab_size + self.dict_list[i + 1][' '.join(sub_context)]))

        return np.log2(prob)

    def __calc_phrase_prob(self, *trigrams):
        return sum(self.__calculate_prob(trigram) for trigram in trigrams)

    def _fill_word(self, ngram, ngram_prob):
        fst_w, sec_w = ngram.split()

        candidates = self.__collect_candidates(fst_w, sec_w)
        best_ngrams = candidates[0]

        return best_ngrams[0] if best_ngrams[-1] > ngram_prob else (ngram,)

    def __collect_candidates(self, first, second):
        candidates = []
        for bgram in self.bigram_counts:
            if bgram.startswith(first):
                sec_bgram = f'{bgram.split()[-1]} {second}'
                triple = ((bgram, sec_bgram), self.__calc_phrase_prob(bgram, sec_bgram))
                candidates.append(triple)
            if bgram.endswith(second):
                fst_bgram = f'{first} {bgram.split()[0]}'
                triple = ((fst_bgram, bgram), self.__calc_phrase_prob(fst_bgram, bgram))
                candidates.append(triple)
        candidates = sorted(candidates, key=lambda x: -x[-1])
        return candidates

    def fill_text(self, sentence):
        def bigrams_2_text(bigrams):
            return [x[-1] for x in bigrams[:-1]]

        sent = f'{self.START} {sentence} {self.START}'
        sent_bigrams = list(bigrams(word_tokenize(sent)))

        min_prob, min_ind = 1.0, -1
        for i, bgram in enumerate(sent_bigrams):
            prob = self.__calculate_prob(bgram)
            if prob < min_prob:
                min_prob = prob
                min_ind = i

        ngrams_new = self._fill_word(sent_bigrams[min_ind], min_prob)
        if sent_bigrams[min_ind] != ngrams_new:
            sent_bigrams.pop(min_ind)
            sent_bigrams[min_ind:min_ind] = list(ngrams_new)

        return ' '.join(bigrams_2_text(sent_bigrams))


if __name__ == '__main__':

    print("Read train data...")
    with Path("resources/word_filler/train_v2.txt").open('r') as fin:
        data = (line for line in fin.readlines())

    df_train = pd.DataFrame(data, columns=['text'])

    print("Read test data...")
    df_test = pd.read_csv("resources/word_filler/test_v2.txt")

    print("Read: ", df_train.shape, df_test.shape)

    weights_values = [.7, .3]
    basic_lm = WordFiller(ngram=2, weights=weights_values)
    sentences_train = df_train["text"].tolist()
    sentences_train = [sentence for sentence in sentences_train]
    basic_lm.fit(sentences=sentences_train)

    print("Trained")

    res = pd.DataFrame()
    for _, row in df_test.iterrows():
        res["id"] = df_test["id"]
        res["text"] = basic_lm.fill_text(row)

    res.to_csv("resources/word_filler/submission.csv", sep=",", index=None, columns=["id", "text"])
