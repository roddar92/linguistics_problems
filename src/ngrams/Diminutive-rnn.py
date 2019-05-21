import pandas as pd

from collections import defaultdict, Counter
from pathlib import Path
from random import choice, random


class DiminutiveGenerator:
    _KA_ENDING = 'ка'
    _RU_VOWELS = 'аеиоуыэюя'
    _LAST_LETTER = _RU_VOWELS + 'ь'
    _DIM_ENDING = '$'
    _START = '~'

    LANGUAGE_DEFAULT_PROB = 0.0001
    DIMINUTIVE_DEFAULT_PROB = 0.0001

    def __init__(self, ngram=2):
        if ngram < 2:
            raise Exception('Ngram parameter should be greater or equal 2 characters!')

        self.ngram = ngram

        self.lang_model = defaultdict(Counter)
        self.lang_endings_model = defaultdict(Counter)
        self.lang_endings_context = defaultdict(Counter)
        self.diminutive_transits = defaultdict(Counter)

    @staticmethod
    def _read_diminutive_samples(path_to_sample_file):
        with Path(path_to_sample_file).open() as fin:
            names = (line.split() for line in fin.readlines())
        return pd.DataFrame(names, columns=['Name', 'Diminutive'])

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

    @staticmethod
    def _normalize_transits(counter):
        def get_prob_denot(char):
            return sum(v for k, v in counter.items() if k[0] == char)

        return [(c, (cnt / get_prob_denot(c[0])))
                for c, cnt in sorted(counter.items(), key=lambda x: x[0][-1])]

    def _train_lm(self, names):
        print('Collecting of letters\' probabilities in language model...')
        for real_name in names:
            real_name = f'{real_name.lower()}$'
            n_chars = self._START * self.ngram
            for char in real_name:
                self.lang_model[n_chars][char] += 1
                n_chars = n_chars[1:] + char

    def _train_diminutive_model(self, names, diminutives):
        print('Collecting of letters\' probabilities in diminutive model...')
        for real_name, diminutive in zip(names, diminutives):
            real_name, diminutive = real_name.lower(), f'{diminutive.lower()}$'
            stay_within_name = True
            n_chars = self._START * self.ngram
            max_len = max(len(real_name), len(diminutive))
            for i in range(max_len):
                if i < len(real_name) and stay_within_name:
                    ch, dim_ch = real_name[i], diminutive[i]
                    if ch != dim_ch:
                        stay_within_name = False
                        self.diminutive_transits[n_chars][(ch, dim_ch)] += 1
                        next_char = diminutive[i]
                    else:
                        next_char = real_name[i]
                    n_chars = n_chars[1:] + next_char
                else:
                    if i == len(real_name) and real_name.endswith(n_chars):
                        ch, dim_ch = '$', diminutive[i]
                        self.diminutive_transits[n_chars][(ch, dim_ch)] += 1
                    elif i < len(diminutive):
                        self.lang_endings_model[n_chars][diminutive[i]] += 1
                        self.lang_endings_context[n_chars[1:]][diminutive[i]] += 1
                    else:
                        break
                    n_chars = n_chars[1:] + diminutive[i]

    def fit(self, path_to_sample_file):
        print('Get data from the file...')
        df = self._read_diminutive_samples(path_to_sample_file)

        # collect language model
        self._train_lm(df.Name)

        # collect diminutive model
        self._train_diminutive_model(df.Name, df.Diminutive)

        # normalize models
        self.lang_endings_model = {hist: self._normalize(chars)
                                   for hist, chars in self.lang_endings_model.items()}
        self.lang_endings_context = {hist: self._normalize(chars)
                                     for hist, chars in self.lang_endings_context.items()}
        self.diminutive_transits = {hist: self._normalize_transits(chars)
                                    for hist, chars in self.diminutive_transits.items()}
        self.lang_model = {hist: self._normalize(chars) for hist, chars in self.lang_model.items()}

        return self

    def _get_lm_prob(self, hist, char):
        if hist not in self.lang_model:
            return self.LANGUAGE_DEFAULT_PROB
        else:
            for c, v in self.lang_model[hist]:
                if c == char:
                    return v
            return self.LANGUAGE_DEFAULT_PROB

    def _find_max_transition(self, word):
        # find the max prob Lang(history, char) * Transit(history, char) and extremal arguments

        max_hist = None
        letter, index = '', 0
        prob = self.DIMINUTIVE_DEFAULT_PROB
        start = len(word) // 2 + self.ngram

        for i in range(start, len(word)):
            ch, ngram_hist = word[i], word[i - self.ngram:i]
            if ngram_hist not in self.diminutive_transits:
                continue
            lm_prob = self._get_lm_prob(ngram_hist, ch)
            for t, p in self.diminutive_transits[ngram_hist]:
                cond_prob = p * lm_prob
                if t[0] == ch and cond_prob >= prob:
                    prob, index, letter = cond_prob, i, t[0]
                    max_hist = self.diminutive_transits[ngram_hist]
        return index, letter, max_hist, prob

    def _generate_letter(self, history):
        if history not in self.lang_endings_model:
            last_hist = history[1:]
            dist = self.lang_endings_context[last_hist] if last_hist in self.lang_endings_context else None
        else:
            dist = self.lang_endings_model[history]

        if not dist:
            return self._KA_ENDING

        return self._choose_letter(dist)

    def _generate_diminutive_tail(self, history):
        tail = []
        while True:
            c = self._generate_letter(history)
            if c == self._DIM_ENDING:
                break

            history = history[-self.ngram + 1:] + c
            tail.append(c)

            if c == self._KA_ENDING:
                break
        return tail

    def _normalize_k_suffix(self, word):
        if word.endswith(self._KA_ENDING):
            if word[-3] in 'йь':
                return word[:-3] + 'я'
            elif word[-3] not in self._RU_VOWELS:
                return word[:-2] + word[-1]
        return word

    @staticmethod
    def _select_hists_by_char(word, hists, char):
        def select_by_char(histories):
            candidates = []
            for h, d in histories:
                curr_transits = [(k, _) for k, _ in d if k[0] == char]
                if curr_transits:
                    candidates += [(h, curr_transits)]
            return candidates

        selected_hists = [(hist, _) for hist, _ in hists if word.endswith(hist)]
        if selected_hists:
            return select_by_char(selected_hists)

        return select_by_char(hists)

    def generate_diminutive(self, word):

        # check if word has 'ка' ending and normalize name
        word = self._normalize_k_suffix(word)

        # fill name with ngram start
        n_chars = self._START * self.ngram
        word = n_chars + word.lower()

        # find transition with max probability
        index, letter, max_hist, prob = self._find_max_transition(word)

        # process last name's symbols with default probability
        if prob <= self.DIMINUTIVE_DEFAULT_PROB:
            index = len(word) - (0 if word[-1] not in self._LAST_LETTER else 2 if word.endswith('ха') else 1)
            letter = '$' if word[-1] not in self._LAST_LETTER else word[-1]

            ngram = self.ngram - 1
            histories_by_last_ch = [
                (h, _) for h, _ in self.diminutive_transits.items() if h.endswith(word[index-ngram:index])
            ]
            if histories_by_last_ch:
                hists_by_last_ch = self._select_hists_by_char(word, histories_by_last_ch, letter)
                if hists_by_last_ch:
                    histories_by_last_ch = hists_by_last_ch
                max_hist = choice(histories_by_last_ch)[-1]
            else:
                return word[self.ngram:].capitalize()

        # select transits with first character which equal the letter of a name
        max_hist_for_letter = [(tup, _) for tup, _ in max_hist if tup[0] == letter]
        if max_hist_for_letter:
            max_hist = max_hist_for_letter

        if not max_hist:
            return word[self.ngram:].capitalize()

        # generate a tail of the diminutive (to 'a' character)
        first_dim_letter = self._choose_letter(max_hist)[-1]
        result = word[self.ngram:index] + first_dim_letter
        tail = self._generate_diminutive_tail(result[-self.ngram:])

        return result.capitalize() + ''.join(tail)


if __name__ == '__main__':
    CORPUS_TRAIN = 'resources/diminutive/train_diminutives.tsv'
    CORPUS_TEST = 'resources/diminutive/test_diminutives.tsv'

    gen = DiminutiveGenerator(ngram=3)
    gen.fit(CORPUS_TRAIN)

    data = pd.read_csv(CORPUS_TEST)
    for name in data.Name:
        print(gen.generate_diminutive(name))
