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

    def autocomplete(self, prefix):
        curr = self.children
        for letter in prefix:
            if letter not in curr:
                return -1
            curr = curr[letter]
        key = curr.get('word', '')
        count = curr.get('score', 0)
        return self.__preorder(curr, key, count)

    def __preorder(self, node, key, max_count):
        if type(node) != dict:
            return key, max_count

        for ch in node:
            if ch in ('word', 'score'):
                continue
            if 'score' in node[ch] and max_count < node[ch]['score']:
                max_count = node[ch]['score']
                key = node[ch]['word']
            key, max_count = self.__preorder(node[ch], key, max_count)
        return key, max_count


class AutoComplete:
    def __init__(self, vocab=None):
        self.dictionary = Trie()
        if vocab:
            assert type(vocab) == dict
            for word, score in vocab.items():
                self.dictionary.add(word, score)

    def get_k_auto_completes(self, prefix, k=1):
        return self.dictionary.autocomplete(prefix)



if __name__ == '__main__':
    trie = Trie()
    trie.add('hackerearth', 10)
    trie.add('hackerrank', 9)
    trie.add('hacker', 6)
    assert trie.autocomplete('hacker') == ('hackerearth', 10)

    trie.add('hackerrating', 11)
    assert trie.autocomplete('hacker') == ('hackerrating', 11)
