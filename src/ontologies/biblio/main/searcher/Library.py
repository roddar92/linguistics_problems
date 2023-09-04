# -*- coding: utf-8 -*-
import io, json
import nltk
nltk.download('stopwords')

from nltk.corpus import stopwords

from RulesParser import RulesParser


class Book(object):
    def __init__(self, author, name, heros=None):
        if heros is None:
            heros = []
        self.author = author
        self.name = name
        self.heros = heros

    def __eq__(self, other):
        if not isinstance(other, Book):
            return False

        return (set(self.author) == set(other.author) and
                set(self.name) == set(other.name) and
                set(self.heros) == set(other.heros))

    def __hash__(self):
        return hash((self.author, self.name, frozenset(self.heros)))

    def __str__(self) -> str:
        return f'{self.author}, {self.name}'


class LibrarySearcher(object):
    def __init__(self):
        self.context_parser = RulesParser()
        self.lib_path = '../../resources/library.json'
        self.stop_words = stopwords.words('english')

        with io.open(self.lib_path, 'r', encoding='utf-8') as json_file:
            self.jdata = json.loads(json_file.read())
    '''
    for word in query:
        search word in CSV headers, else search word in topics keywords, then intersect results
    '''
    def search(self, query):
        words = [word for word in query.strip().split() if word not in self.stop_words]
        # words = [word[:-2] for word in words if word.endswith("'s")]
        total_results = set()
        for word in words:
            results_by_word = self.__search_word_in_library(word)
            if results_by_word and total_results:
                total_results = total_results.intersection(results_by_word)
            else:
                total_results = total_results.union(results_by_word)
        return total_results

    def __search_word_in_library(self, word):
        results = set()
        for d in self.jdata:
            for k in d:
                if isinstance(d[k], str) and word in d[k]:
                    self.__extract_book_information(results, d)
                    break
        context_results = self.find_book_in_context(word)
        if context_results:
            results = results.union(context_results)
        return results

    def __extract_book_information(self, results, d):
        max_len = max([len(auth) for auth in d['author'].split(',')])
        author = ''.join([name for name in d['author'].split(',') if len(name) == max_len]).strip()
        book_name = d['book_name'].split(',')[0]
        if 'herous' in d:
            results.add(Book(author, book_name, d['herous'].split(',')))
        else:
            results.add(Book(author, book_name))

    def find_book_in_context(self, word):
        herou = self.context_parser.normalize_herou(word)
        topic = self.context_parser.normalize_topic(word)

        if topic:
            results = set()
            for d in self.jdata:
                if topic in d['literature_category'] or (herou and 'herous' in d and herou in d['herous']):
                    self.__extract_book_information(results, d)
            return results


if __name__ == '__main__':
    searcher = LibrarySearcher()
    for book in searcher.search('find a book about Electronic boy'):
        print(book, end='; ')
    print()
    for book in searcher.search('search any mathematics book'):
        print(book, end='; ')
