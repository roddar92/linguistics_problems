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
        curr['word'] = word
        curr['score'] = score

    def find_most_freq(self, prefix):
        curr = self.children
        for letter in prefix:
            if letter not in curr:
                return -1
            curr = curr[letter]
        key = curr.get('word', '')
        count = curr.get('score', 0)
        return self.__preorder_for_most_freq(curr, key, count)

    def __preorder_for_most_freq(self, node, key, max_count):
        if type(node) != dict:
            return key, max_count

        for ch in node:
            if ch in ('word', 'score'):
                continue
            if 'score' in node[ch] and max_count < node[ch]['score']:
                max_count = node[ch]['score']
                key = node[ch]['word']
            key, max_count = self.__preorder_for_most_freq(node[ch], key, max_count)
        return key, max_count


class AutoComplete:
    def __init__(self, vocab=None):
        self.node = namedtuple('Node', 'word count')
        self.heap = SortedList(key=lambda x: -x.count)
        self.dictionary = Trie()
        if vocab:
            assert type(vocab) == dict
            for word, score in vocab.items():
                self.dictionary.add(word, score)

    def __preorder(self, node):
        for ch in node:
            if ch in ('word', 'score'):
                continue
            if 'score' in node[ch]:
                self.heap.add(self.node(node[ch]['word'], node[ch]['score']))
            self.__preorder(node[ch])

    def get_k_auto_completes(self, prefix, k=1):
        if k == 1:
            return self.dictionary.find_most_freq(prefix)
        else:
            node = self.dictionary.children
            self.__preorder(node)
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
