import pickle
import string

from collections import Counter
from nltk import word_tokenize, sent_tokenize


class WordDictBuilder:
    def __init__(self):
        self.stop_words = string.punctuation + '«»→↑—✰⛭№•/\\'
        self.word_dict = None

    def build_dict(self, file_collection):
        self.word_dict = Counter()
        for filename in file_collection:
            with open(filename, 'r', encoding='utf-8') as f:
                self.collect_dictionary(f.read())

    def save_dictionary(self, filename):
        with open(filename, 'wb') as f:
            pickle.dump(self.word_dict, f)

    def load_dictionary(self, filename):
        with open(filename, 'rb') as f:
            self.word_dict = pickle.load(f)
        return self.word_dict

    def collect_dictionary(self, text):
        counter = Counter(
            [word.lower() for sent in sent_tokenize(text)
             for word in word_tokenize(sent) if not (word in self.stop_words or word.isdecimal() or not word.isalpha())]
        )
        self.word_dict += counter

    def normalize_frequencies(self, alpha=1.0):
        n = sum(self.word_dict.values())
        return {word: float((freq + alpha) / (n + alpha * n)) for word, freq in self.word_dict.items()}


class WordDecompounder:
    def __init__(self, path_to_dictionary):
        word_dict_builder = WordDictBuilder()
        self.dictionary = word_dict_builder.load_dictionary(path_to_dictionary)
        self.total = sum(self.dictionary.values())
        self.max_word_length = max(map(len, self.dictionary))

    def split(self, text):
        return self._viterbi_segment(text)

    def _word_probability(self, word):
        prob = self.dictionary[word]
        total = self.total if not 0 <= prob <= 1 else 1
        return prob / total

    def _viterbi_segment(self, text):
        probs, lasts = [1.0], [0]
        for i in range(1, len(text) + 1):
            prob_pos, pos = max((probs[j] * self._word_probability(text[j:i]), j)
                                for j in range(max(0, i - self.max_word_length), i))
            probs.append(prob_pos)
            lasts.append(pos)
        words = []
        i = len(text)
        while i > 0:
            words.append(text[lasts[i]:i])
            i = lasts[i]
        words.reverse()
        return words, probs[-1]


if __name__ == "__main__":
    fnames = [
        'resources/corpus/a.txt', 'resources/corpus/b.txt', 'resources/corpus/c.txt'  # and more files
    ]

    print('Collecting of a dictionary..')
    wdb = WordDictBuilder()
    wdb.build_dict(fnames)

    normalized_dict = wdb.normalize_frequencies()
    for k, v in sorted(normalized_dict.items(), key=lambda x: -x[1]):
        print(k, '--', v)

    PATH_TO_DICTIONARY = 'resources/corpus/dictionary.pkl'
    wdb.save_dictionary(PATH_TO_DICTIONARY)

    print()
    print('Decompounding of a text into words..')
    decompounder = WordDecompounder(PATH_TO_DICTIONARY)
    print(decompounder.split('малышикарлсонкоторыйживётнакрыше'))
    print(decompounder.split('зубзолотой'))
    print(decompounder.split('огнибольшогогорода'))
    print(decompounder.split('сказкаонильсеидикихгусях'))
