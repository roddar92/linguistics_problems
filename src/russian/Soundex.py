import re
from abc import ABC, abstractmethod
from editdistance import eval


class Soundex(ABC):
    _vowels = ''
    _table = str.maketrans('', '')

    def __init__(self, delete_first_letter=False, delete_first_coded_letter=False,
                 delete_zeros=False, cut_result=False, seq_cutted_len=4):
        self.delete_first_letter = delete_first_letter
        self.delete_first_coded_letter = delete_first_coded_letter
        self.delete_zeros = delete_zeros
        self.cut_result = cut_result
        self.seq_cutted_len = seq_cutted_len

    def _is_vowel(self, letter):
        return letter in self._vowels

    def _translate_vowels(self, word):
        return ''.join('0' if self._is_vowel(letter) else letter for letter in word)

    def _use_soundex_algorithm(self, word):
        word = word.lower()
        first, last = word[0], word
        last = last.translate(self._table)
        last = self._translate_vowels(last)
        last = re.sub('(0+)', '0', last)
        last = re.sub(r'(\w)(\1)+', r'\1', last)
        if self.delete_zeros:
            last = re.sub('(0+)', '', last)
            last = re.sub(r'(\w)(\1)+', r'\1', last)
        if self.cut_result:
            last = last[:self.seq_cutted_len] if len(last) >= self.seq_cutted_len else last
            last += ('0' * (self.seq_cutted_len - len(last)))
        if self.delete_first_coded_letter:
            last = last[1:]
        first_char = '' if self.delete_first_letter else first.capitalize()
        return first_char + last.upper()

    def get_vowels(self):
        return self._vowels

    def is_delete_first_coded_letter(self):
        return self.delete_first_coded_letter

    def is_delete_first_letter(self):
        return self.delete_first_letter

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
        re.compile(r'([тсзжцчшщ])([жцчшщ])', re.IGNORECASE): r'\2',
        re.compile(r'([лнс])(т)([лнс])', re.IGNORECASE): r'\1\3',
        re.compile(r'([дт][зс])', re.IGNORECASE): 'ц',
        re.compile(r'(р)(д)(ц)', re.IGNORECASE): r'\1\3',
        re.compile(r'(л)(н)(ц)', re.IGNORECASE): r'\2\3',
        re.compile(r'[ъь]', re.IGNORECASE): '',
    }

    def transform(self, word):
        for replace, result in self._replacement_map.items():
            word = replace.sub(result, word)
        return self._use_soundex_algorithm(word)


class SoundexSimilarity:
    def __init__(self, soundex):
        self.soundex_converter = soundex

    def similarity(self, word1, word2):
        w1, w2 = self.soundex_converter.transform(word1), self.soundex_converter.transform(word2)
        if self.soundex_converter.is_delete_first_letter():
            return eval(w1, w2)
        return eval(w1[1:], w2[1:])


if __name__ == '__main__':
    en_soundex = EnglishSoundex(delete_first_coded_letter=True, cut_result=True, delete_zeros=True)
    assert en_soundex.transform('Robert') == 'R196'
    assert en_soundex.transform('Rubin') == 'R180'
    assert en_soundex.transform('Rupert') == en_soundex.transform('Robert')
    assert en_soundex.transform('Ashcraft') == 'A926'
    assert en_soundex.transform('Ashcraft') == en_soundex.transform('Ashcroft')
    assert en_soundex.transform('Tymczak') == 'T835'

    ru_soundex = RussianSoundex()
    assert ru_soundex.transform('ёлочка') == 'JJ070530'
    assert ru_soundex.transform('ёлочка') == ru_soundex.transform('йолочка')
    assert ru_soundex.transform('кот') == ru_soundex.transform('код')
    assert ru_soundex.transform('медь') == ru_soundex.transform('меть')
    assert ru_soundex.transform('девчонка') == ru_soundex.transform('девчёнка')
    assert ru_soundex.transform('детский') == ru_soundex.transform('децкий')
    assert ru_soundex.transform('воротца') == ru_soundex.transform('вороца')
    assert ru_soundex.transform('шчастье') == ru_soundex.transform('счастье')
    assert ru_soundex.transform('том') == ru_soundex.transform('тон')
    assert ru_soundex.transform('щастье') == 'Щ5064J0'
    assert ru_soundex.transform('счастье') == 'Ч5064J0'
    assert ru_soundex.transform('агенство') == ru_soundex.transform('агентство')
    assert ru_soundex.transform('театр') == ru_soundex.transform('тятр')
    assert ru_soundex.transform('ненасный') == ru_soundex.transform('ненастный')
    assert ru_soundex.transform('сонце') == ru_soundex.transform('солнце')
    assert ru_soundex.transform('серце') == ru_soundex.transform('сердце')
    assert ru_soundex.transform('считать') == 'Ч50404'
    assert ru_soundex.transform('щитать') == 'Щ50404'

    ru_soundex = RussianSoundex(delete_first_letter=True)
    similarity_checker = SoundexSimilarity(ru_soundex)
    assert similarity_checker.similarity('щастье', 'счастье') == 0
    assert similarity_checker.similarity('считать', 'щитать') == 0
    assert similarity_checker.similarity('зуд', 'суд') == 0
    assert similarity_checker.similarity('мощь', 'мочь') == 0
    assert similarity_checker.similarity('ночь', 'мочь') == 0
    assert similarity_checker.similarity('сахар', 'цукер') == 0
    assert similarity_checker.similarity('булочная', 'булошная') == 0
    assert similarity_checker.similarity('мальчёнка', 'мальчонка') == 0
