# -*- coding: utf-8 -*-
import io, json

from RulesParser import RulesParser


class Book(object):
    def __init__(self, author, name, heros=None):
        if heros is None:
            heros = []
        self.author = author
        self.name = name
        self.heros = heros


class LibrarySearcher(object):
    def __init__(self):
        self.context_parser = RulesParser()
        self.lib_path = 'resources/library.json'
        self.stop_words = {u'a', u'across', u'am', u'an', u'and', u'as', u'by',
                           u'but', u'in', u'it', u'no', u'not', u'yes', u'on', u'these', u'those',
                           u'this', u'that', u'the', u'to', u'what', u'under', u'for', u'if', u'then'}
    '''
    for word in query:
        search word in CSV headers, else search word in topics keywords, then intersect results
    '''
    def search(self, query):
        words = [word for word in query.strip().split() if word not in self.stop_words]
        words = [word[:-2] for word in words if word.endswith('\'s')]
        total_results = set()
        for word in words:
            results_by_word = self.search_word_in_library(word)
            if total_results and results_by_word:
                total_results.intersection(results_by_word)
            else:
                total_results.add(results_by_word)
        return total_results

    def search_word_in_library(self, word):
        results = set()
        with io.open(self.lib_path, 'r', encoding='utf-8') as json_file:
            jdata = json.loads(json_file.read())
            for d in jdata:
                for k in d:
                    if word in d[k]:
                        self.extract_book_information(results, d)
                        break
        results.add(self.find_book_in_context(word))
        return results

    def extract_book_information(self, results, d):
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

        if not topic:
            return None

        results = set()
        with io.open(self.lib_path, 'r', encoding='utf-8') as json_file:
            jdata = json.loads(json_file.read())
            for d in jdata:
                if topic in d['literature_category'] or ('herous' in d and herou in d['herous']):
                    self.extract_book_information(results, d)
        return results
