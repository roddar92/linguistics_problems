from collections import defaultdict
from math import pi
from nltk import sent_tokenize, word_tokenize
from pathlib import Path
from random import choice
from string import punctuation
from tqdm import tqdm


class PIDayLanguageModel:
    DOT = '.'
    EMPTY_STRING = ''
    START_LENGTH = 3

    def __init__(self):
        self.lm = defaultdict(list)
        self.str_pi = str(pi)[2:]

    def train(self, path_to_corpus_file):
        print('Get data from the file...')
        path_to_corpus = Path(path_to_corpus_file).open()

        print('Collecting of language model...')
        for sent in tqdm(sent_tokenize(path_to_corpus.read())):
            prev = self.EMPTY_STRING
            for i, word in enumerate(word_tokenize(sent)):
                word = word.lower()
                if prev == self.DOT:
                    self.lm[self.EMPTY_STRING].append(word)
                self.lm[prev].append(word)
                prev = word
        path_to_corpus.close()

        return self

    def __tokens_stream(self, word=EMPTY_STRING, n_words=5):
        def generate_word(pword, l):
            sub_seq = [t for t in self.lm[pword] if len(t) == l]
            if not sub_seq:
                sub_seq = [t for t in self.lm[self.EMPTY_STRING] if len(t) == l]
            return choice(sub_seq)

        print('Generating of an example of PI text...')
        prev_word = None
        if not word:
            w = choice([t for t in self.lm[self.EMPTY_STRING] if len(t) == self.START_LENGTH])
            if w:
                yield w.capitalize()
                prev_word = w.capitalize()

        for _, digit in zip(range(n_words), self.str_pi):
            d = int(digit)
            w = generate_word(prev_word, d)
            while w in punctuation or w in '... -- \'\' `` `'.split():
                yield w
                prev_word = w
                w = generate_word(prev_word, d)
            t = w.capitalize() if prev_word in (self.DOT, '...') else w
            yield t
            prev_word = t

    def generate_text(self, word=EMPTY_STRING, n_words=5):
        return " ".join(self.__tokens_stream(word=word, n_words=n_words))


if __name__ == '__main__':
    fname = "resources/corpus/Dostoevsky.txt"
    model = PIDayLanguageModel()
    model.train(fname)
    print(model.generate_text(n_words=15))
