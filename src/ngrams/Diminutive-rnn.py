import pandas as pd
import re

from collections import defaultdict, Counter
from pathlib import Path
from random import choice, random


class DiminutiveGenerator:
    _RU_VOWELS = 'аеиоуыэюя'

    def __init__(self, ngram=2):
        self.ngram = ngram

        self.lang_model = defaultdict(Counter)
        self.lang_endings_model = defaultdict(Counter)
        self.diminutive_transits = defaultdict(Counter)
        self.start = '~'
        self.DIM_SUFFIX = re.compile(r'([иеё]к|[ая])$', re.I)

        self.language_model_default_denot = 9999
        self.diminutive_model_default_prob = 0.0001

    @staticmethod
    def _choose_letter(dist):
        if not dist:
            return 'ка'

        x = random()
        for c, v in dist:
            x = x - v
            if x <= 0:
                return c
        return choice(dist)[0]

    @staticmethod
    def _normalize(counter):
        total = float(sum(counter.values()))
        return [(c, cnt / total) for c, cnt in counter.items()]

    def _normalize_transits(self, history, counter):

        def get_prob_denot(hist, char):
            if hist not in self.lang_model:
                return self.language_model_default_denot
            elif self.lang_model[hist][char] <= 0:
                return sum(v for k, v in counter.items() if k[0] == char)
            else:
                return self.lang_model[history][char]

        return [(c, (cnt / get_prob_denot(history, c[0])))
                for c, cnt in sorted(counter.items(), key=lambda x: x[0][-1])]

    def _train_lm(self, names):
        print('Collecting of letters\' probabilities in language model...')
        for real_name in names:
            real_name = (real_name + '$').lower()
            n_chars = self.start * self.ngram
            for char in real_name:
                self.lang_model[n_chars][char] += 1
                n_chars = n_chars[1:] + char

    def _train_diminutive_model(self, names, diminutives):
        print('Collecting of letters\' probabilities in diminutive model...')
        for real_name, diminutive in zip(names, diminutives):
            real_name, diminutive = real_name.lower(), diminutive.lower()
            n_chars = self.start * self.ngram
            max_len = max(len(real_name), len(diminutive))
            i = 0
            while i < max_len:
                if i < len(real_name):
                    ch, dim_ch = real_name[i], diminutive[i]
                    if ch != dim_ch:
                        self.diminutive_transits[n_chars][(ch, dim_ch)] += 1
                        n_chars = n_chars[1:] + diminutive[i]
                    else:
                        n_chars = n_chars[1:] + real_name[i]
                    i += 1
                else:
                    if i == len(real_name) and diminutive[i] and real_name.endswith(n_chars):
                        ch, dim_ch = '$', diminutive[i]
                        self.diminutive_transits[n_chars][(ch, dim_ch)] += 1
                    else:
                        self.lang_endings_model[n_chars][diminutive[i]] += 1
                    n_chars = n_chars[1:] + diminutive[i]
                    i += 1

    def fit(self, path_to_sample_file):
        print('Get data from the file...')
        names, diminutives = [], []
        with Path(path_to_sample_file).open() as fin:
            for line in fin:
                real_name, diminutive = line.split()
                names += [real_name]
                diminutives += [diminutive]

        df = pd.DataFrame({'Name': names, 'Diminutive': diminutives})

        # collect language model
        self._train_lm(df.Name)
        # collect diminutive model
        self._train_diminutive_model(df.Name, df.Diminutive)
        self.lang_endings_model = {hist: self._normalize(chars)
                                   for hist, chars in self.lang_endings_model.items()}
        self.diminutive_transits = {hist: self._normalize_transits(hist, chars)
                                    for hist, chars in self.diminutive_transits.items()}
        self.lang_model = {hist: self._normalize(chars) for hist, chars in self.lang_model.items()}

        return self

    def _find_max_transition(self, word):
        letter, index, prob = '', 0, self.diminutive_model_default_prob
        max_hist = None
        for i in range(self.ngram, len(word)):
            ch = word[i]
            ngram_hist = word[i - self.ngram:i]
            if ngram_hist not in self.diminutive_transits:
                continue
            for t, v in self.diminutive_transits[ngram_hist]:
                if t[0] == ch and v >= prob:
                    prob = v
                    index = i
                    letter = t[0]
                    max_hist = self.diminutive_transits[ngram_hist]
        return index, letter, max_hist, prob

    def _generate_letter(self, history):
        history = history[-self.ngram:]
        if history not in self.lang_endings_model and self.ngram > 2:
            hists = [hist for hist in self.lang_endings_model if history.endswith(hist[1:])]
            dist = self.lang_endings_model[choice(hists)] if hists else None
        else:
            dist = self.lang_endings_model[history]
        return self._choose_letter(dist)

    def _normalize_k_suffix(self, word):
        if word.endswith('ка'):
            if word[-3] == 'ь':
                word = word[:-3] + 'я'
            elif word[-3] not in self._RU_VOWELS:
                word = word[:-2] + word[-1]
        return word

    def generate_diminutive(self, word):

        def select_hists_by_char(hists, char):
            selected_hists = []
            for h, d in hists:
                curr_transits = [(k, _) for k, _ in d if k[0] == char]
                if curr_transits:
                    selected_hists += [(h, curr_transits)]
            return selected_hists

        # check if word has 'ка' ending
        word = self._normalize_k_suffix(word)
        n_chars = self.start * self.ngram
        word = n_chars + word.lower()

        # find transition with max probability
        index, letter, max_hist, prob = self._find_max_transition(word)

        # process last name's symbols with default probability
        if prob <= self.diminutive_model_default_prob:
            if word[-1] not in self._RU_VOWELS and word[-self.ngram:] in self.diminutive_transits:
                max_hist = self.diminutive_transits[word[-self.ngram:]]
                index = len(word)
                letter = '$'
            elif word[-1] in self._RU_VOWELS and word[-self.ngram-1:-1] not in self.diminutive_transits:
                histories_by_last_ch = [
                    (h, d) for h, d in self.diminutive_transits.items() if h.endswith(word[-2])
                ]
                if histories_by_last_ch:
                    last = word[-1]
                    hists_by_last_ch = select_hists_by_char(histories_by_last_ch, last)
                    if hists_by_last_ch:
                        histories_by_last_ch = hists_by_last_ch
                    max_hist = choice(histories_by_last_ch)[-1]
                    index = len(word) - 1
                    letter = last
                else:
                    return word[self.ngram:].capitalize()
            else:
                return word[self.ngram:].capitalize()

        # generate text from position to 'а' letter
        max_hist_for_letter = [(tup, v) for tup, v in max_hist if tup[0] == letter]
        if max_hist_for_letter:
            max_hist = max_hist_for_letter

        if not max_hist:
            return word[self.ngram:].capitalize()

        # generate a tail of the diminutive
        first_dim_letter = self._choose_letter(max_hist)[-1]
        result = word[self.ngram:index] + first_dim_letter
        history = result[-self.ngram:]
        out = []
        while self.DIM_SUFFIX.search(history) is None:
            c = self._generate_letter(history)
            history = history[-self.ngram + 1:] + c
            out.append(c)

        return result.capitalize() + ''.join(out)


if __name__ == '__main__':
    CORPUS_TRAIN = 'resources/diminutive/train_diminutives.tsv'
    CORPUS_TEST = 'resources/diminutive/test_diminutives.tsv'

    gen = DiminutiveGenerator(ngram=2)
    gen.fit(CORPUS_TRAIN)

    data = pd.read_csv(CORPUS_TEST)
    for name in data.Name:
        print(gen.generate_diminutive(name))
