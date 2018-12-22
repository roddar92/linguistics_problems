import re
from abc import ABC, abstractmethod
import editdistance
import pymorphy2


class Soundex(ABC):
    _vowels = ''
    _table = str.maketrans('', '')
    _reduce_regex = re.compile(r'(\w)(\1)+', re.IGNORECASE)
    _vowels_regex = re.compile(r'(0+)', re.IGNORECASE)

    def __init__(self, delete_first_letter=False, delete_first_coded_letter=False,
                 delete_zeros=False, cut_result=False, seq_cutted_len=4):
        """
        Initialization of Soundex object
        :param delete_first_letter: remove the first letter from the result code (A169 -> 169)
        :param delete_first_coded_letter: remove the first coded letter from the result code (A5169 -> A169)
        :param delete_zeros: remove vowels from the result code
        :param cut_result: cut result core till N symbols
        :param seq_cutted_len: length of the result code
        """
        self.delete_first_letter = delete_first_letter
        self.delete_first_coded_letter = delete_first_coded_letter
        self.delete_zeros = delete_zeros
        self.cut_result = cut_result
        self.seq_cutted_len = seq_cutted_len

    def _is_vowel(self, letter):
        return letter in self._vowels

    def _reduce_seq(self, seq):
        return self._reduce_regex.sub(r'\1', seq)

    def _translate_vowels(self, word):
        return ''.join('0' if self._is_vowel(letter) else letter for letter in word)

    def _remove_paired_sounds(self, seq, replace=''):
        seq = self._vowels_regex.sub(replace, seq)
        seq = self._reduce_seq(seq)
        return seq

    def _apply_soundex_algorithm(self, word):
        word = word.lower()
        first, last = word[0], word
        last = last.translate(self._table)
        last = self._translate_vowels(last)
        last = self._remove_paired_sounds(last, replace='0')
        if self.delete_zeros:
            last = self._remove_paired_sounds(last)
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
        """
        Converts a given word th Soundex code
        :param word: string
        :return: Soundex string code
        """
        return None


class EnglishSoundex(Soundex):
    _hw_replacement = re.compile(r'[hw]', re.IGNORECASE)

    _vowels = 'aeiouy'
    _table = str.maketrans('bpfvcksgjqxzdtlmnr', '112233344555667889')

    def transform(self, word):
        word = self._hw_replacement.sub('', word)
        return self._apply_soundex_algorithm(word)


class RussianSoundex(Soundex):
    _vowels = 'аэиоуыеёюя'
    _table = str.maketrans('бпвфгкхдтжшчщзсцлмнр', '11223334455556667889')
    _ego_ogo_endings = re.compile(r'([ео])(г)(о$)', re.IGNORECASE)

    _replacement_map = {
        re.compile(r'(^|ъ|ь|' + r'|'.join(_vowels) + r')(я)', re.IGNORECASE): 'jа',
        re.compile(r'(^|ъ|ь|' + r'|'.join(_vowels) + r')(ю)', re.IGNORECASE): 'jу',
        re.compile(r'(^|ъ|ь|' + r'|'.join(_vowels) + r')(е)', re.IGNORECASE): 'jэ',
        re.compile(r'(^|ъ|ь|' + r'|'.join(_vowels) + r')(ё)', re.IGNORECASE): 'jо',
        re.compile(r'й', re.IGNORECASE): 'j',
        re.compile(r'([тсзжцчшщ])([жцчшщ])', re.IGNORECASE): r'\2',
        re.compile(r'(с)(т)([лнц])', re.IGNORECASE): r'\1\3',
        re.compile(r'(н)([тд])(ств)', re.IGNORECASE): r'\1\3',
        re.compile(r'([нс])([тд])(ск)', re.IGNORECASE): r'\1\3',
        re.compile(r'(р)(д)([чц])', re.IGNORECASE): r'\1\3',
        re.compile(r'(з)(д)([нц])', re.IGNORECASE): r'\1\3',
        re.compile(r'(в)(ств)', re.IGNORECASE): r'\2',
        re.compile(r'(л)(нц)', re.IGNORECASE): r'\2',
        re.compile(r'[ъь]', re.IGNORECASE): '',
        re.compile(r'([дт][зсц])', re.IGNORECASE): 'ц'
    }

    def __init__(self, delete_first_letter=False, delete_first_coded_letter=False,
                 delete_zeros=False, cut_result=False, seq_cutted_len=4,
                 use_morph_analysis=False):
        """
        Initialization of Russian Soundex object
        :param delete_first_letter:
        :param delete_first_coded_letter:
        :param delete_zeros:
        :param cut_result:
        :param seq_cutted_len:
        :param use_morph_analysis: use morphological grammems for phonemes analysis
        """
        super(RussianSoundex, self).__init__(delete_first_letter, delete_first_coded_letter,
                         delete_zeros, cut_result, seq_cutted_len)
        self.use_morph_analysis = use_morph_analysis
        self._moprh = pymorphy2.MorphAnalyzer()

    def _replace_ego_ogo_endings(self, word):
        return self._ego_ogo_endings.sub(r'\1в\3', word)

    def _use_morph_for_phoneme_replace(self, word):
        parse = self._moprh.parse(word)
        if parse and ('ADJF' in parse[0].tag or 'NUMB' in parse[0].tag or 'NPRO' in parse[0].tag):
            word = self._replace_ego_ogo_endings(word)
        return word

    def transform(self, word):
        if self.use_morph_analysis:
            word = self._use_morph_for_phoneme_replace(word)
        for replace, result in self._replacement_map.items():
            word = replace.sub(result, word)
        return self._apply_soundex_algorithm(word)


class SoundexSimilarity:
    def __init__(self, soundex, metrics=editdistance.eval):
        """
        Init a similarity object
        :param soundex: an object of Soundex class
        :param metrics: similarity function, optional, default is Levenstein distance
        """
        self.soundex_converter = soundex
        self.metrics = metrics

    def similarity(self, word1, word2):
        """
        Compute the similarity between Soundex codes
        :param word1: first original word
        :param word2: second original word
        :return: distance value
        """
        w1, w2 = self.soundex_converter.transform(word1), self.soundex_converter.transform(word2)
        if self.soundex_converter.is_delete_first_letter():
            return self.metrics(w1, w2)
        return self.metrics(w1[1:], w2[1:])


if __name__ == '__main__':
    en_soundex = EnglishSoundex(delete_first_coded_letter=True,
                                cut_result=True, delete_zeros=True)
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
    assert ru_soundex.transform('двацать') == ru_soundex.transform('двадцать')
    assert ru_soundex.transform('сница') == ru_soundex.transform('сниться')
    assert ru_soundex.transform('воротца') == ru_soundex.transform('вороца')
    assert ru_soundex.transform('гигантский') == ru_soundex.transform('гиганский')
    assert ru_soundex.transform('марксистский') == ru_soundex.transform('марксисский')
    assert ru_soundex.transform('чувствовать') == ru_soundex.transform('чуствовать')
    assert ru_soundex.transform('праздник') == ru_soundex.transform('празник')
    assert ru_soundex.transform('шчастье') == ru_soundex.transform('счастье')
    assert ru_soundex.transform('том') == ru_soundex.transform('тон')
    assert ru_soundex.transform('щастье') == 'Щ5064J0'
    assert ru_soundex.transform('счастье') == 'Ч5064J0'
    assert ru_soundex.transform('агенство') == ru_soundex.transform('агентство')
    assert ru_soundex.transform('театр') == ru_soundex.transform('тятр')
    assert ru_soundex.transform('сонце') == ru_soundex.transform('солнце')
    assert ru_soundex.transform('серце') == ru_soundex.transform('сердце')
    assert ru_soundex.transform('считать') == 'Ч50404'
    assert ru_soundex.transform('щитать') == 'Щ50404'

    ru_soundex = RussianSoundex(use_morph_analysis=True)
    assert ru_soundex.transform('зелёного') == 'З60708020'
    assert ru_soundex.transform('никого') == 'Н803020'
    assert ru_soundex.transform('ничего') == 'Н805020'
    assert ru_soundex.transform('много') == 'М8030'

    ru_soundex = RussianSoundex(delete_first_letter=True)
    similarity_checker = SoundexSimilarity(ru_soundex)
    assert similarity_checker.similarity('щастье', 'счастье') == 0
    assert similarity_checker.similarity('считать', 'щитать') == 0
    assert similarity_checker.similarity('зуд', 'суд') == 0
    assert similarity_checker.similarity('мощь', 'мочь') == 0
    assert similarity_checker.similarity('ночь', 'мочь') == 0
    assert similarity_checker.similarity('сахар', 'цукер') == 0
    assert similarity_checker.similarity('булочная', 'булошная') == 0
    assert similarity_checker.similarity('булочная', 'булошная') == 0
    assert similarity_checker.similarity('блеснуть', 'блестнуть') == 0
    assert similarity_checker.similarity('ненасный', 'ненастный') == 0
