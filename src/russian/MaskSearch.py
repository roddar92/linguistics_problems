class RegexTrie:
    def __init__(self):
        self.children = {}

    def add(self, word):
        curr = self.children
        for letter in word:
            if letter not in curr:
                curr[letter] = {}
            curr = curr[letter]
        curr['is_leaf'] = True

    def search_all(self, key):
        answer = []
        self.__dfs(self.children, key, candidates=answer, start=0, prefix="")
        return answer

    def __dfs(self, node, key, candidates, start, prefix):
        if start == len(key) and 'is_leaf' in node:
            candidates.append(prefix)
            return

        ch = key[start]
        if ch in node:
            self.__dfs(node[ch], key, candidates, start=start + 1, prefix=prefix + ch)
        elif ch == '?':
            for letter in node:
                self.__dfs(node[letter], key, candidates, start=start + 1, prefix=prefix + letter)


if __name__ == '__main__':
    VOCABULARY = ['apple', 'orange', 'tomato', 'apfle', 'sandwich', 'avocado', 'tonic', 'timato']
    trie = RegexTrie()
    for w in VOCABULARY:
        trie.add(w)
    assert trie.search_all('t?mato') == ['tomato', 'timato']
    assert trie.search_all('ap?le') == ['apple', 'apfle']
    assert trie.search_all('a??le') == ['apple', 'apfle']
    assert trie.search_all('orange') == ['orange']
