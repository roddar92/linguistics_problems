import os
import pickle
import string

from collections import Counter
from math import log
from nltk import word_tokenize, sent_tokenize


class WordDictBuilder:
    def __init__(self):
        self.stop_words = string.punctuation + '«»→↑—✰⛭№•/\\'
        self.word_dict = None

    def build_dict(self, collection):
        self.word_dict = Counter()
        for f in os.listdir(collection):
            if f.endswith('.txt'):
                self.collect_dictionary(open(os.path.join(collection, f), 'r', encoding='utf-8').read())

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

    # Find the most probable sequence of words with Viterbi algorithm
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


class WordDecompounderWithoutPrioriProb:
    # Build a cost dictionary, assuming Zipf's law and cost = -math.log(probability).
    def __init__(self, path_to_dictionary):
        self.words = list(pickle.load(open(path_to_dictionary, 'rb')).keys())
        total = len(self.words)
        self.wordcost = dict((w, log((i + 1) * log(total))) for i, w in enumerate(self.words))
        self.maxword = max(map(len, self.words))

    def split(self, text):
        # Find the best match for the i first characters, assuming cost has
        # been built for the i-1 first characters.
        # Returns a pair (match_cost, match_length).
        def best_match(pos):
            candidates = enumerate(reversed(costs[max(0, pos - self.maxword):pos]))
            return min((c + self.wordcost.get(text[pos - k - 1:pos], 9e999), k + 1) for k, c in candidates)

        # Build the cost array.
        costs, lengths = [0], [0]
        for i in range(1, len(text) + 1):
            cost, length = best_match(i)
            costs.append(cost)
            lengths.append(length)

        # Backtrack to recover the minimal-cost string.
        out = []
        i = len(text)
        while i > 0:
            out.append(text[i - lengths[i]:i])
            i -= lengths[i]

        return " ".join(reversed(out))


if __name__ == "__main__":
    path_to_collection = 'resources/corpus'

    print('Collecting of a dictionary..')
    wdb = WordDictBuilder()
    wdb.build_dict(path_to_collection)

    normalized_dict = wdb.normalize_frequencies()
    print(len(normalized_dict))
    for key, val in sorted(normalized_dict.items(), key=lambda x: -x[1]):
        print(key, '--', val)

    PATH_TO_DICTIONARY = 'resources/corpus/dictionary.pkl'
    wdb.save_dictionary(PATH_TO_DICTIONARY)

    print()
    print('Decompounding of a text into words..')
    decompounder = WordDecompounder(PATH_TO_DICTIONARY)
    print(decompounder.split('малышикарлсонкоторыйживётнакрыше'))
    print(decompounder.split('зубзолотой'))
    print(decompounder.split('огнибольшогогорода'))
    print(decompounder.split('сказкаонильсеидикихгусях'))
    print(decompounder.split('царьпетр'))

    print()
    print('Decompounding of a text into words ..')
    decompounder = WordDecompounderWithoutPrioriProb(PATH_TO_DICTIONARY)
    print(decompounder.split('малышикарлсонкоторыйживётнакрыше'))
    print(decompounder.split('зубзолотой'))
    print(decompounder.split('огнибольшогогорода'))
    print(decompounder.split('сказкаонильсеидикихгусях'))
    print(decompounder.split('царьпетр'))
