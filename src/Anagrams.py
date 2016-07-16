# -*- coding: utf-8 -*-
# from collections import Counter


class AnagramOperations(object):
    def is_anagram(self, word1, word2):
        """Check is word1 the anagram of word2"""
        if len(word1) != len(word2):
            return False
        # return Counter(word1) == Counter(word2)

        a = {}
        b = {}

        for i in range(len(word1)):
            a[word1[i]] = a[word1[i]] + 1 if word1[i] in a else 1
            b[word2[i]] = b[word2[i]] + 1 if word2[i] in b else 1

        return a == b

    # todo create method for anagrams generation