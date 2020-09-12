from typing import List, Tuple


class SpellingLevensteinTree:
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

    def __search_dfs(self, node, word, dist, candidates, prefix, last_row):
        chars = len(word) + 1
        current_row = [last_row[0] + 1]

        for i in range(1, chars):
            insert_or_del = min(current_row[i - 1] + 1, last_row[i] + 1)
            replace = last_row[i - 1] + int(word[i - 1] != prefix[-1])
            current_row.append(min(insert_or_del, replace))

        if current_row[-1] <= dist and 'is_leaf' in node:
            candidates.append((''.join(prefix), current_row[-1]))

        if min(current_row) <= dist:
            for ll in node:
                if ll != 'is_leaf':
                    self.__search_dfs(node[ll], word, dist, candidates, prefix + [ll], current_row)

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
        Returns candidates list with words that equal to the given word after its modifying with Levenstein distance
        """
        candidates = []
        current_row = list(range(len(word) + 1))
        for letter in self.root:
            self.__search_dfs(self.root[letter], word, distance, candidates, [letter], current_row)
        return candidates


if __name__ == '__main__':
    dictionary = SpellingLevensteinTree()
    dictionary.build_dict(['hello', 'hallo', 'leetcode', 'hell'])

    assert dictionary.search('hello') == [('hello', 0)]
    assert dictionary.search('hhllo', 1) == [('hello', 1), ('hallo', 1)]
    assert dictionary.search('hhllo', 2) == [('hell', 2), ('hello', 1), ('hallo', 1)]
    assert dictionary.search('hkelo', 2) == [('hell', 2), ('hello', 2), ('hallo', 2)]
    assert not dictionary.search('hklo')
    assert dictionary.search('hklo', 2) == [('hell', 2), ('hello', 2), ('hallo', 2)]
    assert dictionary.search('lettcode', 2) == [('leetcode', 1)]
    assert dictionary.search('hkloo', 2) == [('hello', 2), ('hallo', 2)]
    assert dictionary.search('elloo', 2) == [('hello', 2)]
    assert dictionary.search('elloo', 3) == [('hell', 3), ('hello', 2), ('hallo', 3)]
    assert dictionary.find_longest_prefix('elloo') == ''
    assert dictionary.find_longest_prefix('hkloo') == 'h'
    assert dictionary.find_longest_prefix('lettcode') == 'le'
    assert dictionary.find_longest_prefix('hello') == 'hello'
