from collections import namedtuple
from sortedcontainers import SortedList


class Trie:
    def __init__(self):
        self.children = {}

    def add(self, word, score):
        curr = self.children
        for letter in word:
            if letter not in curr:
                curr[letter] = {}
            curr = curr[letter]
        curr['score'] = score

    def find_most_freq(self, prefix):
        curr = self.find(prefix)
        return self.__preorder_for_most_freq(curr, prefix) if curr else None

    def find(self, prefix):
        curr = self.children
        for letter in prefix:
            if letter not in curr:
                return None
            curr = curr[letter]
        return curr

    @staticmethod
    def __preorder_for_most_freq(node, key):
        max_key, max_count = key, -1
        stack = [(node, key)]

        while stack:
            node, prefix = stack.pop()
            if 'score' in node and node['score'] > max_count:
                max_count = node['score']
                max_key = prefix
            for ch in node:
                if ch != 'score':
                    stack.append((node[ch], prefix + ch))
        return max_key, max_count


class AutoComplete:
    def __init__(self, vocab=None):
        self.node = namedtuple('Node', 'word count')
        self.heap = SortedList(key=lambda x: -x.count)
        self.dictionary = Trie()
        if vocab:
            assert type(vocab) == dict
            for word, score in vocab.items():
                self.dictionary.add(word, score)

    def __preorder(self, node, prefix):
        stack = [(node, prefix)]
        while stack:
            node, prefix = stack.pop()
            if 'score' in node:
                self.heap.add(self.node(prefix, node['score']))
            for ch in node:
                if ch != 'score':
                    stack.append((node[ch], prefix + ch))

    def get_k_auto_completes(self, prefix, k=1):
        if k == 1:
            return self.dictionary.find_most_freq(prefix)
        else:
            node = self.dictionary.find(prefix)
            if not node:
                return []

            self.__preorder(node, prefix)
            answer = []

            while k > 0:
                node = self.heap.pop(0)
                answer.append((node.word, node.count))
                k -= 1
            return answer


if __name__ == '__main__':
    trie = Trie()
    trie.add('hackerearth', 10)
    trie.add('hackerrank', 9)
    trie.add('hacker', 6)
    assert trie.find_most_freq('hacker') == ('hackerearth', 10)

    trie.add('hackerrating', 11)
    assert trie.find_most_freq('hacker') == ('hackerrating', 11)

    vocabulary = {
        'hackerearth': 10,
        'hackerrank': 9,
        'hacker': 6,
        'hackerrating': 11
    }
    complete = AutoComplete(vocab=vocabulary)
    print(complete.get_k_auto_completes('hacker', k=3))
