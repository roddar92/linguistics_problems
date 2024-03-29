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
        p_len, text_len = len(pattern), len(text)

        cP = Counter(pattern)
        cS = Counter(text[:p_len])

        indices = []
        for i in range(text_len - p_len + 1):
            if cP == cS:
                indices.append(i)
            cS[text[i]] -= 1
            if cS[text[i]] == 0:
                cS.pop(text[i])

            if i + p_len < text_len:
                cS[text[i + p_len]] += 1

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
    assert anagram_voc.find_anagrams('cbaebabacd', 'abc') == [0, 6]
