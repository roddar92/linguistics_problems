# -*- coding: utf-8 -*-

"""
Testing Trie data structure for phrases matching
"""
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
        prev_word = self._ROOT
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
    
    
class PhraseTemplateTrie:
    _DEFAULT_LABEL = '__default__'

    def __init__(self):
        self.root = {}

    def __contains__(self, item):
        return self.get_label_for_phrase(item.split())
    
    @staticmethod
    def __get_node(node, word):
        if word not in node:
            node[word] = {}
        return node[word]
    
    # add recursively alternatives for tokens i.e. (token1|token2|...|tokenN)
    def __add_subtree(self, subphrase, label, node, token=''):
        if token != '':
            for part in token.split():
                node = self.__get_node(node, part)
                
        is_alternative = False
        for i, word in enumerate(subphrase):
            word = word.lower()
            if word.startswith('(') and word.endswith(')') and not is_alternative:
                is_alternative = True
                for token in word[1:-1].split('|'):
                    self.__add_subtree(subphrase[i + 1:], label, node, token)
            elif not is_alternative:
                node = self.__get_node(node, word)
                
        if not is_alternative:
            node['label'] = label

    def add_phrase(self, phrase, label=_DEFAULT_LABEL):
        self.__add_subtree(phrase, label, self.root)

    def get_label_for_phrase(self, phrase):
        i, node = 0, self.root
        while i < len(phrase) and phrase[i].lower() in node:
            node = node[phrase[i].lower()]
            i += 1

        return node.get('label', '')


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

    phrase_trie = PhraseTemplateTrie()
    phrase_trie.add_phrase(['Мама', '(мыла|умывала)', '(раму|рамку)'], 'X')
    phrase_trie.add_phrase(['Во', 'поле', '(берёзонька|кудрявая|зелёная и пушистая)', 'стояла'], 'Y')
    phrase_trie.add_phrase(['(Мама|Папа)', '(подарила|подарил)', 'мне', '(куклу|бабочку)'], 'Z')
    phrase_trie.add_phrase(['Во', 'поле', 'снежок', 'расстаял'], 'Y')
    phrase_trie.add_phrase(['у', 'Васи', 'сегодня', 'день', '(рождения|варенья)'], 'Z')
    phrase_trie.add_phrase(['я', 'помню', 'чудное', 'мгновенье'], 'P')
    phrase_trie.add_phrase(['я', 'помню', 'чудное', '(мгновенье|варенье)', 'передо', 'мной', 'явилась', 'ты'], 'A')

    start = time()
    assert phrase_trie.get_label_for_phrase(['Мама', 'мыла', 'раму']) == 'X'
    assert phrase_trie.get_label_for_phrase(['Мама', 'мыла', 'рамку']) == 'X'
    assert phrase_trie.get_label_for_phrase(['Во', 'поле', 'кудрявая', 'стояла']) == 'Y'
    assert phrase_trie.get_label_for_phrase(['Во', 'поле', 'зелёная', 'и', 'пушистая', 'стояла']) == 'Y'
    assert 'Мама мыла раму' in phrase_trie
    assert 'Мама мыла рамочку' not in phrase_trie
    print(f'Elapsed {(time() - start)/1000:.10f} sec')
