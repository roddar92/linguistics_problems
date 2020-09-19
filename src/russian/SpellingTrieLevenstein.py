from sortedcontainers import SortedDict, SortedListWithKey
from typing import List


class SpellingLevensteinTree:
    def __init__(self):
        """
        Initialize if trie data structure
        """
        self.root = {}

    def add(self, word: str) -> None:
        """
        Add new word into trie
        """
        node = self.root
        for l in word:
            if l not in node:
                node[l] = SortedDict()
            node = node[l]
        node['is_leaf'] = True

    def build_dict(self, words: List[str]) -> None:
        """
        Build a dictionary through a list of words
        """
        for word in words:
            self.add(word)

    def find_longest_prefix(self, word: str) -> str:
        """
        Find the longest word prefix in a trie dictionary
        """
        pos, node = -1, self.root
        for i, letter in enumerate(word):
            if letter not in node:
                pos = i
                break
            node = node[letter]
        return word[:pos] if pos >= 0 else word

    def search(self, word: str, distance=0) -> SortedListWithKey:
        """
        Returns candidates list with words that equal to the given word after its modifying with Levenstein distance
        """
        def __dfs(curr_node, curr_prefix, prev_row):
            curr_row = [prev_row[0] + 1]
            min_dist = curr_row[0]

            for i in range(1, len(word) + 1):
                curr_row.append(min(
                    curr_row[i - 1] + 1,
                    prev_row[i] + 1,
                    prev_row[i - 1] + (word[i - 1] != curr_prefix[-1])
                ))
                min_dist = min(min_dist, curr_row[-1])

            if min_dist > distance:
                return

            if curr_row[-1] <= distance and 'is_leaf' in curr_node:
                candidates.add((''.join(curr_prefix), curr_row[-1]))

            for ll in curr_node:
                if ll != 'is_leaf':
                    __dfs(curr_node[ll], curr_prefix + [ll], curr_row)

        candidates = SortedListWithKey(key=lambda x: x[-1])
        for letter in self.root:
            __dfs(self.root[letter], [letter], range(len(word) + 1))
        return candidates


if __name__ == '__main__':
    dictionary = SpellingLevensteinTree()
    dictionary.build_dict(['hello', 'hallo', 'leetcode', 'hell'])

    assert dictionary.search('hello') == [('hello', 0)]
    assert dictionary.search('hhllo', 1) == [('hallo', 1), ('hello', 1)]
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
