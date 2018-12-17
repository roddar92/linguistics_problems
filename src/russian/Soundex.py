import re
from abc import ABC, abstractmethod
from editdistance import eval


class Soundex(ABC):
    _vowels = ''
    _table = str.maketrans('', '')

    def __init__(self, delete_zeros=False, cut_result=False, seq_cutted_len=4):
        self.delete_zeros = delete_zeros
        self.cut_result = cut_result
        self.seq_cutted_len = seq_cutted_len

    def _is_vowel(self, letter):
        return letter in self._vowels

    def _translate_vowels(self, word):
        return ''.join('0' if self._is_vowel(letter) else letter for letter in word)

    def _use_soundex_algorithm(self, word):
        word = word.lower()
        first, last = word[0], word[1:]
        last = last.translate(self._table)
        last = self._translate_vowels(last)
        if self.delete_zeros:
            last = re.sub('(0+)', '', last)
            last = re.sub(r'(\w)(\1)+', r'\1', last)
        if self.cut_result:
            last = last[3:] if len(last) >= 3 else last
            last += ('0' * (self.seq_cutted_len - len(last)))
        return first.capitalize() + last.upper()

    def get_vowels(self):
        return self._vowels

    def get_table(self):
        return self._table

    @abstractmethod
    def transform(self, word):
        return None


class EnglishSoundex(Soundex):
    _hw_replacement = re.compile(r'[hw]', re.IGNORECASE)

    _vowels = 'aeiouy'
    _table = str.maketrans('bpfvcksgjqxzdtlmnr', '112233344555667889')

    def transform(self, word):
        word = self._hw_replacement.sub('', word)
        return self._use_soundex_algorithm(word)


class RussianSoundex(Soundex):
    _vowels = 'аэиоуыеёюя'
    _table = str.maketrans('бпвфгкхдтжшчщзсцлмнр', '11223334455556667889')

    _replacement_map = {
        re.compile(r'(^|ъ|ь|' + r'|'.join(_vowels) + r')(я)', re.IGNORECASE): 'jа',
        re.compile(r'(^|ъ|ь|' + r'|'.join(_vowels) + r')(ю)', re.IGNORECASE): 'ju',
        re.compile(r'(^|ъ|ь|' + r'|'.join(_vowels) + r')(е)', re.IGNORECASE): 'jэ',
        re.compile(r'(^|ъ|ь|' + r'|'.join(_vowels) + r')(ё)', re.IGNORECASE): 'jо',
        re.compile(r'й', re.IGNORECASE): 'j',
        re.compile(r'[ъь]', re.IGNORECASE): '',
        re.compile(r'([тсзжцчшщ])([жцчшщ])', re.IGNORECASE): r'\2'
    }

    def transform(self, word):
        for replace, result in self._replacement_map.items():
            word = replace.sub(result, word)
        return self._use_soundex_algorithm(word)


class SoundexSimilarity:
    def __init__(self):
        self.soundex_converter = Soundex()

    def similarity(self, word1, word2):
        w1, w2 = self.soundex_converter.transform(word1), self.soundex_converter.transform(word2)
        table = self.soundex_converter.get_table()
        if w1[0].translate(table) == w2[0].translate(table):
            return eval(w1[1:], w2[1:])
        return eval(w1, w2)


if __name__ == '__main__':
    en_soundex = EnglishSoundex()
    ru_soundex = RussianSoundex()
    assert ru_soundex.transform('ёлочка') == 'J070530'
    assert ru_soundex.transform('ёлочка') == ru_soundex.transform('йолочка')
    assert ru_soundex.transform('девчонка') == ru_soundex.transform('девчёнка')
    assert ru_soundex.transform('шчастье') == ru_soundex.transform('счастье')
    assert ru_soundex.transform('считать') == 'Ч0404'
    assert ru_soundex.transform('щитать') == 'Щ0404'
