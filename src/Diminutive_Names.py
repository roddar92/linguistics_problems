# -*- coding: utf-8 -*-
class Diminutiver(object):
    @staticmethod
    def is_vowel(symbol):
        return symbol in "аеиоуыэя"

    @staticmethod
    def is_sibilant(symbol):
        return symbol in "чшщ"

    @staticmethod
    def is_sonant(symbol):
        return symbol in "мр"

    def get_diminutive(self, name):
        if self.is_sonant(name[-2]):
            suffix = "очка"
        else:
            suffix = "енька"
        return name[:-1] + suffix
