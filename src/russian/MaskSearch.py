from functools import wraps
from time import time


class RegexTrie:
    __END = 'is_leaf'

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
        candidates = set()
        key_len = len(key)

        stack = [(self.root, 0, [])]
        while stack:
            node, start, prefix = stack.pop()
            if start == key_len:
                if 'is_leaf' in node:
                    candidates.add(''.join(prefix))
                continue

            ch = key[start]
            if ch in node:
                stack.append((node[ch], start + 1, prefix + [ch]))
            elif ch == '?':
                for letter, children in node.items():
                    if letter != 'is_leaf':
                        stack.append((children, start + 1, prefix + [letter]))

        return candidates

    def __dfs(self, key):
        candidates = set()
        key_len = len(key)

        stack = [(self.root, 0, [], '')]
        while stack:
            node, start, prefix, after_star_ch = stack.pop()

            if self.__END in node:
                if len(node) == 1 and after_star_ch.isalpha():
                    continue

                if start >= key_len:
                    candidates.add(''.join(prefix))
                    continue

            if start >= key_len:
                ch = '$' if key[start - 1] == '?' else '*'
            else:
                ch = key[start]

            if ch in node:
                stack.append((node[ch], start + 1, prefix + [ch], after_star_ch))
            elif ch == '?':
                for letter, children in node.items():
                    if letter != self.__END:
                        stack.append((children, start + 1, prefix + [letter], after_star_ch))
            elif ch == '*':
                if after_star_ch == '':
                    after_star_ch = key[start + 1] if start + 1 < key_len else '*'

                for letter, children in node.items():
                    if letter == self.__END:
                        if after_star_ch == '*':
                            candidates.add(''.join(prefix))
                        continue

                    add = 2 if letter == after_star_ch else 0
                    if letter == after_star_ch:
                        after_star_ch = ''

                    stack.append((children, start + add, prefix + [letter], after_star_ch))
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
        ('?', set()),
        ('???', {'ale'}),
        ('t?mato', {'timato', 'tomato'}),
        ('ap?le', {'apfle', 'apple'}),
        ('a??le', {'apfle', 'apple'}),
        ('orange', {'orange'})
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
