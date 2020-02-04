from typing import List


class SpellingDictionary:
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

    def __search_dfs(self, node, word, dist, candidates, prefix, count, start):
        if start == len(word) and 'is_leaf' in node and count <= dist:
            candidates.append(''.join(prefix))
            return

        if start >= len(word):
            return

        letter = word[start]
        for ll in node:
            if ll != 'is_leaf':
                one = int(letter != ll)
                self.__search_dfs(node[ll], word, dist, candidates, prefix + [ll], count + one, start + 1)

    def search(self, word: str, distance=0) -> List[str]:
        """
        Returns candidates list with words that equal to the given word after modifying exactly distance characters
        """
        candidates = []
        self.__search_dfs(self.root, word, distance, candidates, [], 0, 0)
        return candidates


if __name__ == '__main__':
    dictionary = SpellingDictionary()
    dictionary.build_dict(['hello', 'hallo', 'leetcode', 'hell'])

    assert dictionary.search('hello') == ['hello']
    assert dictionary.search('hhllo', 1) == ['hello', 'hallo']
    assert dictionary.search('hkelo', 2) == ['hello', 'hallo']
    assert not dictionary.search('hklo')
    assert dictionary.search('hklo', 2) == ['hell']
    assert dictionary.search('hkloo', 2) == ['hello', 'hallo']
    assert not dictionary.search('elloo', 2)
