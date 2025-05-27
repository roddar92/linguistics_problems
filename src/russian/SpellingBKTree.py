import editdistance
from typing import Dict, List, Tuple, Set


class BKTree:
    def __init__(self, words_list: List[str], distance: callable):
        self.root = {}
        self.root_word = None
        self.__distance = distance
        self.__build_bk(words_list)

    def __build_bk(self, words_list):
        for word in words_list:
            if not self.root:
                self.__add(word, self.root, '')
                self.root_word = next(iter(self.root))
            else:
                self.__add(word, self.root[self.root_word], self.root_word)

    def __get_element_with_same_distance(self, word: str, node: Dict[str, Dict], dist: int):
        """
        Returns a child, whose distance to `word` equals to `dist`
        :param word:
        :param node:
        :param dist:
        return (child, parent word)
        """
        for key in node:
            if self.__distance(key, word) == dist:
                return node[key], key
        return None, None

    def __add(self, word: str, node: Dict[str, Dict], key: str):
        """
        Adds new word to the tree
        1. If the current node is empty, then add to it a pair <word, empty_dict>
        2. Calculate distance `d` between `word` and `key`
        3. Check a child node whose distance equals to `d`
        4. If a child node exists, then add a new word to this child node, otherwise do Point 1
        :param word:
        :param node:
        :param key:
        """

        if not node:
            node[word] = {}
            return

        dist = self.__distance(word, key)
        child_node, parent_key = self.__get_element_with_same_distance(key, node, dist)

        if not child_node and not parent_key:
            node[word] = {}
            return
        else:
            self.__add(word, child_node, parent_key)

    def search(self, word: str, n=0) -> Set[Tuple[str, int]]:
        """
        Returns a set of candidates for a misspelling word
        A stack contains those child nodes whose calculated distance lies
        in the interval (d(word, node_key) - N, d(word, node_key) + N)
        :param word:
        :param n:
        return: Set[Tuple[str, int]]
        """

        stack = [(self.root[self.root_word], self.root_word)]
        matches = set()
        while stack:
            node, key = stack.pop()
            dist = self.__distance(word, key)
            if dist <= n:
                matches.add((key, dist))

            for candidate in node:
                distch = self.__distance(key, candidate)
                if dist - n <= distch <= dist + n:
                    stack.append((node[candidate], candidate))
        return matches


if __name__ == '__main__':

    # Test BK-tree with standard Levenstein distance
    words = ['hello', 'hallo', 'leetcode', 'hell', 'bell']
    dictionary = BKTree(words, editdistance.eval)

    assert dictionary.search('hello') == {('hello', 0)}
    assert dictionary.search('hhllo', 1) == {('hallo', 1), ('hello', 1)}
    assert dictionary.search('ehllo', 2) == {('hallo', 2), ('hello', 2)}
    assert dictionary.search('hhllo', 2) == {('hallo', 1), ('hello', 1), ('hell', 2)}
    assert dictionary.search('hkelo', 2) == {('hallo', 2), ('hell', 2), ('hello', 2)}
    assert not dictionary.search('hklo')
    assert dictionary.search('hklo', 3) == {('hallo', 2), ('hell', 2), ('bell', 3), ('hello', 2)}
    assert dictionary.search('lettcode', 2) == {('leetcode', 1)}
    assert dictionary.search('hkloo', 2) == {('hallo', 2), ('hello', 2)}
    assert dictionary.search('elloo', 2) == {('hello', 2)}
    assert dictionary.search('elloo', 3) == {('hello', 2), ('hallo', 3), ('hell', 3), ('bell', 3)}
    assert dictionary.search('leetcdoe', 2) == {('leetcode', 2)}
