class TrieNode:
    _DEFAULT_NODE_LABEL = '__NODE__'

    def __init__(self, word):
        self.word = word
        self.children = {}
        self.leaf_label = self._DEFAULT_NODE_LABEL

    def get_word(self):
        return self.word

    def get_children(self):
        return self.children

    def set_children(self, children):
        self.children = children

    def get_leaf_label(self):
        return self.leaf_label

    def set_leaf_label(self, label):
        self.leaf_label = label

    def __eq__(self, o):
        return super().__eq__(o)

    def __hash__(self):
        return super().__hash__()


class Trie:
    def __init__(self):
        self.root = TrieNode('__ROOT__')

    def add(self, phrase, leaf_value):
        node = self.root
        for word in phrase:
            word = word.lower()
            found_in_children = False
            for child in node.get_children():
                if child.get_word() == word:
                    node = child
                    found_in_children = True
                    break

            if not found_in_children:
                new_node = TrieNode(word)
                node.children[new_node] = {}
                node = new_node

        node.set_leaf_label(leaf_value)

    def search(self, phrase) -> str:
        node = self.root
        if not node.get_children():
            return ''

        for word in phrase:
            word = word.lower()
            found_in_children = False
            for child in node.get_children():
                if child.get_word() == word:
                    node = child
                    found_in_children = True
                    break

            if not found_in_children:
                return ''

        return node.get_leaf_label()


if __name__ == '__main__':
    phrase_trie = Trie()
    phrase_trie.add(['Мама', 'мыла', 'раму'], 'X')
    phrase_trie.add(['Во', 'поле', 'берёзонька', 'стояла'], 'Y')
    phrase_trie.add(['Мама', 'подарила', 'мне', 'куклу'], 'Z')
    phrase_trie.add(['Во', 'поле', 'снежок', 'расстаял'], 'Y')
    phrase_trie.add(['у', 'Васи', 'сегодня', 'день', 'рождения'], 'Z')

    assert phrase_trie.search(['Мама', 'мыла', 'раму']) == 'X'
    assert phrase_trie.search(['Мама', 'мыла', 'рамку']) == ''
