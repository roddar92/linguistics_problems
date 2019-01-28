import pandas as pd

from collections import defaultdict, Counter
from pathlib import Path
from random import random


class DiminutiveGenerator:
    def __init__(self):
        self.lang_model = defaultdict(Counter)
        self.language_model = defaultdict(Counter)
        self.diminutive_transitions = defaultdict(Counter)
        self.start = '~'

        self.language_model_default_prob = 1e999
        self.diminutive_model_default_prob = 1e-999

    @staticmethod
    def _choose_letter(dist):
        x = random()
        for c, v in dist:
            x = x - v
            if x <= 0:
                return c

    @staticmethod
    def _normalize(counter):
        total = float(sum(counter.values()))
        return [(c, cnt / total) for c, cnt in counter.items()]

    def _normalize_transits(self, history, counter):
        # print(history, counter)
        # print(self.lang_model[history])
        def _get_prob(history, char):
            if not self.lang_model[history] or not self.lang_model[history][char]:
                return self.language_model_default_prob
            else:
                return self.lang_model[history][char]

        return [(c, (cnt / _get_prob(history, c[0]))) for c, cnt in counter.items()]

    def _train_lm(self, names, ngram):
        print('Collecting of letters\' probabilities in language model...')
        for name in names:
            name = name.lower()
            n_chars = self.start * ngram
            for char in name:
                self.lang_model[n_chars][char] += 1
                n_chars = n_chars[1:] + char

    def _train_diminutive_model(self, names, diminutives, ngram):
        print('Collecting of letters\' probabilities in diminutive model...')
        for name, diminutive in zip(names, diminutives):
            name, diminutive = name.lower(), diminutive.lower()
            n_chars = self.start * ngram
            max_len = max(len(name), len(diminutive))
            for i in range(max_len):
                if i < len(name):
                    ch, dim_ch = name[i], diminutive[i]
                    if ch != dim_ch:
                        # if n_chars == 'ми':
                        #    print(name, diminutive)
                        self.diminutive_transitions[n_chars][(ch, dim_ch)] += 1
                        self.language_model[n_chars][ch] += 1
                        self.language_model[n_chars][dim_ch] += 1
                        n_chars = n_chars[1:] + diminutive[i]
                    else:
                        self.language_model[n_chars][ch] += 1
                        n_chars = n_chars[1:] + name[i]
                else:
                    self.language_model[n_chars][diminutive[i]] += 1
                    n_chars = n_chars[1:] + diminutive[i]

    def fit(self, path_to_sample_file, ngram=2):
        print('Get data from the file...')
        names, diminutives = [], []
        with Path(path_to_sample_file).open() as fin:
            for line in fin:
                name, diminutive = line.split()
                names += [name]
                diminutives += [diminutive]

        data = pd.DataFrame({'Name': names, 'Diminutive': diminutives})

        # collect language model
        self._train_lm(data.Name, ngram)
        # collect diminutive model
        self._train_diminutive_model(data.Name, data.Diminutive, ngram)
        self.language_model = {hist: self._normalize(chars) for hist, chars in self.language_model.items()}
        self.diminutive_transitions = {hist: self._normalize_transits(hist, chars)
                                       for hist, chars in self.diminutive_transitions.items()}
        self.lang_model = {hist: self._normalize(chars) for hist, chars in self.lang_model.items()}

        return self

    def _generate_letter(self, history, ngram):
        history = history[-ngram:]
        dist = self.language_model[history]
        return self._choose_letter(dist)

    def generate_diminutive(self, word, ngram=2):
        # find transition with max prob
        hist, letter, index, prob = '', '', 0, 0
        max_hist = None
        n_chars = self.start * ngram
        word = n_chars + word
        for i in range(ngram, len(word)):
            ch = word[i]
            ngram_hist = word[i - ngram:i]
            if ngram_hist not in self.diminutive_transitions or not self.diminutive_transitions[ngram_hist]:
                prob = self.diminutive_model_default_prob
                continue
            for t, v in self.diminutive_transitions[ngram_hist]:
                if t[0] == ch and v > prob:
                    prob = v
                    index = i
                    letter = t[1]
                    hist = word[i - ngram:i]
                    max_hist = self.diminutive_transitions[ngram_hist]

        if prob == self.diminutive_model_default_prob:
            return word

        # generate text from position to 'а' letter
        first_dim_letter = self._choose_letter(max_hist)[-1]
        result = word[:index] + first_dim_letter
        history = result[-ngram:]
        out = []
        while not history.endswith('а') and not history.endswith('я'):
            c = self._generate_letter(history, ngram)
            history = history[-ngram:] + c
            out.append(c)

        return result + ''.join(out)


if __name__ == '__main__':
    CORPUS_TRAIN = 'resources/diminutive/train_diminutives.tsv'
    CORPUS_TEST = 'resources/diminutive/test_diminutives.tsv'

    gen = DiminutiveGenerator()
    gen.fit(CORPUS_TRAIN)

    data = pd.read_csv(CORPUS_TEST)
    for name in data.Name:
        print(gen.generate_diminutive(name)[2:])
