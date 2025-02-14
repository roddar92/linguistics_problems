# -*- coding: utf-8 -*-
import pymorphy2
import re

from functools import reduce
from gensim.models.keyedvectors import KeyedVectors
from nltk.stem import SnowballStemmer


class CognateWordChecker(object):

    def __init__(self, word2vec_path, lang="russian"):
        self.morphological_analyser = pymorphy2.MorphAnalyzer()
        self.stemmer = SnowballStemmer(language=lang)
        self.__prefixes = re.compile(r"^(пере|чрез|еже)")
        self.__suffixes = re.compile(r"([иоы]й|ая|ец|н[иь]е|ция|(ос)?ть|с[ья]|ище|ист|ни(к|ца)|тель)$")

        self.w2v = self.__load_word2vec(word2vec_path)

        self.__changed_consonants = [
            {'г', 'ж', 'з'},
            {'к', 'ч'},
            {'х', 'ш'},
            {'д', 'ж'},
            {'т', 'ч', 'щ'},
            {'т', 'д', 'с'},
            {'с', 'щ'}
        ]

        self.__changed_vowels = [
            {'о', 'е', 'и'},
            {'о', 'у', 'ы'},
            {'о', 'е'},
            {'о', 'а'},
            {'о', 'ы'},
            {'и', 'ы'},
            {'е', 'и', 'й'},
            {'е', 'и'}
        ]

        self.hidden_vowels = 'ое'
        self.consonants_before_l = 'бпвфм'

    @staticmethod
    def __load_word2vec(path, limit=500000):
        """
        Init word2vec model
        :param path: path to the model
        :param limit: optional
        :return: word2vec model
        """
        print('Выгружаю семантическую модель слов...')
        w2v = KeyedVectors.load_word2vec_format(path, binary=True,
                                                unicode_errors='ignore', limit=limit)
        w2v.init_sims(replace=True)
        print('Выгрузка окончена')
        return w2v

    @staticmethod
    def __is_vowel(symbol):
        return symbol in 'аеиоуыэюя'

    def __is_changed_consonants(self, symbol1, symbol2):
        for changed_consinants_set in self.__changed_consonants:
            if symbol1 in changed_consinants_set and symbol2 in changed_consinants_set:
                return True
        return False

    def __is_changed_vowels(self, symbol1, symbol2):
        for changed_vowels_set in self.__changed_vowels:
            if symbol1 in changed_vowels_set and symbol2 in changed_vowels_set:
                return True
        return False

    def __find_hidden_vowels(self, a, b):
        w1, w2 = list(a), list(b)
        l1, l2 = len(a), len(b)
        for i in range(l1 - 2):
            for j in range(l2 - 2):
                if a[i] == b[j]:
                    if a[i + 2] == b[j + 1] and a[i + 1] in self.hidden_vowels:
                        w1[i + 1] = '*'
                        w2.insert(j + 1, '*')
                    elif a[i + 1] == b[j + 2] and b[j + 1] in self.hidden_vowels:
                        w1.insert(i + 1, '*')
                        w2[j + 1] = '*'
        return ''.join(w1), ''.join(w2)

    def __find_changed_vowels(self, a, b):
        w1, w2 = list(a), list(b)
        l1, l2 = len(a), len(b)
        for i in range(l1 - 2):
            for j in range(l2 - 2):
                if a[i] == b[j] and a[i + 2] == b[j + 2] and \
                        a[i + 1] != b[j + 1] and self.__is_changed_vowels(a[i + 1], b[j + 1]):
                    w1[i + 1] = '*'
                    w2[j + 1] = '*'
        return ''.join(w1), ''.join(w2)

    def __improve_substring(self, substring, word1, word2):
        start1, end1 = word1.find(substring), word1.find(substring) + len(substring)
        start2, end2 = word2.find(substring), word1.find(substring) + len(substring)

        if end1 < len(word1) and end2 < len(word2):
            if self.__is_changed_consonants(word1[end1], word2[end2]):
                substring += word1[end1]

        if substring[-1] in self.consonants_before_l and \
                end1 + 1 < len(word1) and word1[end1 + 1] == 'л' and \
                end2 + 1 < len(word2) and word2[end2 + 1] == 'л':
            substring += word1[end2 + 1]

        return substring

    def __get_lemma(self, word):
        return self.morphological_analyser.normal_forms(word)[0]

    def __get_word_canonical_form(self, word):
        stemmed_word = word

        while self.__prefixes.search(stemmed_word) and not len(stemmed_word) <= 5:
            stemmed_word = self.__prefixes.sub("", stemmed_word)
        while self.__suffixes.search(stemmed_word) and not len(stemmed_word) <= 5:
            stemmed_word = self.__suffixes.sub("", stemmed_word)

        if len(stemmed_word) > 5:
            stemmed_word = self.stemmer.stem(stemmed_word)

        hard_sign_index = stemmed_word.find('ъ')
        stemmed_word = stemmed_word[(hard_sign_index + 1):]

        if stemmed_word[-1] == 'н' and not self.__is_vowel(stemmed_word[-2]):
            return stemmed_word[:-1]

        return stemmed_word

    @staticmethod
    def __is_complex(word, root):
        ind = word.find(root)
        return word[ind - 1] in "ое" if ind > 0 else word[ind + 1] in "ое" if ind < len(word) else False

    @staticmethod
    def __find_lcs(a, b):
        m, n = 1 + len(a), 1 + len(b)
        prev, curr = [0] * n, [0]
        lcs, end = 0, 0
        for i in range(1, m):
            for j in range(1, n):
                curr.append(prev[j - 1] + 1 if a[i - 1] == b[j - 1] else 0)
                if curr[-1] > lcs:
                    lcs = curr[-1]
                    end = i
            prev = curr
            curr = [0]
        return a[end - lcs: end]

    def has_words_same_root(self, w1, w2):
        lemmas = list(map(self.__get_lemma, (w1, w2)))

        if len(set(lemmas)) < 2:
            return "У вас было введено одно и тоже слово!"

        if self.w2v and self.w2v.similarity(lemmas[0], lemmas[-1]) < 0.45:
            return "Слова с омонимичным корнем не могут является однокоренными..."

        normalized_words = list(map(self.__get_word_canonical_form, lemmas))
        corrected_normalized = self.__find_changed_vowels(normalized_words[0], normalized_words[-1])
        corrected_normalized = self.__find_hidden_vowels(corrected_normalized[0], corrected_normalized[-1])

        lcs = reduce(self.__find_lcs, corrected_normalized)

        if len(lcs) <= 2:
            lcs = self.__improve_substring(lcs, normalized_words[0], normalized_words[-1])

        if any(len(lcs) < len(w) * 0.5 for w in normalized_words):
            if self.__is_complex(w1, lcs) or self.__is_complex(w2, lcs):
                return "О, кажется, обнаружено сложное слово с корнем из другого слова!"
            return "Ваши слова не является однокоренными..."
        else:
            return "Ура! Все слова происходят от одного корня!"


if __name__ == "__main__":
    rch = CognateWordChecker(
        "../resources/all.norm-sz100-w10-cb0-it1-min100.w2v"
    )

    assert rch.has_words_same_root("дом", "домик") == "Ура! Все слова происходят от одного корня!"
    assert rch.has_words_same_root("домик", "домика") == "У вас было введено одно и тоже слово!"
    assert rch.has_words_same_root("земля", "землетрясение") == "О, кажется, обнаружено сложное слово " \
                                                                "с корнем из другого слова!"
    assert rch.has_words_same_root("опасный", "опасность") == "Ура! Все слова происходят от одного корня!"
    assert rch.has_words_same_root("дружить", "друг") == "Ура! Все слова происходят от одного корня!"
    assert rch.has_words_same_root("водить", "вождение") == "Ура! Все слова происходят от одного корня!"
    assert rch.has_words_same_root("сухой", "сушить") == "Ура! Все слова происходят от одного корня!"
    assert rch.has_words_same_root("покупка", "куплю") == "Ура! Все слова происходят от одного корня!"
    assert rch.has_words_same_root("красный", "прекрасный") == "Ура! Все слова происходят от одного корня!"
    assert rch.has_words_same_root("вода", "водить") == "Слова с омонимичным корнем " \
                                                        "не могут является однокоренными..."
    assert rch.has_words_same_root("сбор", "собирать") == "Ура! Все слова происходят от одного корня!"
    assert rch.has_words_same_root("сохнуть", "сухой") == "Ура! Все слова происходят от одного корня!"
    assert rch.has_words_same_root("война", "военный") == "Ура! Все слова происходят от одного корня!"
    assert rch.has_words_same_root("день", "ежедневный") == "Ура! Все слова происходят от одного корня!"
    assert rch.has_words_same_root("день", "дневник") == "Ура! Все слова происходят от одного корня!"
    assert rch.has_words_same_root("дерево", "древесина") == "Ура! Все слова происходят от одного корня!"
    assert rch.has_words_same_root("хор", "хоровой") == "Ура! Все слова происходят от одного корня!"
    assert rch.has_words_same_root("юность", "юный") == "Ура! Все слова происходят от одного корня!"
    assert rch.has_words_same_root("послезавтра", "завтрашний") == "Ура! Все слова происходят от одного корня!"

    # IT DOESN'T WORK DUE TO WORD2VEC SIMILARITY FUNCTION!
    # assert rch.has_words_same_root("сохнуть", "сухо") == "Ура! Все слова происходят от одного корня!"

    # todo improve algorithm for these tests
    # assert rch.has_words_same_root("жать", "отжимать") == "Ура! Все слова происходят от одного корня!"
    # assert rch.has_words_same_root("жать", "сжимать") == "Ура! Все слова происходят от одного корня!"
    # assert rch.has_words_same_root("жать", "сожму") == "Ура! Все слова происходят от одного корня!"
    # assert rch.has_words_same_root("кованый", "кую") == "Ура! Все слова происходят от одного корня!"
