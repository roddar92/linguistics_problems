# -*- coding: utf-8 -*-
class SyllableModule(object):
    @staticmethod
    def is_russian_vowel(symbol):
        return symbol in "аеиоуыэя"

    @staticmethod
    def is_english_vowel(symbol):
        return symbol in "aeiou"

    def syllables_count(self, word, engish=False):
        if engish and word[-1] == "e":
            leng = len(word) - 1
        else:
            leng = len(word)

        cnt = 0
        prev = ""
        for i in range(leng):
            if engish:
                if (prev == "" or not self.is_english_vowel(prev)) and self.is_english_vowel(word[i]):
                    cnt += 1
                prev = word[i]
            else:
                if self.is_russian_vowel(word[i]):
                    cnt += 1

        return cnt
