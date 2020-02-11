from typing import List


class WordFilterTrie:
    def __init__(self, words: List[str]):
        self.suff = '#'
        self.word = '~'
        self.root = {}
        for word in words:
            self.insert(word)
        
    def insert(self, word: str) -> None:
        for i in range(len(word), -1, -1):
            self.__insert_partition_word(word[i:] + self.suff + word)
        
    def __insert_partition_word(self, word) -> None:
        node = self.root
        for letter in word:
            if letter not in node:
                node[letter] = {}
            node = node[letter]
        node[self.word] = word

    def f(self, prefix: str, suffix: str) -> List[str]:
        word = suffix + self.suff + prefix
        return self.find(word)
        
    def find(self, word: str):
        answer = []
        prefix = ''
        
        node = self.root
        for letter in word:
            if letter not in node: 
                return []
            node = node[letter]
            prefix += letter
        
        stack = [node]
        while stack:
            curr = stack.pop()
            if self.word in curr:
                answer.append(self.word)
            for letter in curr: 
                if letter != self.word:
                    stack.append(curr[letter])
        return answer
 
