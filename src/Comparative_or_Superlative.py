# -*- coding: utf-8 -*-
from Syllables import SyllableModule


class AdjectiveComparisoner(object):
    @staticmethod
    def is_english_vowel(symbol):
        return symbol in "aeiouy"

    @staticmethod
    def is_english_consonant(symbol):
        return symbol in "bcdfghjklmnpqrstvwxz"

    def get_adjective_comparation(self, word, superlative=False):
        if word == "good":
            return "better" if not superlative else "best"
        elif word == "bad":
            return "worse" if not superlative else "worst"
        else:
            sm = SyllableModule()
            if sm.english_syllables_count(word) == 1:
                suffix = ("r" if word.endswith("e") else "er") if not superlative \
                    else ("st" if word.endswith("e") else "est")
                return ("" if not superlative else "the ") + word + suffix
            else:
                return ("more " if not superlative else "the most ") + word