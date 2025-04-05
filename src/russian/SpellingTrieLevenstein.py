from sortedcontainers import SortedDict, SortedListWithKey
from typing import List, Optional


class SpellingLevensteinTree:
    __END = 'is_leaf'

    def __init__(self, use_damerau_modification=False):
        """
        Initialize if trie data structure
        :param use_damerau_modification Use Damerau-Levenstein distance, otherwise standard Lenevstein metric
        """
        self.root = SortedDict()
        self.use_damerau_modification = use_damerau_modification

    @staticmethod
    def __get_row_len(word: str) -> int:
        return len(word) + 1

    def add(self, word: str) -> None:
        """
        Add new word into trie
        :param word new string for the dictionary
        :return
        """
        node = self.root
        for letter in word:
            if letter not in node:
                node[letter] = SortedDict()
            node = node[letter]
        node[self.__END] = True

    def build_dict(self, words: List[str]) -> None:
        """
        Build a dictionary through a list of words
        :param words list of words for dictionary creating
        :return
        """
        for word in words:
            self.add(word)

    def find_longest_prefix(self, word: str) -> str:
        """
        Find the longest word prefix in a trie dictionary
        :param word any string
        :return the maximum prefix in the dictionary
        """
        i, node, word_len = 0, self.root, len(word)
        while i < word_len and word[i] in node:
            node = node[word[i]]
            i += 1
        return word[:i]

    def search(self, word: str, distance=0) -> SortedListWithKey:
        """
        Returns candidates list of words that equal to the given word after its modifying with Levenstein (DL) distance
        :param word Misspelled word
        :param distance Maximum distance for candidates where their cost could be less than given parameter
        :return array of candidates with their distances
        """

        _calc_distance = self.__calculate_distance
        _get_row_len = self.__get_row_len

        candidates = SortedListWithKey(key=lambda x: x[::-1])
        stack = [([letter], children, None, [*range(_get_row_len(word))])
                 for letter, children in self.root.items()]

        while stack:
            prefix, node, pre_prev_row, prev_row = stack.pop()
            curr_row, min_dist = _calc_distance(word, prefix, pre_prev_row, prev_row)

            if min_dist > distance:
                continue

            if curr_row[-1] <= distance and self.__END in node:
                candidates.add((''.join(prefix), curr_row[-1]))

            stack.extend(
                (prefix + [letter], children, prev_row if self.use_damerau_modification else None, curr_row)
                for letter, children in node.items() if letter != self.__END
            )

        return candidates

    def __calculate_distance(self, word: str, prefix: List[str],
                             pre_prev_row: Optional[List[int]], prev_row: List[int]):
        """
        Calculate Levenstein (DL) distance for input word and the current prefix
        :param word Misspelled word
        :param prefix The current prefix traversed in the trie
        :param pre_prev_row The row for DL distance calculation
        :param prev_row The row for Levenstein distance calculation
        :return the last calculated row and the minimum distance
        """
        _get_row_len = self.__get_row_len

        curr_row = [0] * len(prev_row)
        curr_row[0] = prev_row[0] + 1
        for i in range(1, _get_row_len(word)):
            curr_row[i] = min(
                curr_row[i - 1] + 1,
                prev_row[i] + 1,
                prev_row[i - 1] + (word[i - 1] != prefix[-1])
            )

            if self.use_damerau_modification:
                if len(prefix) > 1 and i >= 1 and word[i - 1] == prefix[-2] and \
                        word[i - 1] != prefix[-1] and word[i - 2] == prefix[-1]:
                    curr_row[i] = min(curr_row[i], pre_prev_row[i - 2] + 1)

        min_dist = min(curr_row)
        return curr_row, min_dist


if __name__ == '__main__':

    # Test standard Levenstein Trie
    dictionary = SpellingLevensteinTree()
    dictionary.build_dict(['hello', 'hallo', 'leetcode', 'hell'])

    assert dictionary.search('hello') == [('hello', 0)]
    assert dictionary.search('hhllo', 1) == [('hallo', 1), ('hello', 1)]
    assert dictionary.search('ehllo', 2) == [('hallo', 2), ('hello', 2)]
    assert dictionary.search('hhllo', 2) == [('hallo', 1), ('hello', 1), ('hell', 2)]
    assert dictionary.search('hkelo', 2) == [('hallo', 2), ('hell', 2), ('hello', 2)]
    assert not dictionary.search('hklo')
    assert dictionary.search('hklo', 2) == [('hallo', 2), ('hell', 2), ('hello', 2)]
    assert dictionary.search('lettcode', 2) == [('leetcode', 1)]
    assert dictionary.search('hkloo', 2) == [('hallo', 2), ('hello', 2)]
    assert dictionary.search('elloo', 2) == [('hello', 2)]
    assert dictionary.search('elloo', 3) == [('hello', 2), ('hallo', 3), ('hell', 3)]
    assert dictionary.find_longest_prefix('elloo') == ''
    assert dictionary.find_longest_prefix('hkloo') == 'h'
    assert dictionary.find_longest_prefix('lettcode') == 'le'
    assert dictionary.find_longest_prefix('hello') == 'hello'
    assert dictionary.search('leetcdoe', 2) == [('leetcode', 2)]

    # Test Damerau-Levenstein Trie
    dictionary = SpellingLevensteinTree(use_damerau_modification=True)
    dictionary.build_dict(['hello', 'hallo', 'leetcode', 'hell'])

    assert dictionary.search('ehllo', 2) == [('hello', 1), ('hallo', 2), ('hell', 2)]
    assert dictionary.search('leetcdoe', 2) == [('leetcode', 1)]
    assert dictionary.search('eletcode', 2) == [('leetcode', 1)]
