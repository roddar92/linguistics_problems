# -*- coding: utf-8 -*-
import re
import string

from src.russian.NaiveTokenizer import NaiveTokenizer
# from src.russian.SpellChecker import StatisticalSpeller


class Transliterator:

    def __init__(self, need_spell=False):

        self.RU_VOWELS = 'аeёиоуыэюя'
        self.AFFIXES = re.compile(
            r'(^|\s+)(pod|raz|iz|pred|ot|ob|bez|in|trans|(sver|dvu|tr([yj][ёo]|ё))k?h)$',
            re.IGNORECASE
        )
        self.E_AFFIX = re.compile(r'(^|\s+)[Ss]$', re.IGNORECASE)
        self.CH_START_REGEX = re.compile(r'(^|\s+)ch$', re.IGNORECASE)
        self.CH_END_REGEX = re.compile(r'^ch($|\s+|\W)', re.IGNORECASE)

        self.PHONEMES = {
            'я': ['ya', 'ia', 'ja', 'â'],
            'ю': ['yu', 'iu', 'ju', 'û'],
            'э': ['ae', 'ė'],
            'б': ['b'],
            'в': ['v', 'w'],
            'д': ['d'],
            'п': ['p'],
            'и': ['i'],
            'о': ['o'],
            'e': ['е', 'ie', 'je', 'ye'],
            'ё': ['yo', 'jo', 'yë', 'ë'],
            'з': ['z'],
            'й': ['j'],
            'л': ['l'],
            'м': ['m'],
            'н': ['n'],
            'а': ['a'],
            'у': ['u'],
            'ф': ['f', 'ph'],
            'х': ['kh', 'h'],
            'ц': ['ts', 'tc', 'tz', 'c', 'cz'],
            'ч': ['ch', 'č'],
            'ш': ['sh', 'š'],
            'щ': ['shch', 'shh', 'šč', 'ŝ'],
            'ж': ['zh', 'jj', 'ž'],
            'к': ['k', 'ck'],
            'г': ['g'],
            'ь': ['\''],
            'ъ': ['#'],
            'р': ['r'],
            'с': ['s'],
            'т': ['t'],
            'ы': ['y']
        }

        self.COMPLEX_PHONEMES = {
            'jog': ['й', 'о', 'г'],
            'yog': ['й', 'о', 'г'],
            'tch': ['т', 'ч'],
            'tsh': ['т', 'ш']
        }

        self.UNCORRECTED_PHONEMES = {
            re.compile(r'ця', re.IGNORECASE): 'тся',
            re.compile(r'цч', re.IGNORECASE): 'тщ',
            re.compile(r'шч', re.IGNORECASE): 'щ',
            re.compile(r'([жш])(ы)', re.IGNORECASE): r'\1и',
            re.compile(r'([' + self.RU_VOWELS + r'])ы', re.IGNORECASE): r'\1й',
            re.compile(r'([чщ])(я)', re.IGNORECASE): r'\1а',
            re.compile(r'([чщ])(ю)', re.IGNORECASE): r'\1у'
        }

        self.COMBINATED_PHONEMES = {
            'ie': 'ие',
            'je': 'ье',
            'ye': 'ые'
        }

        self.need_spell = need_spell
        self.tokenizer = None
        self.spell_checker = None

        if need_spell:
            self.tokenizer = NaiveTokenizer()
            # self.spell_checker = StatisticalSpeller()

        for phoneme in self.PHONEMES.copy():
            if not self.is_solid_or_soft_sign(phoneme):
                self.PHONEMES[phoneme.capitalize()] = [ph.capitalize() for ph in self.PHONEMES[phoneme]]

        self.straight_phonemes = {k: v[0] for k, v in self.PHONEMES.items()}
        self.inverted_phonemes = {t: k for k, v in self.PHONEMES.items() for t in v}

        self.inverted_phonemes['x'] = 'кс'
        self.inverted_phonemes['qu'] = 'кв'
        self.inverted_phonemes['iy'] = 'ый'
        self.inverted_phonemes['ij'] = 'ый'

        self.inverted_phonemes.update(self.COMPLEX_PHONEMES)

        self.keys = str.maketrans(self.straight_phonemes)

    @staticmethod
    def is_solid_or_soft_sign(letter):
        return letter in 'ъь'

    def is_vowel(self, character):
        return character.lower() in self.RU_VOWELS

    def starts_with_affix(self, text):
        return self.AFFIXES.search(text)

    def simple_spell_euristic(self, word):
        for phoneme, replaced in self.UNCORRECTED_PHONEMES.items():
            word = phoneme.sub(replaced, word, re.IGNORECASE)
        return word

    def transliterate(self, text):
        return text.translate(self.keys)

    def inverse_transliterate(self, text):
        elems = []
        i = 0
        is_upper = 0

        while i < len(text):
            if i == 0 or text[i - 1].isspace() or text[i - 1] in string.punctuation:
                is_upper = 1 if text[i].isupper() else 0

            if i == len(text) - 1 or text[i + 1] in string.punctuation or text[i + 1].isspace():
                symbol = text[i]
                output_symbol = 'й' if symbol in 'i' and self.is_vowel(elems[-1]) \
                    else self.inverted_phonemes[symbol] if text[i] in self.inverted_phonemes \
                    else symbol
                elems += [output_symbol]
                i += 1
            elif i + 4 <= len(text) and text[i:i + 4] in self.inverted_phonemes:
                phoneme = self.inverted_phonemes[text[i:i + 4]]
                elems += [phoneme] if isinstance(phoneme, str) else phoneme
                i += 4
            elif i + 3 <= len(text) and text[i:i + 3] in self.inverted_phonemes:
                phoneme = self.inverted_phonemes[text[i:i + 3]]
                elems += [phoneme] if isinstance(phoneme, str) else phoneme
                i += 3
            elif i + 2 <= len(text) and text[i:i + 2] in self.inverted_phonemes:
                if self.CH_START_REGEX.search(text[:i + 2]):
                    if text[i + 2:].startswith('ro'):
                        elems += ['х' if text[i:i + 2].islower() else 'Х']
                    elif text[i + 2:].startswith('ri'):
                        elems += ['к' if text[i:i + 2].islower() else 'К']
                    else:
                        elems += [self.inverted_phonemes[text[i:i + 2]]]
                elif self.CH_END_REGEX.search(text[i:]):
                    if ''.join(elems[-2:]) in ['ви', 'ны'] and is_upper == 1:
                        elems += [self.inverted_phonemes[text[i:i + 2]]]
                    elif elems[-1] in 'иы':
                        elems += ['х']
                    else:
                        elems += ['ч']
                elif text[i:i + 2].lower() in ['ia', 'ya', 'ja', 'ie', 'ye', 'je', 'yu', 'iu', 'ju']:
                    answer = self.COMBINATED_PHONEMES[text[i:i + 2]] \
                        if text[i:i + 2] in ['ie', 'ye', 'je'] else self.inverted_phonemes[text[i:i + 2]]
                    elems += [self.inverted_phonemes[text[i:i + 2]]
                              if i == 0 or self.is_vowel(elems[-1]) or not elems[-1].isalpha()
                              else 'ъ' + self.inverted_phonemes[text[i:i + 2]]
                              if i > 0 and not self.is_vowel(text[i - 1]) and (self.starts_with_affix(text[:i])
                              or (text[i:i + 2] in ['ie', 'ye', 'je'] and self.E_AFFIX.search(text[:i])))
                              else answer]
                elif text[i:i + 2].lower() in ['ij', 'iy', 'yi', 'yj'] and not text[i + 2].isalnum():
                    elems += ['ий' if re.search(r'[гджкцчшщ]$', elems[-1]) else self.inverted_phonemes[text[i:i + 2]]]
                elif text[i:i + 2].lower() in ['ij', 'iy', 'yi', 'yj']:
                    elems += [self.inverted_phonemes[text[i:i + 1]]]
                    i -= 1
                else:
                    elems += [self.inverted_phonemes[text[i:i + 2]]]
                i += 2
            else:
                output_symbol = self.inverted_phonemes[text[i]] if text[i] in self.inverted_phonemes else text[i]
                elems += [output_symbol]
                i += 1

        res = ''.join(elems)
        res = self.simple_spell_euristic(res)

        if self.need_spell:
            pass
            # todo: add spell checker for this case
            '''
            elements = [
                self.spell_checker.rectify(token.Value) if token.Type == 'WORD' else token.Value
                for token in self.tokenizer.tokenize(res)
            ]
            res = ' '.join(elements)
            '''

        return res


if __name__ == '__main__':
    # todo: try to implement HMM (Hidden Markov Model)
    transliterator = Transliterator()
    assert transliterator.transliterate('я поймал бабочку') == 'ya pojmal babochku'
    assert transliterator.transliterate('Эти летние дожди!') == 'Aeti lеtniе dozhdi!'
    assert transliterator.transliterate('Железнодорожный романс') == 'Zhеlеznodorozhnyj romans'

    assert transliterator.inverse_transliterate('Neizbezhnyj') == 'Нeизбeжный'
    assert transliterator.inverse_transliterate('Shveciia') == 'Швeция'
    assert transliterator.inverse_transliterate('Tsarskoe Selo') == 'Царскоe Сeло'
    assert transliterator.inverse_transliterate('Sankt-Peterburg') == 'Санкт-Пeтeрбург'
    assert transliterator.inverse_transliterate('Aeti letnie dozhdi') == 'Эти лeтние дожди'
    assert transliterator.inverse_transliterate('Nash zelyoniy mir') == 'Наш зeлёный мир'
    assert transliterator.inverse_transliterate('Nevskiy prospekt') == 'Нeвский проспeкт'
    assert transliterator.inverse_transliterate('Nickolay Petrowich') == 'Николай Пeтрович'
    assert transliterator.inverse_transliterate('Idi, Yaandreyev, urok otvechat\'!') == 'Иди, Яандрeeв, урок отвeчать!'
    assert transliterator.inverse_transliterate('schyot') == 'счёт'
    assert transliterator.inverse_transliterate(
        'Iezhi i jojjonok jeli žyrniy yogurt') == 'Eжи и ёжонок eли жирный йогурт'
    assert transliterator.inverse_transliterate('ulitsa Yefimova') == 'улица Eфимова'
    assert transliterator.inverse_transliterate('ah, ėti chyornye glaza!') == 'ах, эти чёрные глаза!'
    assert transliterator.inverse_transliterate('Roshchino') == 'Рощино'
    assert transliterator.inverse_transliterate('slavnyi soldat Shvejk') == 'славный солдат Швeйк'
    assert transliterator.inverse_transliterate('Frankophoniia') == 'Франкофония'
    assert transliterator.inverse_transliterate('aqualangisty') == 'аквалангисты'
    assert transliterator.inverse_transliterate('leyka') == 'лeйка'
    assert transliterator.inverse_transliterate('znanija') == 'знания'
    assert transliterator.inverse_transliterate('shhuka plyvyot k shkhune') == 'щука плывёт к шхунe'
    assert transliterator.inverse_transliterate('ploshchad\' Alexandra Pushkina') == 'площадь Алeксандра Пушкина'
    assert transliterator.inverse_transliterate('Chris i Chrom') == 'Крис и Хром'
    assert transliterator.inverse_transliterate('kotorych, strojnych, San Sanych') == 'которых, стройных, Сан Саныч'
    assert transliterator.inverse_transliterate('palach') == 'палач'
    assert transliterator.inverse_transliterate('Siezd k Syamozeru') == 'Съeзд к Сямозeру'
    assert transliterator.inverse_transliterate(
        'moi podiezd, i ya vyiezzhayu s Bolshoy Podyacheskoj na orientirovanie') == \
        'мой подъeзд, и я выeзжаю с Болшой Подъячeской на ориентирование'
    assert transliterator.inverse_transliterate(
        'zelyonaja doska i xerox stoyat ryadom') == 'зeлёная доска и ксeрокс стоят рядом'
    assert transliterator.inverse_transliterate(
        'Andrey, Arsenii, Nikolaj sobirajutsia v Dubai') == 'Андрeй, Арсeний, Николай собираются в Дубай'
    assert transliterator.inverse_transliterate(
        'tscheslavniy i tshcheslavnij khodjat paroj') == 'тщeславный и тщeславный ходят парой'
