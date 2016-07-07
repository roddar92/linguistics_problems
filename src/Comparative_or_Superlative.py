# -*- coding: utf-8 -*-
from Syllables import SyllableModule


class AdjectiveComparisoner(object):
    @staticmethod
    def is_english_vowel(symbol):
        return symbol in "aeiouy"

    @staticmethod
    def is_english_consonant(symbol):
        return symbol in "bcdfghjklmnpqrstvwxz"

    def get_adjective_in_the_comparative_degree(self, word, superlative=False):
        """Return adjective in the comparative degree"""
        word = word.lower()
        prefix = "" if not superlative else "the"

        if word == "good":
            word = "better" if not superlative else "best"
        elif word == "bad":
            word = "worse" if not superlative else "worst"
        else:
            sm = SyllableModule()
            if sm.english_syllables_count(word) == 1:
                suffix = ("r" if word.endswith("e") else "er") if not superlative \
                    else ("st" if word.endswith("e") else "est")

                if word.endswith("y"):
                    word = word[:-1] + "i"
                elif word[-1] in "bglpt" and self.is_english_vowel(word[-2]):
                    word += word[-1]

                word += suffix
            else:
                if not superlative:
                    prefix += "more"
                else:
                    prefix = " ".join([prefix, "most"])

        return " ".join([prefix, word])

    def get_all_comparisons(self, word):
        return [self.get_adjective_in_the_comparative_degree(word),
                self.get_adjective_in_the_comparative_degree(word, True)]
