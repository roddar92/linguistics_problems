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

    def __dfs_light(self, node, key, candidates, start, prefix):
        if start == len(key) and 'is_leaf' in node:
            candidates.append(prefix)
            return

        ch = key[start]
        if ch in node:
            self.__dfs(node[ch], key, candidates, start=start + 1, prefix=prefix + ch)
        elif ch == '?':
            for letter in node:
                self.__dfs(node[letter], key, candidates, start=start + 1, prefix=prefix + letter)
                
    def __dfs(self, node, key, candidates, start, prefix, next_ch=''):
        if 'is_leaf' in node and len(node) == 1 and next_ch not in ('', '*'):
            return

        if start == len(key) and 'is_leaf' in node:
            candidates.append(prefix)
            return

        ch = key[start] if start < len(key) else '' if key[start - 1] == '?' else '*'
        if ch in node:
            self.__dfs(node[ch], key, candidates, start=start + 1, prefix=prefix + ch)
        elif ch == '?':
            for letter in node:
                self.__dfs(node[letter], key, candidates, start=start + 1, prefix=prefix + letter)
        elif ch == '*':
            next_ch = key[start + 1] if start + 1 < len(key) else '*'

            if next_ch in node:
                self.__dfs(node[next_ch], key, candidates, start=start + 2, prefix=prefix + next_ch)

            for letter in node:
                if letter == 'is_leaf' and len(node) > 1:
                    continue

                if 'is_leaf' in node and next_ch == '*':
                    candidates.append(prefix)

                if letter != 'is_leaf':
                    self.__dfs(node[letter], key, candidates, start=start, prefix=prefix + letter, next_ch=next_ch) 


if __name__ == '__main__':
    VOCABULARY = ['ale', 'apple', 'orange', 'tomato', 'timati', 'apfle', 'tomatosoup',
                  'sandwich', 'avocado', 'avocadole', 'tonic', 'timato']
    trie = RegexTrie()
    for w in VOCABULARY:
        trie.add(w)
        
    assert trie.search_all('*') == sorted(VOCABULARY)
    assert trie.search_all('?')) == []
    assert trie.search_all('???')) == ['ale']
    assert trie.search_all('a*le') == ['ale', 'apple', 'apfle', 'avocadole']
    assert trie.search_all('t?mato') == ['tomato', 'timato']
    assert trie.search_all('t?mato*') == ['tomato', 'tomatosoup', 'timato']
    assert trie.search_all('ap?le') == ['apple', 'apfle']
    assert trie.search_all('a??le') == ['apple', 'apfle']
    assert trie.search_all('orange') == ['orange']
