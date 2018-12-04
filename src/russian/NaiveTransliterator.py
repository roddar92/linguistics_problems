# -*- coding: utf-8 -*-
import re
import string

# from src.russian.NaiveTokenizer import NaiveTokenizer
# from src.russian.SpellChecker import StatisticalSpeller


class Transliterator:

    def __init__(self, need_spell=False):

        self.SHCH_EXCEPTIONS = [
            'бекешчаба',
            'веснушчатость',
            'вeснушчатый',
            'кошчи',
            'пушчонка',
            'сиводушчатый',
            'харишчандра',
            'черешчатый'
        ]

        self.RU_VOWELS = 'аeёиоуыэюя'
        self.AFFIXES = re.compile(
            r'(^|\s+)(pod|raz|iz|pred|ot|ob|bez|in|trans|(sver|dvu|tr([yj][ёo]|ё))k?h)$',
            re.IGNORECASE
        )
        self.E_AFFIX = re.compile(r'(^|\s+)[Ss]$', re.IGNORECASE)
        self.CH_START_REGEX = re.compile(r'(^|\s+)ch$', re.IGNORECASE)
        self.CH_END_REGEX = re.compile(r'^ch($|\s+|' +
                                       r'|'.join(['\\' + punct for punct in string.punctuation]) +
                                       r')', re.IGNORECASE)

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
            'щ': ['shh', 'šč', 'ŝ'],
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
            pass
            # self.tokenizer = NaiveTokenizer()
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

    def _is_shch_exceptions(self, word):
        return word in self.SHCH_EXCEPTIONS

    @staticmethod
    def is_solid_or_soft_sign(letter):
        return letter in 'ъь'

    def _has_s_affix(self, text, i):
        return text[i:i + 2] in ['ie', 'ye', 'je'] and self.E_AFFIX.search(text[:i])

    def _transliterate_ij_ending(self, text, elems, i):
        symbol = text[i]
        if symbol in 'i' and self._is_vowel(elems[-1]):
            return 'й'
        elif text[i] in self.inverted_phonemes:
            return self.inverted_phonemes[symbol]
        else:
            return symbol

    def _tranliterate_vowels_sequence(self, text, answer, elems, i):
        if i == 0 or self._is_vowel(elems[-1]) or not elems[-1].isalpha() or elems[-1] == 'ь':
            return self.inverted_phonemes[text[i:i + 2]]
        elif i > 0 and not self._is_vowel(text[i - 1]) and \
                (self._starts_with_affix(text[:i]) or self._has_s_affix(text, i)):
            return 'ъ' + self.inverted_phonemes[text[i:i + 2]]
        else:
            return answer

    def _transliterate_ch_sequence(self, text, i):
        if text[i + 2:].startswith('ro'):
            return 'х' if text[i:i + 2].islower() else 'Х'
        elif text[i + 2:].startswith('ri'):
            return 'к' if text[i:i + 2].islower() else 'К'
        else:
            return self.inverted_phonemes[text[i:i + 2]]

    def _transliterate_ch_end_sequence(self, text, elems, i, is_upper):
        if ''.join(elems[-2:]) in ['ви', 'ны'] and is_upper == 1:
            return self.inverted_phonemes[text[i:i + 2]]
        elif elems[-1] in 'иы':
            return 'х'
        else:
            return 'ч'

    def _transliterate_vowel_ending(self, text, elems, i):
        return 'ий' if re.search(r'[гджкцчшщ]$', elems[-1]) else self.inverted_phonemes[text[i:i + 2]]

    def transliterate_two_letter_sequence(self, text, elems, i, is_upper):
        if self.CH_START_REGEX.search(text[:i + 2]):
            res = self._transliterate_ch_sequence(text, i)
        elif self.CH_END_REGEX.search(text[i:]):
            res = self._transliterate_ch_end_sequence(text, elems, i, is_upper)
        elif text[i:i + 2].lower() in ['ia', 'ya', 'ja', 'ie', 'ye', 'je', 'yu', 'iu', 'ju']:
            answer = self.COMBINATED_PHONEMES[text[i:i + 2]] \
                if text[i:i + 2] in ['ie', 'ye', 'je'] else self.inverted_phonemes[text[i:i + 2]]
            res = self._tranliterate_vowels_sequence(text, answer, elems, i)
        elif text[i:i + 2].lower() in ['ij', 'iy', 'yi', 'yj'] and not text[i + 2].isalnum():
            res = self._transliterate_vowel_ending(text, elems, i)
        elif text[i:i + 2].lower() in ['ij', 'iy', 'yi', 'yj']:
            res = self.inverted_phonemes[text[i:i + 1]]
            i -= 1
        else:
            res = self.inverted_phonemes[text[i:i + 2]]
        return res, i

    def _is_vowel(self, character):
        return character.lower() in self.RU_VOWELS

    def _starts_with_affix(self, text):
        return self.AFFIXES.search(text)

    def simple_spell_euristic(self, word):
        if not self._is_shch_exceptions(word):
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
                elems += [self._transliterate_ij_ending(text, elems, i)]
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
                answer, i = self.transliterate_two_letter_sequence(text, elems, i, is_upper)
                elems += answer
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
    translit = Transliterator()
    assert translit.transliterate('я поймал бабочку') == 'ya pojmal babochku'
    assert translit.transliterate('Эти летние дожди!') == 'Aeti lеtniе dozhdi!'
    assert translit.transliterate('Железнодорожный романс') == 'Zhеlеznodorozhnyj romans'

    assert translit.inverse_transliterate('Neizbezhnyj') == 'Нeизбeжный'
    assert translit.inverse_transliterate('Shveciia') == 'Швeция'
    assert translit.inverse_transliterate('Tsarskoe Selo') == 'Царскоe Сeло'
    assert translit.inverse_transliterate('Sankt-Peterburg') == 'Санкт-Пeтeрбург'
    assert translit.inverse_transliterate('Aeti letnie dozhdi') == 'Эти лeтние дожди'
    assert translit.inverse_transliterate('Nash zelyoniy mir') == 'Наш зeлёный мир'
    assert translit.inverse_transliterate('Nevskiy prospekt') == 'Нeвский проспeкт'
    assert translit.inverse_transliterate('Nickolay Petrowich') == 'Николай Пeтрович'
    assert translit.inverse_transliterate('Idi, Yaandreyev, urok otvechat\'!') == 'Иди, Яандрeeв, урок отвeчать!'
    assert translit.inverse_transliterate('schyot') == 'счёт'
    assert translit.inverse_transliterate(
        'Iezhi i jojjonok jeli žyrniy yogurt') == 'Eжи и ёжонок eли жирный йогурт'
    assert translit.inverse_transliterate('ulitsa Yefimova') == 'улица Eфимова'
    assert translit.inverse_transliterate('ah, ėti chyornye glaza!') == 'ах, эти чёрные глаза!'
    assert translit.inverse_transliterate('Roshchino') == 'Рощино'
    assert translit.inverse_transliterate('slavnyi soldat Shvejk') == 'славный солдат Швeйк'
    assert translit.inverse_transliterate('Frankophoniia') == 'Франкофония'
    assert translit.inverse_transliterate('aqualangisty') == 'аквалангисты'
    assert translit.inverse_transliterate('leyka') == 'лeйка'
    assert translit.inverse_transliterate('schast\'ye') == 'счастьe'
    assert translit.inverse_transliterate('vesnushchatyi') == 'вeснушчатый'
    assert translit.inverse_transliterate('znanija') == 'знания'
    assert translit.inverse_transliterate('shhuka plyvyot k shkhune') == 'щука плывёт к шхунe'
    assert translit.inverse_transliterate('ploshchad\' Alexandra Pushkina') == 'площадь Алeксандра Пушкина'
    assert translit.inverse_transliterate('Chris i Chrom') == 'Крис и Хром'
    assert translit.inverse_transliterate('kotorych, strojnych, San Sanych') == 'которых, стройных, Сан Саныч'
    assert translit.inverse_transliterate('palach') == 'палач'
    assert translit.inverse_transliterate('Siezd k Syamozeru') == 'Съeзд к Сямозeру'
    assert translit.inverse_transliterate(
        'moi podiezd, i ya vyiezzhayu s Bolshoy Podyacheskoj na orientirovanie') == \
        'мой подъeзд, и я выeзжаю с Болшой Подъячeской на ориентирование'
    assert translit.inverse_transliterate(
        'zelyonaja doska i xerox stoyat ryadom') == 'зeлёная доска и ксeрокс стоят рядом'
    assert translit.inverse_transliterate(
        'Andrey, Arsenii, Nikolaj sobirajutsia v Dubai') == 'Андрeй, Арсeний, Николай собираются в Дубай'
    assert translit.inverse_transliterate(
        'tscheslavniy i tshcheslavnij khodjat paroj') == 'тщeславный и тщeславный ходят парой'
