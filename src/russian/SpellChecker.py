"""
    Simple spell-checker
    https://www.kaggle.com/c/csc-iinlp-2017-please-feax-me/
"""
import codecs
import csv
import time
from collections import Counter, defaultdict
from pyxdameraulevenshtein import damerau_levenshtein_distance
from functools import lru_cache

import nltk
from nltk.corpus import stopwords
import numpy as np
import pandas as pd
import pymorphy2
import re
from sklearn.feature_extraction.text import CountVectorizer
import string

nltk.download('stopwords')
all_stopwords = stopwords.words('russian') + stopwords.words('english')


class WordDict:
    _END = '__end__'

    def __init__(self):
        self.root = {}

    def __contains__(self, item):
        node = self.root
        for letter in item:
            letter = letter.lower()
            if letter not in node.keys():
                return False

            node = node[letter]
        else:
            return self._END in node

    def __add_item(self, word):
        node = self.root
        for letter in word:
            letter = letter.lower()
            node = node.setdefault(letter, {})
        node[self._END] = self._END
            
    def collect(self, words):
        for word in words:
            self.__add_item(word)
        return self


class StatisticalSpeller(object):
    """
        Поиск слов, наиболее близких по числу общих n-грамм и
        последующее ранжирование по эвристике-близости
    """

    __pron_set = ['то', 'та', 'те', 'так', 'это', 'эта', 'эти',
                  'той', 'тем', 'там', 'том', 'тех',
                  'этих', 'этой', 'этом', 'согласно']

    @staticmethod
    def tokenize(text):
        return ['^'] + [t for t in text.split()] + ['$']

    def __init__(self, n_candidates_search=150):
        """
        :param n_candidates_search: число кандидатов-строк при поиске
        """
        self.n_candidates = n_candidates_search
        self.morph = pymorphy2.MorphAnalyzer()

        # векторайзеры для нграмного индекса и частотного словаря
        self.vectorizer = CountVectorizer(analyzer="char_wb", ngram_range=(2, 3), binary=True)
        self.voc_vectorizer = CountVectorizer(tokenizer=self.tokenize, ngram_range=(2, 2))

        # нграмный индекс + частотный словарь биграм по корпусу текстов
        self.index = defaultdict(set)
        self.voc = defaultdict(int)
        self.words_list = None

        # регэкспы для битых предлогов
        self.on_prep = re.compile(r'\b(н{2,}а|на{2,})\b')
        self.year = re.compile(r'^[12]\d{3}')

    def fit(self, words_list):
        """
            Подгонка спеллера
        """

        checkpoint = time.time()
        self.words_list = words_list

        encoded_words = self.vectorizer.fit_transform(words_list).tocoo()

        # строим словарь, отображающий идентификатор нграммы в множество термов
        for ind in zip(encoded_words.row, encoded_words.col):
            self.index[ind[1]].add(ind[0])

        print("Speller fitted in", time.time() - checkpoint)

        return self

    def fit_texts(self, texts):
        checkpoint = time.time()
        words_vocab = self.voc_vectorizer.fit_transform(texts).tocoo()
        self.voc = dict(zip(
            sorted(self.voc_vectorizer.vocabulary_.values()),
            words_vocab.sum(axis=0).A1))

        print("Speller fitted for texts in", time.time() - checkpoint)

    @lru_cache(maxsize=1000000)
    def rectify(self, word, prev_word):
        """
            Предсказания спеллера
        """

        if word == ',,':
            return ','
        if word == '..':
            return '...'

        # запрос, преобразованный в нграммы
        char_ngrams_list = self.vectorizer.transform([word]).tocoo().col

        # подбираем число кандидатов по длине запроса
        self.n_candidates = 350 if len(word) <= 4 else 250 if len(word) <= 7 else self.n_candidates

        # для каждого терма считаем совпадение по нграммам
        counter = Counter()

        for token_id in char_ngrams_list:
            for word_id in self.index[token_id]:
                counter[word_id] += 1

        # среди топа по совпадениям по нграммам ищем "хорошее" исправление

        # используем модифицированное расстояние Левенштейна (с перестановками)
        # а также ищем слово с минимальным количеством новых букв
        suggests = list()
        for suggest in counter.most_common(n=self.n_candidates):
            sugg = self.words_list[suggest[0]]
            dist = damerau_levenshtein_distance(sugg, word)
            context_list = self.voc_vectorizer.transform([f"{prev_word} {sugg}"]).tocoo().col.tolist()
            if dist <= 5:
                if context_list:
                    suggs = [(sugg, dist, self.voc.get(context, 0.0)) for context in context_list]
                else:
                    suggs = [(sugg, dist, 0.0)]
                suggests.extend(suggs)

        suggests = sorted(suggests, key=lambda tup: tup[1])

        minimal_distance = min([suggest[1] for suggest in suggests])
        candidates = sorted(
            [(suggest[0], suggest[2]) for suggest in suggests
             if suggest[1] == minimal_distance and set(suggest[0]) == set(word)],
            key=lambda tup: -tup[1])

        return candidates[0][0] if candidates and candidates[0][1] > 0 else suggests[0][0]

    # ищем тег среди разборов одного слова
    def __tag_in_parse(self, tag_name, word):
        return any(tag_name in parse.tag for parse in self.morph.parse(word))

    # строим эвристики для битых предлогов
    def need_fix_prep(self, word, prep):
        if prep == 'е':
            if self.__tag_in_parse('VERB', word) \
                    or word in ['только', 'более', 'менее', 'больше', 'меньше']:
                return 'не'
            else:
                return prep
        elif prep == 'аа':
            return 'а'
        elif prep == 'даа' or prep == 'дда':
            return 'да'
        elif prep == 'ии':
            return 'и'
        elif prep == 'илли' or prep == 'иили':
            return 'или'
        elif prep == 'отт':
            return 'от'
        elif prep == 'ри':
            return 'при'
        elif prep in ['ыб', 'бл']:
            return 'был'
        elif prep in ['ым', 'ыт', 'ыв']:
            return prep[::-1]
        elif prep in ['зи', 'ов', 'од', 'ан', 'оп', 'ми', 'хи', 'ен']:
            if not self.__tag_in_parse('PREP', word):
                return prep[::-1]
            else:
                return prep
        elif prep == 'аз':
            if self.__tag_in_parse('accs', word):
                return prep[::-1]
            elif 'VERB' in self.morph.parse(word)[0].tag:
                return 'раз'
            else:
                return prep
        elif prep == 'в':
            if word == 'время':
                return 'во'
            else:
                return prep
        elif prep == 'д':
            if word not in string.punctuation \
                    and word not in '.. ... ,,'.split():
                return 'до'
            else:
                return prep
        elif prep == 'з':
            if len(word) > 1:
                if self.__tag_in_parse('gent', word):
                    return 'из'
                elif self.__tag_in_parse('accs', word) \
                        or self.__tag_in_parse('ablt', word):
                    return 'за'
                else:
                    return prep
            else:
                return prep
        elif prep == 'н':
            if len(word) > 1:
                if self.__tag_in_parse('accs', word) \
                        or self.__tag_in_parse('loct', word) \
                        or self.__tag_in_parse('loc2', word):
                    return 'на'
                elif 'VERB' in self.morph.parse(word)[0].tag:
                    return 'он'
                else:
                    return prep
            else:
                return prep
        elif prep == 'п':
            if self.__tag_in_parse('datv', word) \
                    or self.__tag_in_parse('loct', word) \
                    or self.__tag_in_parse('loc2', word) or word.isdigit():
                return 'по'
            else:
                return prep
        elif prep == 'т':
            if len(word) > 1:
                if self.__tag_in_parse('gent', word):
                    return 'от'
                elif self.__tag_in_parse('ablt', word) or word in ['же', 'есть']:
                    return 'то'
                elif self.__tag_in_parse('femn', word):
                    return 'та'
                else:
                    return prep
            else:
                return prep
        elif prep == 'х':
            if word not in string.punctuation and not word.isdigit():
                return 'их'
            else:
                return prep
        elif prep == 'чо':
            return 'что'
        elif prep == 'о':
            if word == 'время':
                return 'во'
            else:
                return prep
        elif prep == 'ноо':
            if not word.isalpha():
                return 'но'
            else:
                return prep
        elif prep == 'кк':
            if 'datv' in self.morph.parse(word)[0].tag:
                return 'к'
            elif word not in string.punctuation:
                return 'как'
            else:
                return prep
        elif prep == 'оо':
            if self.__tag_in_parse('loct', word):
                return 'о'
            else:
                return prep
        elif prep == 'сс':
            if self.__tag_in_parse('gent', word) \
                    or self.__tag_in_parse('ablt', word) \
                    or self.year.search(word):
                return 'с'
            else:
                return prep
        elif self.on_prep.search(prep):
            if self.__tag_in_parse('accs', word) \
                    or self.__tag_in_parse('loct', word) \
                    or self.__tag_in_parse('loc2', word) \
                    or word.isdigit():
                return 'на'
            else:
                return prep
        elif prep == 'пр':
            if self.__tag_in_parse('loct', word):
                return 'при'
            elif self.__tag_in_parse('accs', word):
                return 'про'
            else:
                return prep
        elif prep == 'эо':
            return 'это'
        elif prep == 'эт':
            if self.__tag_in_parse('femn', word):
                if self.__tag_in_parse('accs', word):
                    return 'эту'
                elif self.__tag_in_parse('gent', word) \
                        or self.__tag_in_parse('datv', word):
                    return 'этой'
                else:
                    return 'эта'
            elif self.__tag_in_parse('masc', word) \
                    and not self.__tag_in_parse('ablt', word):
                return 'этот'
            else:
                return 'это'
        else:
            return prep

    def need_fix_prep_after_words(self, word, prep, next_word, ind):
        if prep == 'вв':
            if ind == 0 or (ind - 1 >= 0 and 'ivx' not in word):
                return 'в'
            elif next_word == 'время':
                return 'во'
            else:
                return prep
        elif prep == 'тс' and ind - 1 >= 0 and word.isdigit():
            return 'тыс'
        elif prep == 'мк' and word.isdigit():
            return prep[::-1]
        elif prep == 'е':
            if word in self.__pron_set:
                return 'же'
            elif self.__tag_in_parse('Name', word):
                return 'де'
            elif next_word != '' and next_word not in string.punctuation:
                return 'ее'
            else:
                return prep
        elif prep == 'ж':
            if word in self.__pron_set:
                return 'же'
            else:
                return prep
        elif prep == 'ил':
            if self.__tag_in_parse('VERB', word):
                return 'ли'
            else:
                return 'или'
        else:
            return prep


if __name__ == "__main__":

    np.random.seed(0)

    # зачитываем словарь "правильных слов"
    words_set = set(line.strip() for line in codecs.open("../resources/words_dict.txt", "r", encoding="utf-8"))
    
    words_dict = WordDict()
    words_dict.collect(words_set)

    # создаём спеллер
    speller = StatisticalSpeller()
    speller.fit(sorted(list(words_set)))

    # читаем выборку из правильных текстов
    df = pd.read_csv("../resources/corrected_texts.csv")

    speller.fit_texts(list(df["text"]))

    # читаем выборку
    df = pd.read_csv("../resources/broken_texts.csv")

    checkpoint1 = time.time()
    total_rectification_time = 0.0
    total_sentences_rectifications = 0.0

    y_submission = []
    counts = 0

    # исправляем, попутно собирая счётчики и засекая время
    for i in range(df.shape[0]):

        counts += 1

        if counts % 100 == 0:
            print("Rows processed", counts)

        start = time.time()
        mispelled_text = df["text"][i]
        mispelled_tokens = mispelled_text.split()

        was_rectified = False

        # для каждого слова из текста поступаем следующим образом:
        # если слово отсутствует в словаре, то подбираем ему наилучшее исправление
        # далее при наличие слева стопслова с опечаткой пытаемся его исправить с помощью простых эвристик
        for j, mispelled_token in enumerate(mispelled_tokens):
            if mispelled_token not in all_stopwords and mispelled_token not in words_dict:
                prev_token = mispelled_tokens[j - 1] if j > 0 else '^'
                rectified_token = speller.rectify(mispelled_token, prev_token)
                mispelled_tokens[j] = rectified_token
                if j - 1 >= 0:
                    mispelled_tokens[j - 1] = speller.need_fix_prep(rectified_token, mispelled_tokens[j - 1])
                was_rectified = True
            elif mispelled_token in words_dict:
                mispelled_tokens[j - 1] = speller.need_fix_prep(mispelled_token, mispelled_tokens[j - 1])
                nw = mispelled_tokens[j + 1] if j + 1 < len(mispelled_tokens) else ''
                mispelled_tokens[j] = speller.need_fix_prep_after_words(mispelled_tokens[j - 1],
                                                                        mispelled_token, nw, j)
                was_rectified = True

        if was_rectified:
            mispelled_text = " ".join(mispelled_tokens)
            total_rectification_time += time.time() - start
            total_sentences_rectifications += 1.0

        y_submission.append(mispelled_text)

    checkpoint2 = time.time()

    print("elapsed", checkpoint2 - checkpoint1)
    print("average speller time", total_rectification_time / float(total_sentences_rectifications))

    submission = pd.DataFrame({"id": df["id"], "text": y_submission}, columns=["id", "text"])
    submission.to_csv("baseline_submission.csv", index=None, encoding="utf-8", quotechar='"',
                      quoting=csv.QUOTE_NONNUMERIC)
