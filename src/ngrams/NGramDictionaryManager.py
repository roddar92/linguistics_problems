# -*- coding: utf-8 -*-
from collections import defaultdict
import os
import re


class NGramDictionaryManager(object):
    def __init__(self):
        self.ngram_dictionary = defaultdict(int)

    def create_dictionary(self, input_path, n_gram_length = 2):

        def get_ngrams(word, ngram_len):
            n_grams = list()
            for i in range(len(word) - ngram_len + 1):
                n_grams.append(word[i:i + ngram_len])
            return n_grams

        with open(input_path, 'r', encoding='utf-8') as f:
            for line in f:

                # TODO tokenization with NLTK RegexpTokenizer(r'[\.,:;!\?_\-\+=/\"&\*\(\)\^\[\]\{\}\<\>\|\d%$@#№]')
                line = line.strip()
                line = re.sub(r'[\.,:;!\?_\-\+=/\"&\*\(\)\^\[\]\{\}\<\>\|\d%$@#№]', '', line)
                line = re.sub(r'\b(a|across|am|an|and|as|by|but|in|it|no|not|yes|this|that|the|to|what|under|'
                              r'а|в|к|и|но|да|нет|не|ни|это|что|то|за|по|про|под|над)\b', '', line)
                tokens = line.split()

                for token in tokens:
                    if '\'' in token:
                        token = token.replace('\'', "")
                    token = token.lower()
                    if len(token) >= n_gram_length:
                        ngrams = get_ngrams(token, n_gram_length)
                        for ngram in ngrams:
                            self.ngram_dictionary[ngram] += 1

    def save_dictionary_to_file(self, output_path):
        with open(output_path, "w", encoding='utf-8') as f:
            for (k, v) in sorted(self.ngram_dictionary.items(), key=lambda x: -x[1]):
                f.write("{} - {}".format(k, v))
            f.flush()
            f.close()

    def print_dictionary(self, limit=10):
        i = 0
        for (k, v) in sorted(self.ngram_dictionary.items(), key=lambda x: -x[1]):
            if i < limit:
                print("{} - {}".format(k, v))
                i += 1
            else:
                break


if __name__ == "__main__":
    path = "resources"
    ngram_length = 2

    ngram_dict_manager = NGramDictionaryManager()
    for descriptor in os.listdir(path):
        ngram_dict_manager.create_dictionary(os.path.join(path, descriptor), 2)
    ngram_dict_manager.print_dictionary()
