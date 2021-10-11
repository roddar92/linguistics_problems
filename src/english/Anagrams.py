from collections import Counter, defaultdict
from string import ascii_lowercase


class AnagramDistance:
    @staticmethod
    def distance(word1, word2):
        if len(word2) != len(word1):
            return -1

        char_count = Counter(word1)

        for ch in word2:
            char_count[ch] -= 1
        return sum(-v for v in char_count.values() if v < 0)


class AnagramVocabulary:
    def __init__(self, words=None):
        self.vocabulary = {}
        self.anagram_dist = AnagramDistance()

        if words and isinstance(words, list):
            self.__make_vocabulary(words)

    @staticmethod
    def group_anagrams(words):
        groups = defaultdict(list)
        for word in words:
            groups[str(tuple(word.count(ch) for ch in ascii_lowercase))].append(word)
        return groups

    def __make_vocabulary(self, words):
        for word in words:
            nearest_word = [w for w in self.vocabulary if self.anagram_dist.distance(word, w) == 0]
            if not nearest_word:
                self.vocabulary[word] = []
            else:
                self.vocabulary[nearest_word[0]] += [word]

    def find_anagrams(self, text, pattern):
        cP, cS = Counter(pattern), Counter(text[:len(pattern)])
        indices, start = [], 0

        for end in range(len(pattern), len(text)):
            if cS == cP:
                indices.append(start)

            start_ch, end_ch = text[start], text[end]
            if cS[start_ch] == 1:
                cS.pop(start_ch)
            else:
                cS[start_ch] -= 1

            if end_ch not in cS:
                cS[end_ch] = 1
            else:
                cS[end_ch] += 1

            start += 1

        if cS == cP:
            indices.append(start)
        return indices

    def add_words(self, words):
        self.__make_vocabulary(words)


if __name__ == '__main__':
    anagram_dist = AnagramDistance()
    assert anagram_dist.distance('abcd', 'bba') == -1
    assert anagram_dist.distance('', 'tuf') == -1
    assert anagram_dist.distance('abc', 'bba') == 1
    assert anagram_dist.distance('ab', 'bc') == 1
    assert anagram_dist.distance('abb', 'bba') == 0
    assert anagram_dist.distance('abc', 'bca') == 0
    assert anagram_dist.distance('prs', 'tuf') == 3
    assert anagram_dist.distance('aaa', 'bbb') == 3

    dictionary = ['abcd', 'bba', 'tuf', 'abc', 'ab', 'bc', 'abb', 'bca', 'prs', 'aaa', 'bbb', 'fut', 'dacb']
    anagram_voc = AnagramVocabulary()
    print(anagram_voc.group_anagrams(dictionary))
