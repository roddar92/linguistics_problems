# -*- coding: utf-8 -*-
import re
import string

from src.russian.NaiveTokenizer import NaiveTokenizer
from src.russian.SpellChecker import StatisticalSpeller


class Transliterator:

    def __init__(self, need_spell=False):

        self.phonemes = {
            'я': ['ya', 'ia', 'ja'],
            'ю': ['yu', 'ju'],
            'э': ['ae'],
            'б': ['b'],
            'в': ['v', 'w'],
            'д': ['d'],
            'п': ['p'],
            'и': ['i'],
            'о': ['o'],
            'e': ['е'],
            'ё': ['yo', 'jo'],
            'з': ['z'],
            'й': ['j'],
            'л': ['l'],
            'м': ['m'],
            'н': ['n'],
            'а': ['a'],
            'у': ['u'],
            'ф': ['f', 'ph'],
            'х': ['kh', 'h'],
            'ц': ['ts', 'tc', 'tz', 'c'],
            'ч': ['ch'],
            'ш': ['sh'],
            'щ': ['shch', 'sch', 'shh'],
            'ж': ['zh', 'jj'],
            'к': ['k', 'ck'],
            'г': ['g'],
            'ь': ['\''],
            'ъ': ['#'],
            'р': ['r'],
            'с': ['s'],
            'т': ['t'],
            'ы': ['y']
        }

        self.need_spell = need_spell
        self.tokenizer = None
        self.spell_checker = None

        if need_spell:
            self.tokenizer = NaiveTokenizer()
            self.spell_checker = StatisticalSpeller()

        for phoneme in self.phonemes.copy():
            self.phonemes[phoneme.upper()] = [phonem.capitalize() for phonem in self.phonemes[phoneme]]

        self.straight_phonemes = {k: v[0] for k, v in self.phonemes.items()}
        self.inverted_phonemes = {t: k for k, v in self.phonemes.items() for t in v}

        self.inverted_phonemes['x'] = 'кс'
        self.inverted_phonemes['iy'] = 'ый'

        self.keys = str.maketrans(self.straight_phonemes)

    @staticmethod
    def is_vowel(character):
        return character.lower() in 'аeёиоуыэюя'

    @staticmethod
    def simple_spell_euristic(word):
        word = re.sub(r'ця', 'тся', word, re.IGNORECASE)
        return word

    def transliterate(self, text):
        return text.translate(self.keys)

    def inverse_transliterate(self, text):
        elems = []
        i = 0
        while i < len(text):
            if i == len(text) - 1 or text[i + 1] in string.punctuation or text[i + 1].isspace():
                symbol = text[i]
                output_symbol = 'й' if symbol in 'iy' and self.is_vowel(elems[-1]) \
                    else self.inverted_phonemes[symbol] if text[i] in self.inverted_phonemes \
                    else symbol
                elems += [output_symbol]
                i += 1
            elif text[i:i + 4] in self.inverted_phonemes:
                elems += [self.inverted_phonemes[text[i:i + 4]]]
                i += 4
            elif text[i:i + 3] in self.inverted_phonemes:
                elems += [self.inverted_phonemes[text[i:i + 3]]]
                i += 3
            elif text[i:i + 2] in self.inverted_phonemes:
                if text[i:i + 2] in ['ij', 'iy']:
                    elems += ['ий' if re.search(r'[гджкцчшщ]$', elems[-1]) else self.inverted_phonemes[text[i:i + 2]]]
                else:
                    elems += [self.inverted_phonemes[text[i:i + 2]]]
                i += 2
            else:
                output_symbol = self.inverted_phonemes[text[i]] if text[i] in self.inverted_phonemes else text[i]
                elems += [output_symbol]
                i += 1

        res = ''.join(elems)
        if self.need_spell:
            # todo: add spell checker for this case
            '''
            elements = [
                self.spell_checker.rectify(token.Value) if token.Type == 'WORD' else token.Value
                for token in self.tokenizer.tokenize(res)
            ]
            res = ' '.join(elements)
            '''
            res = self.simple_spell_euristic(res)

        return res


if __name__ == '__main__':
    transliterator = Transliterator()
    assert transliterator.transliterate('я поймал бабочку') == 'ya pojmal babochku'
    assert transliterator.transliterate('Эти летние дожди!') == 'Aeti lеtniе dozhdi!'
    assert transliterator.transliterate('Железнодорожный романс') == 'Zhеlеznodorozhnyj romans'
    assert transliterator.inverse_transliterate('Neizbezhnyj') == 'Нeизбeжный'
    assert transliterator.inverse_transliterate('Shveciia') == 'Швeция'
    assert transliterator.inverse_transliterate('Tsarskoe Selo') == 'Царскоe Сeло'
    assert transliterator.inverse_transliterate('Sankt-Peterburg') == 'Санкт-Пeтeрбург'
    assert transliterator.inverse_transliterate('Aeti letnie dozhdi') == 'Эти лeтниe дожди'
    assert transliterator.inverse_transliterate('Nash zelyoniy mir') == 'Наш зeлёный мир'
    assert transliterator.inverse_transliterate('Nevskiy prospekt') == 'Нeвский проспeкт'
    assert transliterator.inverse_transliterate('Nickolay Petrowich') == 'Николай Пeтрович'
    assert transliterator.inverse_transliterate('Roschino') == 'Рощино'
    assert transliterator.inverse_transliterate('Roshchino') == 'Рощино'
    assert transliterator.inverse_transliterate('Frankophoniia') == 'Франкофония'
    assert transliterator.inverse_transliterate(
        'zelyonaja doska i xerox stoyat ryadom') == 'зeлёная доска и ксeрокс стоят рядом'

    # todo: try to implement HMM (Hidden Markov Model)
    transliterator = Transliterator(need_spell=True)
    assert transliterator.inverse_transliterate(
        'Andrey, Arsenii, Nikolaj sobirajutsia v Dubai') == 'Андрeй, Арсeний, Николай собираются в Дубай'
