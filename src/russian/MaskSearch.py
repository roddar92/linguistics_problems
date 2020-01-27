from functools import wraps
from time import time


class RegexTrie:
    def __init__(self):
        self.root = {}

    def add(self, word):
        curr = self.root
        for letter in word:
            if letter not in curr:
                curr[letter] = {}
            curr = curr[letter]
        curr['is_leaf'] = True

    def search_all(self, key):
        answer = []
        self.__dfs(self.root, key, candidates=answer, start=0, prefix="")
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
                if letter != 'is_leaf':
                    self.__dfs(node[letter], key, candidates, start=start + 1, prefix=prefix + letter)
                
    def __dfs(self, node, key, candidates, start, prefix, next_ch=''):
        if 'is_leaf' in node and len(node) == 1 and next_ch not in ('', '*'):
            return

        if start >= len(key) and 'is_leaf' in node:
            candidates.append(prefix)
            return

        if start < len(key):
            ch = key[start]
        elif key[start - 1] == '?':
            ch = '$'
        else:
            ch = '*'

        if ch in node:
            self.__dfs(node[ch], key, candidates, start=start + 1, prefix=prefix + ch)
        elif ch == '?':
            for letter in node:
                if letter != 'is_leaf':
                    self.__dfs(node[letter], key, candidates, start=start + 1, prefix=prefix + letter)
        elif ch == '*':
            next_ch = key[start + 1] if start + 1 < len(key) else '*'

            if next_ch in node:
                self.__dfs(node[next_ch], key, candidates, start=start + 2, prefix=prefix + next_ch)

            for letter in node:
                if letter == 'is_leaf' and next_ch == '*':
                    candidates.append(prefix)

                if letter != 'is_leaf':
                    self.__dfs(node[letter], key, candidates, start=start, prefix=prefix + letter, next_ch=next_ch)


def profile(func):
    @wraps(func)
    def wrapper(*args):
        start = time()
        result = func(*args)
        print(f'Elapsed {(time() - start):.10f} ms...')
        return result
    return wrapper


@profile
def search_by_pattern(func, pattern):
    return func(pattern)


if __name__ == '__main__':
    VOCABULARY = ['ale', 'apple', 'orange', 'tomato', 'timati', 'apfle', 'tomatosoup',
                  'sandwich', 'avocado', 'avocadole', 'tonic', 'timato']
    trie = RegexTrie()
    for w in VOCABULARY:
        trie.add(w)

    test_pairs = [
        ('?', []),
        ('???', ['ale']),
        ('a*le', ['ale', 'apple', 'apfle', 'avocadole']),
        ('t*m*to', ['tomato', 'timato']),
        ('t*m*t?', ['tomato', 'timati', 'timato']),
        ('t*mat?', ['tomato', 'timati', 'timato']),
        ('t?mato', ['tomato', 'timato']),
        ('t?mato*', ['tomato', 'tomatosoup', 'timato']),
        ('ap?le', ['apple', 'apfle']),
        ('a??le', ['apple', 'apfle']),
        ('t*mat*up', ['tomatosoup']),
        ('orange', ['orange'])
    ]
        
    assert sorted(search_by_pattern(trie.search_all, '*')) == sorted(VOCABULARY)

    for arg, expected in test_pairs:
        assert search_by_pattern(trie.search_all, arg) == expected
