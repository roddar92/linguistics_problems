from collections import defaultdict
from math import pi
from nltk import sent_tokenize, word_tokenize
from pathlib import Path
from random import choice
from string import punctuation
from tqdm import tqdm


class PIDayLanguageModel:
    def __init__(self):
        self.lm = defaultdict(list)
        self.str_pi = str(pi)[2:]

    def train(self, path_to_corpus_file):
        print('Get data from the file...')
        path_to_corpus = Path(path_to_corpus_file).open()

        print('Collecting of language model...')
        for sent in tqdm(sent_tokenize(path_to_corpus.read())):
            prev = ''
            for i, word in enumerate(word_tokenize(sent)):
                word = word.lower()
                if prev == '.':
                    self.lm[''] += [word]
                self.lm[prev] += [word]
                prev = word
        path_to_corpus.close()

        return self

    def tokens_stream(self, word='', n_words=5):
        def generate_word(prev_word, l):
            subseq = [t for t in self.lm[prev_word] if len(t) == l]
            if not subseq:
                subseq = [t for t in self.lm[''] if len(t) == l]
            res_word = choice(subseq)
            return res_word

        print('Generating of an example of PI text...')
        prev_word = None
        if not word:
            w = choice([t for t in self.lm[''] if len(t) == 3])
            if w:
                yield w.capitalize(); prev_word = w.capitalize()

        for _, digit in zip(range(n_words), self.str_pi):
            d = int(digit)
            w = generate_word(prev_word, d)
            while w in punctuation or w in '... -- \'\' `` `'.split():
                yield w; prev_word = w
                w = generate_word(prev_word, d)
            t = w.capitalize() if prev_word == '.' or prev_word == '...' else w
            yield t; prev_word = t

    def generate_text(self, word='', n_words=5):
        return " ".join(self.tokens_stream(word=word, n_words=n_words))


if __name__ == '__main__':
    fname = "resources/corpus/Dostoevsky.txt"
    model = PIDayLanguageModel()
    model.train(fname)
    print(model.generate_text(n_words=15))
