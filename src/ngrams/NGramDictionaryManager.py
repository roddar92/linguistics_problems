# -*- coding: utf-8 -*-
import os
import re
from collections import defaultdict, deque

from nltk.corpus import stopwords


class NGramDictionaryManager(object):
    def __init__(self):
        self.stop_words = set(stopwords.words('english') + stopwords.words('russian'))
        self.ngram_dictionary = defaultdict(int)

    def clear_dictionary(self):
        self.ngram_dictionary.clear()

    def text_preprocessing(self, line, remove_stop_words):
        line = line.strip()
        line = re.sub(r'[\r\t\n\.,:;!\'\"\?_\-\+=/&\*\(\)\^\[\]\{\}\<\>\|]', u'', line)
        tokens = [token.lower() for token in line.split()]
        if remove_stop_words:
            tokens = [token for token in tokens if token not in self.stop_words]
        return tokens

    # TODO override this method for information retrieval with spell-checker
    def create_dictionary_for_spelling(self, input_path, n_gram_length=2, remove_stop_words=False):
        def get_ngrams(word, ngram_len):
            n_grams = list()
            for i in range(len(word) - ngram_len + 1):
                n_grams.append(word[i:i + ngram_len])
            return n_grams

        with open(input_path, 'r', encoding='utf-8') as f:
            for line in f:
                tokens = self.text_preprocessing(line, remove_stop_words)

                for token in tokens:
                    if '\'' in token:
                        token = token.replace('\'', "")
                    token = token.lower()
                    if len(token) >= n_gram_length:
                        ngrams = get_ngrams(token, n_gram_length)
                        for ngram in ngrams:
                            self.ngram_dictionary[ngram] += 1

    def create_dictionary_for_translation(self, input_path, n_gram_length=2, remove_stop_words=False):
        with open(input_path, 'r', encoding='utf-8') as f:
            tokens = self.text_preprocessing(f.read(), remove_stop_words)

            n_gram = deque()
            i = 0
            for k in range(n_gram_length - 1):
                n_gram.append(tokens[i])
                i += 1

            while i < len(tokens):
                n_gram.append(tokens[i])
                self.ngram_dictionary[' '.join(n_gram)] += 1
                n_gram.popleft()
                i += 1

    def save_dictionary_to_file(self, output_path):
        with open(output_path, "w", encoding='utf-8') as f:
            for (k, v) in sorted(self.ngram_dictionary.items(), key=lambda x: -x[1]):
                f.write("{}\t{}".format(k, v))
            f.flush()
            f.close()

    def print_dictionary(self, limit=10):
        i = 0
        for (k, v) in sorted(self.ngram_dictionary.items(), key=lambda x: -x[1]):
            if i < limit:
                print("{}\t{}".format(k, v))
                i += 1
            else:
                break


if __name__ == "__main__":
    path = "resources"

    for descriptor in os.listdir(path):
        ngram_dict_manager = NGramDictionaryManager()

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
