# -*- coding: utf-8 -*-
import pymorphy2, re

from functools import reduce
from gensim.models.keyedvectors import KeyedVectors
from nltk.stem import SnowballStemmer


class CognateWordChecker(object):

    def __init__(self, word2vec_path, lang="russian"):
        self.morphological_analyser = pymorphy2.MorphAnalyzer()
        self.stemmer = SnowballStemmer(language=lang)
        self.prefixes = re.compile(r"^(по|под|пр[еио]|пере|на|чрез|ис|из|вне|бе[зс]|за|от|воз)")
        self.suffixes = re.compile(r"([иоы]й|ец|н[иь]е|ция|ть|с[ья]|[еиоё]к|ище|ни(к|ца)|тель)$")

        self.w2v = self._load_word2vec(word2vec_path)

        self.changed_consonants = [
            {'г', 'ж', 'з'},
            {'к', 'ч'},
            {'х', 'ш'},
            {'д', 'ж'},
            {'т', 'ч', 'щ'},
            {'т', 'д', 'с'},
            {'с', 'щ'}
        ]

        self.changed_vowels = [
            {'о', 'е', 'и'},
            {'о', 'у', 'ы'},
            {'о', 'е'},
            {'о', 'а'},
            {'о', 'ы'},
            {'и', 'ы'},
            {'е', 'и'}
        ]

        self.consonants_before_l = 'бпвфм'

    def _load_word2vec(self, path, limit=500000):
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

    def _is_vowel(self, symbol):
        return symbol in 'аеиоуыэя'

    def _is_changed_consonants(self, symbol1, symbol2):
        for changed_consinants_set in self.changed_consonants:
            if symbol1 in changed_consinants_set and symbol2 in changed_consinants_set:
                return True
        return False

    def improve_substring(self, substring, word1, word2):
        start1, end1 = word1.find(substring), word1.find(substring) + len(substring)
        start2, end2 = word2.find(substring), word1.find(substring) + len(substring)

        if end1 < len(word1) and end2 < len(word2):
            if self._is_changed_consonants(word1[end1], word2[end2]):
                substring += word1[end1]

        if substring[-1] in self.consonants_before_l and \
                end1 + 1 < len(word1) and word1[end1 + 1] == 'л' and \
                end2 + 1 < len(word2) and word2[end2 + 1] == 'л':
            substring += word1[end2 + 1]

        return substring

    def _get_lemma(self, word):
        return self.morphological_analyser.normal_forms(word)[0]

    def _get_word_canonical_form(self, word):
        stemmed_word = word

        while self.prefixes.search(stemmed_word) and not len(stemmed_word) <= 5:
            stemmed_word = self.prefixes.sub("", stemmed_word)

        while self.suffixes.search(stemmed_word) and not len(stemmed_word) <= 5:
            stemmed_word = self.suffixes.sub("", stemmed_word)

        hard_sign_index = stemmed_word.find('ъ')
        stemmed_word = stemmed_word[(hard_sign_index + 1):]

        if stemmed_word[-1] == 'н' and not self._is_vowel(stemmed_word[-2]):
            return stemmed_word[:-1]

        return stemmed_word

    def _is_complex(self, word, root):
        ind = word.find(root)
        return word[ind - 1] in "ое" if ind > 0 else word[ind + 1] in "ое" if ind < len(word) else False

    def _find_lcs(self, a, b):
        answer, match = "", ""
        l1, l2 = len(a), len(b)
        for i in range(l1):
            for j in range(l2):
                if (i + j < l1 and a[i + j] == b[j]):
                    match += b[j]
                else:
                    if (len(match) > len(answer)): answer = match
                    match = ""
        return answer

    def has_words_same_root(self, w1, w2):
        lemmas = [self._get_lemma(w) for w in (w1, w2)]

        if len(set(lemmas)) < 2:
            return "У вас было введено одно и тоже слово!"

        if self.w2v.similarity(lemmas[0], lemmas[-1]) < 0.45:
            return "Слова с омонимичным корнем не могут является однокоренными..."

        normalized_words = [self._get_word_canonical_form(w) for w in lemmas]
        lcs = reduce(self._find_lcs, normalized_words)

        if len(lcs) <= 2:
            lcs = self.improve_substring(lcs, normalized_words[0], normalized_words[-1])

        if any(len(lcs) <= len(w) * 0.5 for w in normalized_words):
            if self._is_complex(w1, lcs) or self._is_complex(w2, lcs):
                return "О, кажется, обнаружено сложное слово с корнем из другого слова!"
            return "Ваши слова не является однокоренными..."
        else:
            return "Ура! Все слова происходят от одного корня!"


if __name__ == "__main__":
    rch = CognateWordChecker(
        "/resources/all.norm-sz100-w10-cb0-it1-min100.w2v"
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

    # todo improve algorithm for these tests
    # assert rch.has_words_same_root("дерево", "древесина") == "Ура! Все слова происходят от одного корня!"
    # assert rch.has_words_same_root("сбор", "собирать") == "Ура! Все слова происходят от одного корня!"
    # assert rch.has_words_same_root("сохнуть", "сухо") == "Ура! Все слова происходят от одного корня!"
