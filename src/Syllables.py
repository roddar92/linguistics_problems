# -*- coding: utf-8 -*-
class SyllableModule(object):
    @staticmethod
    def is_russian_vowel(symbol):
        return symbol in "аеиоуыэюя"

    @staticmethod
    def is_russian_consonant(symbol):
        return symbol in "бвгджзйклмнпрстфчцчшщ"

    @staticmethod
    def is_english_vowel(symbol):
        return symbol in "aeiouy"

    @staticmethod
    def is_english_consonant(symbol):
        return symbol in "bcdfghjklmnpqrstvwxz"

    def russian_syllables_count(self, word):
        cnt = 0
        for letter in word:
            if self.is_russian_vowel(letter):
                cnt += 1

        return cnt

    def english_syllables_count(self, word):
        leng = len(word)
        if word[-1] == "e":
            leng -= 1

        cnt = 0
        prev = ""
        for i in range(leng):
            if (prev == "" or not self.is_english_vowel(prev)) and self.is_english_vowel(word[i]):
                cnt += 1
            prev = word[i]

        return cnt
