# -*- coding: utf-8 -*-
class AnagramOperations(object):
    def is_anagram(self, word1, word2):
        """Check is word1 the anagram of word2"""
        if len(word1) != len(word2):
            return False
        return sorted(word1) == sorted(word2)

    # todo create method for anagrams generation