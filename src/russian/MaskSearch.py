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
        return self.__dfs(key)

    def search_light_all(self, key):
        return self.__dfs_light(key)

    def __dfs_light(self, key):
        candidates = []

        stack = [(self.root, 0, '')]
        while stack:
            node, start, prefix = stack.pop()
            if start == len(key):
                if 'is_leaf' in node:
                    candidates.append(prefix)
                continue

            ch = key[start]
            if ch in node:
                stack.append((node[ch], start + 1, prefix + ch))
            elif ch == '?':
                for letter in node:
                    if letter != 'is_leaf':
                        stack.append((node[letter], start + 1, prefix + letter))

        return candidates

    def __dfs(self, key):
        candidates = set()

        stack = [(self.root, 0, '', '')]
        while stack:
            node, start, prefix, next_ch = stack.pop()

            if 'is_leaf' in node and len(node) == 1 and next_ch not in ('', '*'):
                continue

            if start >= len(key) and 'is_leaf' in node:
                candidates.add(prefix)
                continue

            if start < len(key):
                ch = key[start]
            elif key[start - 1] == '?':
                ch = '$'
            else:
                ch = '*'

            if ch in node:
                stack.append((node[ch], start + 1, prefix + ch, ''))
            elif ch == '?':
                for letter in node:
                    if letter != 'is_leaf':
                        stack.append((node[letter], start + 1, prefix + letter, ''))
            elif ch == '*':
                next_ch = key[start + 1] if start + 1 < len(key) else '*'

                for letter in node:
                    if letter == 'is_leaf' and next_ch == '*':
                        candidates.add(prefix)

                    if letter == 'is_leaf':
                        continue

                    add = 2 if letter == next_ch else 0
                    n_ch = '' if letter == next_ch else next_ch

                    stack.append((node[letter], start + add, prefix + letter, n_ch))
        return candidates


def profile(func):
    @wraps(func)
    def wrapper(*args):
        start = time()
        result = func(*args)
        print(f'Elapsed for {args[-1]} pattern: {(time() - start):.10f} ms...')
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
        ('t?mato', ['timato', 'tomato']),
        ('ap?le', ['apfle', 'apple']),
        ('a??le', ['apfle', 'apple']),
        ('orange', ['orange'])
    ]

    for arg, expected in test_pairs:
        assert search_by_pattern(trie.search_light_all, arg) == expected

    test_pairs = [
        ('?', set()),
        ('???', {'ale'}),
        ('a*le', {'ale', 'avocadole', 'apfle', 'apple'}),
        ('t*m*to', {'timato', 'tomato'}),
        ('t*m*t?', {'timato', 'timati', 'tomato'}),
        ('t*mat?', {'timato', 'timati', 'tomato'}),
        ('t?mato', {'timato', 'tomato'}),
        ('t?mato*', {'timato', 'tomato', 'tomatosoup'}),
        ('ap?le', {'apfle', 'apple'}),
        ('a??le', {'apfle', 'apple'}),
        ('t*mat*up', {'tomatosoup'}),
        ('orange', {'orange'})
    ]

    assert sorted(search_by_pattern(trie.search_all, '*')) == sorted(VOCABULARY)

    for arg, expected in test_pairs:
        assert search_by_pattern(trie.search_all, arg) == expected