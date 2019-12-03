# -*- coding: utf-8 -*-
import os
import re
import string
from collections import Counter, deque

from nltk.corpus import stopwords


class NGramDictionaryManager:
    def __init__(self):
        self.stop_words = set(stopwords.words('english') + stopwords.words('russian'))
        self.ngram_dictionary = Counter()

    def clear_dictionary(self):
        self.ngram_dictionary.clear()

    def text_preprocessing(self, line, remove_stop_words):
        line = line.strip()
        line = re.sub(r'[\r\t\n' + string.punctuation + r']', ' ', line)
        tokens = [token.lower() for token in line.split()]
        if remove_stop_words:
            tokens = filter(lambda t: t not in self.stop_words, tokens)
        return tokens

    # TODO override this method for information retrieval with spell-checker
    def create_dictionary_for_spelling(self, input_path, n_gram_length=2, remove_stop_words=False):
        def get_ngrams(word, ngram_len):
            return (
                word[i:i + ngram_len] for i in range(len(word) - ngram_len + 1)
            )

        with open(input_path, 'r', encoding='utf-8') as f:
            for line in f:
                for token in self.text_preprocessing(line, remove_stop_words):
                    if '\'' in token:
                        token = re.sub(r'\'', '', token)
                    if len(token) >= n_gram_length:
                        for ngram in get_ngrams(token.lower(), n_gram_length):
                            self.ngram_dictionary[ngram] += 1

    def create_dictionary_for_translation(self, input_path, n_gram_length=2, remove_stop_words=False):
        with open(input_path, 'r', encoding='utf-8') as f:
            tokens = self.text_preprocessing(f.read(), remove_stop_words)

            n_gram = deque()
            for k in range(n_gram_length - 1):
                n_gram.append(next(tokens))

            try:
                while True:
                    n_gram.append(next(tokens))
                    self.ngram_dictionary[' '.join(n_gram)] += 1
                    n_gram.popleft()
            except StopIteration:
                self.ngram_dictionary[' '.join(n_gram)] += 1

    def save_dictionary_to_file(self, output_path):
        with open(output_path, "w", encoding='utf-8') as f:
            for (k, v) in self.ngram_dictionary.most_common():
                f.write("{}\t{}".format(k, v))
            f.flush()
            f.close()

    def print_dictionary(self, limit=10):
        for k, v in self.ngram_dictionary.most_common(limit):
            print("{}\t{}".format(k, v))


if __name__ == "__main__":
    path = "resources"

    for descriptor in os.listdir(path):
        ngram_dict_manager = NGramDictionaryManager()

        if descriptor.endswith('.txt'):
            path_desc = os.path.join(path, descriptor)
            print(path_desc)
            print('Spelling N-grams')
            ngram_dict_manager.create_dictionary_for_spelling(path_desc, 2, remove_stop_words=True)
            ngram_dict_manager.print_dictionary()

            print()
            ngram_dict_manager.clear_dictionary()

            print('Translation N-grams')
            ngram_dict_manager.create_dictionary_for_translation(path_desc, 2, remove_stop_words=True)
            ngram_dict_manager.print_dictionary()
            print('\n')
