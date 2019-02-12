import pandas as pd

from collections import defaultdict, Counter
from pathlib import Path
from random import random, randint


class DiminutiveGenerator:
    _RU_VOWELS = 'аеиоуыэюя'

    def __init__(self):
        self.lang_model = defaultdict(Counter)
        self.lang_endings_model = defaultdict(Counter)
        self.diminutive_transits = defaultdict(Counter)
        self.start = '~'

        self.language_model_default_prob = 9999
        self.diminutive_model_default_prob = 0.0001

    @staticmethod
    def _choose_letter(dist):
        x = random()
        for c, v in dist:
            x = x - v
            if x <= 0:
                return c
        ind = randint(0, len(dist) - 1)
        return dist[ind][0]

    @staticmethod
    def _normalize(counter):
        total = float(sum(counter.values()))
        return [(c, cnt / total) for c, cnt in counter.items()]

    def _normalize_transits(self, history, counter):

        def get_prob_denot(hist, char):
            if hist not in self.lang_model:
                return self.language_model_default_prob
            elif self.lang_model[hist][char] <= 0:
                return sum(v for k, v in counter.items() if k[0] == char)
            else:
                return self.lang_model[history][char]

        return [(c, (cnt / get_prob_denot(history, c[0]))) for c, cnt in counter.items()]

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
                        self.diminutive_transits[n_chars][(ch, dim_ch)] += 1
                        self.lang_endings_model[n_chars][dim_ch] += 1
                        n_chars = n_chars[1:] + diminutive[i]
                    else:
                        n_chars = n_chars[1:] + real_name[i]
                else:
                    if i == len(real_name) and diminutive[i] and real_name.endswith(n_chars):
                        ch, dim_ch = '$', diminutive[i]
                        self.diminutive_transits[n_chars][(ch, dim_ch)] += 1
                    self.lang_endings_model[n_chars][diminutive[i]] += 1
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
        self.lang_endings_model = {hist: self._normalize(chars)
                                   for hist, chars in self.lang_endings_model.items()}
        self.diminutive_transits = {hist: self._normalize_transits(hist, chars)
                                    for hist, chars in self.diminutive_transits.items()}
        self.lang_model = {hist: self._normalize(chars) for hist, chars in self.lang_model.items()}

        return self

    def _find_max_transition(self, word, ngram):
        letter, index, prob = '', 0, self.diminutive_model_default_prob
        max_hist = None
        for i in range(ngram, len(word)):
            ch = word[i]
            ngram_hist = word[i - ngram:i]
            if ngram_hist not in self.diminutive_transits:
                continue
            for t, v in self.diminutive_transits[ngram_hist]:
                if t[0] == ch and v >= prob:
                    prob = v
                    index = i
                    letter = t[0]
                    max_hist = self.diminutive_transits[ngram_hist]
        return index, letter, max_hist, prob

    def _generate_letter(self, history, ngram):
        history = history[-ngram:]
        dist = self.lang_endings_model[history]
        return self._choose_letter(dist)

    def _normalize_k_suffix(self, word):
        if word.endswith('ка'):
            if word[-3] == 'ь':
                word = word[:-3] + 'я'
            elif word[-3] not in self._RU_VOWELS:
                word = word[:-2] + word[-1]
        return word

    def generate_diminutive(self, word, ngram=2):

        def select_hists_by_char(hists, char):
            selected_hists = []
            for h, d in hists:
                curr_transits = [(k, _) for k, _ in d if k[0] == char]
                if curr_transits:
                    selected_hists += [(h, curr_transits)]
            return selected_hists

        # check if word has 'ка' ending
        word = self._normalize_k_suffix(word)
        n_chars = self.start * ngram
        word = n_chars + word.lower()

        # find transition with max probability
        index, letter, max_hist, prob = self._find_max_transition(word, ngram)

        # process last name's symbols with default probability
        if prob <= self.diminutive_model_default_prob:
            if word[-1] not in self._RU_VOWELS and word[-2:] in self.diminutive_transits:
                max_hist = self.diminutive_transits[word[-2:]]
                index = len(word)
                letter = '$'
            elif word[-1] in self._RU_VOWELS and word[-3:-1] not in self.diminutive_transits:
                histories_by_last_ch = [
                    (h, d) for h, d in self.diminutive_transits.items() if h.endswith(word[-2])
                ]
                if histories_by_last_ch:
                    last = word[-1]
                    hists_by_last_ch = select_hists_by_char(histories_by_last_ch, last)
                    if hists_by_last_ch:
                        histories_by_last_ch = hists_by_last_ch
                    rand_ind = randint(0, len(histories_by_last_ch) - 1)
                    max_hist = histories_by_last_ch[rand_ind][-1]
                    index = len(word) - 1
                    letter = last
                else:
                    return word[2:].capitalize()
            else:
                return word[2:].capitalize()

        # generate text from position to 'а' letter
        max_hist_for_letter = [(tup, v) for tup, v in max_hist if tup[0] == letter]
        if max_hist_for_letter:
            max_hist = max_hist_for_letter

        if not max_hist:
            return word[2:].capitalize()

        # generate a tail of the diminutive
        first_dim_letter = self._choose_letter(max_hist)[-1]
        result = word[2:index] + first_dim_letter
        history = result[-ngram:]
        out = []
        while not history.endswith('а') and not history.endswith('я') and not history.endswith('ик'):
            c = self._generate_letter(history, ngram)
            history = history[-ngram:] + c
            out.append(c)

        return result.capitalize() + ''.join(out)


if __name__ == '__main__':
    CORPUS_TRAIN = 'resources/diminutive/train_diminutives.tsv'
    CORPUS_TEST = 'resources/diminutive/test_diminutives.tsv'

    gen = DiminutiveGenerator()
    gen.fit(CORPUS_TRAIN)

    data = pd.read_csv(CORPUS_TEST)
    for name in data.Name:
        print(gen.generate_diminutive(name))
