from typing import List, Tuple


class SpellingHammingDictionary:
    def __init__(self):
        """
        Initialize your data structure here.
        """
        self.root = {}

    def add(self, word: str) -> None:
        node = self.root
        for l in word:
            if l not in node:
                node[l] = {}
            node = node[l]
        node['is_leaf'] = True

    def build_dict(self, words: List[str]) -> None:
        """
        Build a dictionary through a list of words
        """
        for word in words:
            self.add(word)

    def __search_dfs(self, node, word, dist, candidates, prefix, cost, start):
        if start == len(word) and 'is_leaf' in node and cost <= dist:
            candidates.append((''.join(prefix), cost))
            return

        if start - len(word) > cost:
            return

        letter = word[start] if start < len(word) else '*'
        for ll in node:
            if ll != 'is_leaf':
                one = int(letter != ll)
                self.__search_dfs(node[ll], word, dist, candidates, prefix + [ll], cost + one, start + 1)

    def find_longest_prefix(self, word):
        pos, node = -1, self.root
        for i, letter in enumerate(word):
            if letter not in node:
                pos = i
                break
            node = node[letter]
        return word[:pos] if pos >= 0 else word

    def search(self, word: str, distance=0) -> List[Tuple[str, int]]:
        """
        Returns candidates list with words that equal to the given word after modifying exactly distance characters
        """
        candidates = []
        self.__search_dfs(self.root, word, distance, candidates, [], 0, 0)
        return candidates


if __name__ == '__main__':
    dictionary = SpellingHammingDictionary()
    dictionary.build_dict(['hello', 'hallo', 'leetcode', 'hell'])

    assert dictionary.search('hello') == [('hello', 0)]
    assert dictionary.search('hhllo', 1) == [('hello', 1), ('hallo', 1)]
    assert dictionary.search('hhllo', 2) == [('hello', 1), ('hallo', 1)]
    assert dictionary.search('hkelo', 2) == [('hello', 2), ('hallo', 2)]
    assert not dictionary.search('hklo')
    assert dictionary.search('hklo', 2) == [('hell', 2)]
    assert dictionary.search('lettcode', 2) == [('leetcode', 1)]
    assert dictionary.search('hkloo', 2) == [('hello', 2), ('hallo', 2)]
    assert not dictionary.search('elloo', 2)
    assert dictionary.search('elloo', 3) == [('hello', 3), ('hallo', 3)]
    assert dictionary.find_longest_prefix('elloo') == ''
    assert dictionary.find_longest_prefix('hkloo') == 'h'
    assert dictionary.find_longest_prefix('lettcode') == 'le'
    assert dictionary.find_longest_prefix('hello') == 'hello'
