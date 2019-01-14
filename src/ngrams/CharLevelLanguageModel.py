from collections import defaultdict, Counter
from pathlib import Path
from random import random


class CharLevelLanguageModel:
    def __init__(self):
        self.lm = defaultdict(Counter)
        self.start = '~'

    def train(self, path_to_corpus_file, ngram=7):
        print('Get data from the file...')
        path_to_corpus = Path(path_to_corpus_file).open()

        print('Collecting of letters\' probabilities...')
        n_chars = self.start * ngram
        for char in path_to_corpus.read():
            self.lm[n_chars][char] += 1
            n_chars = n_chars[1:] + char
        path_to_corpus.close()
        self.lm = {hist: self._normalize(chars) for hist, chars in self.lm.items()}

        return self

    @staticmethod
    def _normalize(counter):
        total = float(sum(counter.values()))
        return [(c, cnt / total) for c, cnt in counter.items()]

    def _generate_letter(self, history, ngram):
        history = history[-ngram:]
        dist = self.lm[history]
        x = random()
        for c, v in dist:
            x = x - v
            if x <= 0:
                return c

    def generate_text(self, ngram=7, n_letters=1000):
        print('Genrating of an example of text...')
        history = self.start * ngram
        out = []
        for i in range(n_letters):
            c = self._generate_letter(history, ngram)
            history = history[-ngram:] + c
            out.append(c)
        return "".join(out)


if __name__ == '__main__':
    fname = "resources/corpus/Dostoevsky.txt"
    model = CharLevelLanguageModel()
    model.train(fname, ngram=10)
    print(model.generate_text(ngram=10))
