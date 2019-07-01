from pathlib import Path

import numpy as np
import pandas as pd

from collections import defaultdict, Counter
from nltk import bigrams, word_tokenize


class WordFiller:
    START, END = '^', '^'

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

        self.dict_list = None

    def fit(self, path_to_train_file):
        with Path(path_to_train_file).open('r') as fin:
            print("Iterating through ngrams...")
            n = 0
            while True:
                sentence = fin.readline()
                if not sentence:
                    break

                sent = f'{self.START} {sentence} {self.END}'.split()
                self.unigram_counts.update(Counter(sent))
                self.bigram_counts.update(Counter(' '.join([sent[i], sent[i+1]]) for i in range(len(sent) - 1)))
                n += 1
                if n % 100000 == 0:
                    print(f"Processed {n} lines")

        self.vocab_size = len(self.unigram_counts)

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

    def __calc_phrase_prob(self, *ngrams):
        return sum(self.__calculate_prob(ngram) for ngram in ngrams)

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
        def bigrams_2_text(l):
            return [x[-1] for x in l[:-1]]

        sent = f'{self.START} {sentence} {self.END}'
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

    weights_values = [.7, .3]
    basic_lm = WordFiller(ngram=2, weights=weights_values)

    print("Obtain data...")
    basic_lm.fit(path_to_train_file="resources/word_filler/train_v2.txt")

    print("Trained")

    df_test = pd.read_csv("resources/word_filler/test_v2.txt")
    print("Read test data, shape: ", df_test.shape)

    res = pd.DataFrame()
    for _, row in df_test.iterrows():
        res["id"] = df_test["id"]
        res["text"] = basic_lm.fill_text(row)

    res.to_csv("resources/word_filler/submission.csv", sep=",", index=None, columns=["id", "text"])
