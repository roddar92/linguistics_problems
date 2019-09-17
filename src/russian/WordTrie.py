from time import time


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


class PhraseTrie:
    _DEFAULT_LABEL = '__default__'
    _ROOT = '__root__'

    def __init__(self):
        self.root = {self._ROOT: {}}

    def __contains__(self, item):
        return self.get_label_for_phrase(item.split())

    def add_phrase(self, phrase, label=_DEFAULT_LABEL):
        node = self.root
        i, prev_word = 0, self._ROOT
        for i, word in enumerate(phrase):
            word = word.lower()
            children = node.get(prev_word, None)
            if word in children.keys():
                node = children
            else:
                new_node = {word: {'label': label} if i == len(phrase) - 1 else {}}
                node[prev_word].update(new_node)
                node = new_node
            prev_word = word

    def get_label_for_phrase(self, phrase):
        node = self.root
        prev_word = self._ROOT
        for word in phrase:
            word = word.lower()
            children = node.get(prev_word, None)
            if not children or word not in children.keys():
                return ''

            node = children
            prev_word = word

        return node[prev_word]['label']


if __name__ == '__main__':
    phrase_trie = Trie()
    phrase_trie.add(['Мама', 'мыла', 'раму'], 'X')
    phrase_trie.add(['Во', 'поле', 'берёзонька', 'стояла'], 'Y')
    phrase_trie.add(['Мама', 'подарила', 'мне', 'куклу'], 'Z')
    phrase_trie.add(['Во', 'поле', 'снежок', 'расстаял'], 'Y')
    phrase_trie.add(['у', 'Васи', 'сегодня', 'день', 'рождения'], 'Z')
    phrase_trie.add(['я', 'помню', 'чудное', 'мгновенье'], 'P')
    phrase_trie.add(['я', 'помню', 'чудное', 'мгновенье', 'передо', 'мной', 'явилась', 'ты'], 'A')

    start = time()
    assert phrase_trie.search(['Мама', 'мыла', 'раму']) == 'X'
    assert phrase_trie.search(['Мама', 'мыла', 'рамку']) == ''
    print(f'Elapsed {(time() - start)/1000:.10f} sec')

    phrase_trie = PhraseTrie()
    phrase_trie.add_phrase(['Мама', 'мыла', 'раму'], 'X')
    phrase_trie.add_phrase(['Во', 'поле', 'берёзонька', 'стояла'], 'Y')
    phrase_trie.add_phrase(['Мама', 'подарила', 'мне', 'куклу'], 'Z')
    phrase_trie.add_phrase(['Во', 'поле', 'снежок', 'расстаял'], 'Y')
    phrase_trie.add_phrase(['у', 'Васи', 'сегодня', 'день', 'рождения'], 'Z')
    phrase_trie.add_phrase(['я', 'помню', 'чудное', 'мгновенье'], 'P')
    phrase_trie.add_phrase(['я', 'помню', 'чудное', 'мгновенье', 'передо', 'мной', 'явилась', 'ты'], 'A')

    start = time()
    assert phrase_trie.get_label_for_phrase(['Мама', 'мыла', 'раму']) == 'X'
    assert phrase_trie.get_label_for_phrase(['Мама', 'мыла', 'рамку']) == ''
    assert 'Мама мыла раму' in phrase_trie
    assert 'Мама мыла рамку' not in phrase_trie
    print(f'Elapsed {(time() - start)/1000:.10f} sec')
