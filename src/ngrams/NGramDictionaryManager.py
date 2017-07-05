# -*- coding: utf-8 -*-
from collections import defaultdict, deque
import io, os
import re


class NGramDictionaryManager(object):
    def __init__(self):
        self.ngram_dictionary = defaultdict(int)

    # TODO override this method for information retrieval with spell-checker
    def create_dictionary_for_spelling(self, input_path, n_gram_length = 2):

        def get_ngrams(word, ngram_len):
            n_grams = list()
            for i in range(len(word) - ngram_len + 1):
                n_grams.append(word[i:i + ngram_len])
            return n_grams

        with io.open(input_path, 'r', encoding='utf-8') as f:
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

    # TODO check method correctness
    def create_dictionary_for_translation(self, input_path, n_gram_length = 2):

        with io.open(input_path, 'r', encoding='utf-8') as f:

            # TODO tokenization with NLTK RegexpTokenizer(r'[\.,:;!\?_\-\+=/\"&\*\(\)\^\[\]\{\}\<\>\|\d%$@#№]')
            line = f.read().strip()
            line = re.sub(r'[\.,:;!\?_\-\+=/\"&\*\(\)\^\[\]\{\}\<\>\|]', u'', line)
            line = re.sub(r'\b(a|across|am|an|and|as|by|but|in|it|no|not|yes|this|that|the|to|what|under|'
                          r'а|в|к|и|но|да|нет|не|ни|это|что|то|за|по|про|под|над)\b', u'', line)
            tokens = line.split()
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
        with io.open(output_path, "w", encoding='utf-8') as f:
            for (k, v) in sorted(self.ngram_dictionary.items(), key=lambda x: -x[1]):
                f.write(u"{}\t{}".format(k, v).encode('utf-8'))
            f.flush()
            f.close()

    def print_dictionary(self, limit=10):
        i = 0
        for (k, v) in sorted(self.ngram_dictionary.items(), key=lambda x: -x[1]):
            if i < limit:
                print(u"{}\t{}".format(k, v).encode('utf-8'))
                i += 1
            else:
                break


if __name__ == "__main__":
    path = "resources"
    ngram_length = 2

    ngram_dict_manager = NGramDictionaryManager()

    print('Spelling N-grams\n')
    for descriptor in os.listdir(path):
        ngram_dict_manager.create_dictionary_for_spelling(os.path.join(path, descriptor), 2)
    ngram_dict_manager.print_dictionary()

    ngram_dict_manager = NGramDictionaryManager()

    print('Translation N-grams\n')
    for descriptor in os.listdir(path):
        ngram_dict_manager.create_dictionary_for_translation(os.path.join(path, descriptor), 2)
    ngram_dict_manager.print_dictionary()
