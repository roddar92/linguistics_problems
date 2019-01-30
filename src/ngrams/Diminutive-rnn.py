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
        return dist[-1][0]

    @staticmethod
    def _normalize(counter):
        total = float(sum(counter.values()))
        return [(c, cnt / total) for c, cnt in counter.items()]

    def _normalize_transits(self, history, counter):
        # print(history, counter)
        # print(self.lang_model[history])
        def _get_prob(hist, char):
            if not self.lang_model[hist] or not self.lang_model[hist][char]:
                return self.language_model_default_prob
            else:
                return self.lang_model[history][char]

        return [(c, (cnt / _get_prob(history, c[0]))) for c, cnt in counter.items()]

    def _train_lm(self, names, ngram):
        print('Collecting of letters\' probabilities in language model...')
        for real_name in names:
            real_name = real_name.lower()
            n_chars = self.start * ngram
            for char in real_name:
                self.lang_model[n_chars][char] += 1
                n_chars = n_chars[1:] + char

    def _train_diminutive_model(self, names, diminutives, ngram):
        print('Collecting of letters\' probabilities in diminutive model...')
        for real_name, diminutive in zip(names, diminutives):
            real_name, diminutive = real_name.lower(), diminutive.lower()
            n_chars = self.start * ngram
            max_len = max(len(real_name), len(diminutive))
            for i in range(max_len):
                if i < len(real_name):
                    ch, dim_ch = real_name[i], diminutive[i]
                    if ch != dim_ch:
                        self.diminutive_transitions[n_chars][(ch, dim_ch)] += 1
                        self.language_model[n_chars][ch] += 1
                        self.language_model[n_chars][dim_ch] += 1
                        n_chars = n_chars[1:] + diminutive[i]
                    else:
                        self.language_model[n_chars][ch] += 1
                        n_chars = n_chars[1:] + real_name[i]
                else:
                    self.language_model[n_chars][diminutive[i]] += 1
                    n_chars = n_chars[1:] + diminutive[i]

    def fit(self, path_to_sample_file, ngram=2):
        print('Get data from the file...')
        names, diminutives = [], []
        with Path(path_to_sample_file).open() as fin:
            for line in fin:
                real_name, diminutive = line.split()
                names += [real_name]
                diminutives += [diminutive]

        df = pd.DataFrame({'Name': names, 'Diminutive': diminutives})

        # collect language model
        self._train_lm(df.Name, ngram)
        # collect diminutive model
        self._train_diminutive_model(df.Name, df.Diminutive, ngram)
        self.language_model = {hist: self._normalize(chars) for hist, chars in self.language_model.items()}
        self.diminutive_transitions = {hist: self._normalize_transits(hist, chars)
                                       for hist, chars in self.diminutive_transitions.items()}
        self.lang_model = {hist: self._normalize(chars) for hist, chars in self.lang_model.items()}

        return self

    def _generate_letter(self, history, ngram):
        history = history[-ngram:]
        if history in self.language_model:
            dist = self.language_model[history]
            return self._choose_letter(dist)
        return ''

    def generate_diminutive(self, word, ngram=2):
        # find transition with max prob
        letter, index, prob = '', 0, 0
        max_hist = None
        n_chars = self.start * ngram
        word = n_chars + word.lower()
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
                    letter = t
                    max_hist = self.diminutive_transitions[ngram_hist]

        if prob == self.diminutive_model_default_prob:
            return word

        # generate text from position to 'а' letter
        max_hist_for_letter = [(tup, v) for tup, v in max_hist if tup[0] == letter[0]]
        if max_hist_for_letter:
            max_hist = max_hist_for_letter

        if not max_hist:
            return word

        first_dim_letter = self._choose_letter(max_hist)[-1]
        result = word[:index] + first_dim_letter
        history = result[-ngram:]
        out = []
        while not history.endswith('а') and not history.endswith('я'):
            c = self._generate_letter(history, ngram)
            history = history[-ngram:] + c
            out.append(c)

        return result[2:].capitalize() + ''.join(out)


if __name__ == '__main__':
    CORPUS_TRAIN = 'resources/diminutive/train_diminutives.tsv'
    CORPUS_TEST = 'resources/diminutive/test_diminutives.tsv'

    gen = DiminutiveGenerator()
    gen.fit(CORPUS_TRAIN)

    data = pd.read_csv(CORPUS_TEST)
    for name in data.Name:
        print(gen.generate_diminutive(name))
