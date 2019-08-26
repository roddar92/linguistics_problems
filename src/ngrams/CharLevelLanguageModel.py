from collections import defaultdict, Counter
from pathlib import Path
from random import random


class CharLevelLanguageModel:
    def __init__(self, ngram=10):
        self.ngram = ngram
        self.__lm = defaultdict(Counter)
        self.__start = '~'

    def train(self, path_to_corpus_file):
        print('Get data from the file...')
        with Path(path_to_corpus_file).open() as f:
            print('Collecting of letters\' probabilities...')
            n_chars = self.__start * self.ngram
            for char in f.read():
                self.__lm[n_chars][char] += 1
                n_chars = n_chars[1:] + char
        self.__lm = {hist: self.__normalize(chars) for hist, chars in self.__lm.items()}

        return self

    @staticmethod
    def __normalize(counter):
        total = float(sum(counter.values()))
        return [(c, cnt / total) for c, cnt in counter.items()]

    def __generate_letter(self, history):
        history = history[-self.ngram:]
        dist = self.__lm[history]
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
            c = self.__generate_letter(history)
            history = history[-self.ngram:] + c
            out.append(c)
        return "".join(out)


if __name__ == '__main__':
    fname = 'resources/corpus/Dostoevsky.txt'
    model = CharLevelLanguageModel(ngram=15)
    model.train(fname)
    print(model.generate_text())
