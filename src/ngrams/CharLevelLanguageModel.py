from collections import defaultdict, Counter
from pathlib import Path
from random import random


class CharLevelLanguageModel:
    def __init__(self, ngram=10):
        self.lm = defaultdict(Counter)
        self.ngram = ngram
        self.start = '~'

    def train(self, path_to_corpus_file):
        print('Get data from the file...')
        with Path(path_to_corpus_file).open() as f:
            print('Collecting of letters\' probabilities...')
            n_chars = self.start * self.ngram
            for char in f.read():
                self.lm[n_chars][char] += 1
                n_chars = n_chars[1:] + char
        self.lm = {hist: self._normalize(chars) for hist, chars in self.lm.items()}

        return self

    @staticmethod
    def _normalize(counter):
        total = float(sum(counter.values()))
        return [(c, cnt / total) for c, cnt in counter.items()]

    def _generate_letter(self, history):
        history = history[-self.ngram:]
        dist = self.lm[history]
        x = random()
        for c, v in dist:
            x = x - v
            if x <= 0:
                return c

    def generate_text(self, n_letters=1000):
        print('Generating of an example of text...')
        history = self.start * self.ngram
        out = []
        for i in range(n_letters):
            c = self._generate_letter(history)
            history = history[-self.ngram:] + c
            out.append(c)
        return "".join(out)


if __name__ == '__main__':
    fname = 'resources/corpus/Dostoevsky.txt'
    model = CharLevelLanguageModel(ngram=15)
    model.train(fname)
    print(model.generate_text())
