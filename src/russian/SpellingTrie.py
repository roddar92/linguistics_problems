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

    def __search_dfs(self, node, word, dist, count, start):
        if start == len(word):
            return 'is_leaf' in node and count <= dist

        letter = word[start]
        res = False
        for ll in node:
            if ll != 'is_leaf' and letter == ll:
                res = self.__search_dfs(node[letter], word, dist, count, start + 1)
            elif ll != 'is_leaf':
                res = self.__search_dfs(node[ll], word, dist, count + 1, start + 1)
            if res:
                return True
        return res

    def search(self, word: str, distance=1) -> bool:
        """
        Returns if there is any word in the trie that equals to the given word after modifying exactly distance characters
        """
        return self.__search_dfs(self.root, word, distance, 0, 0)


if __name__ == '__main__':
    dictionary = SpellingDictionary()
    dictionary.build_dict(['hello', 'leetcode'])

    assert dictionary.search('hello')
    assert dictionary.search('hhllo')
    assert dictionary.search('hkelo', 2)
    assert not dictionary.search('hklo', 2)
    assert not dictionary.search('hklo')
