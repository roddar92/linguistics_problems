# -*- coding: utf-8 -*-
from Syllables import SyllableModule


class AdjectiveComparisoner(object):

    def __init__(self):
        self.irregular_adjectives = dict()
        self.irregular_adjectives["good"] = ["better", "best"]
        self.irregular_adjectives["bad"] = ["worse", "worst"]
        self.irregular_adjectives["far"] = ["farther", "farthest"]
        self.irregular_adjectives["little"] = ["less", "least"]
        self.irregular_adjectives["much"] = ["more", "most"]

    @staticmethod
    def is_english_vowel(symbol):
        return symbol in "aeiouy"

    @staticmethod
    def is_english_consonant(symbol):
        return symbol in "bcdfghjklmnpqrstvwxz"

    def get_comparative_degree(self, word, superlative=False):
        """Return adjective in the comparative degree"""
        word = word.lower()
        prefix = "" if not superlative else "the"

        if word in self.irregular_adjectives:
            word = self.irregular_adjectives[word][0] if not superlative else self.irregular_adjectives[word][1]
        else:
            sm = SyllableModule()
            if sm.english_syllables_count(word) == 1:
                suffix = "er" if not superlative else "est"

                if word[-1] in "bdglpt" and self.is_english_vowel(word[-2]) and self.is_english_consonant(word[-3]):
                    word += word[-1]

                word += suffix
            elif word.endswith("y"):
                word = word[:-1] + "i"
            elif word.endswith("e"):
                suffix = "r" if not superlative else "st"
                word += suffix
            else:
                if not superlative:
                    prefix += "more"
                else:
                    prefix = " ".join([prefix, "most"])

        return " ".join([prefix, word])

    def get_all_comparisons(self, word):
        return [self.get_comparative_degree(word),
                self.get_comparative_degree(word, True)]
