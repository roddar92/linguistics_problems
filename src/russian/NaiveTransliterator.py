# -*- coding: utf-8 -*-
import re
import string

# from src.russian.NaiveTokenizer import NaiveTokenizer
# from src.russian.SpellChecker import StatisticalSpeller


class Transliterator:
    SHCH_EXCEPTIONS = [
        'бекешчаба',
        'веснушчатость',
        'вeснушчатый',
        'кошчи',
        'пушчонка',
        'сиводушчатый',
        'харишчандра',
        'черешчатый'
    ]

    IOT_VOWELS = ['io', 'jo', 'yo']
    IET_VOWELS = ['ie', 'ye', 'je']
    IAT_VOWELS = ['ia', 'ya', 'ja']
    IUT_VOWELS = ['iu', 'yu', 'ju']

    CH_AFTER_SEQ = {
        'ro': 'х',
        'ri': 'к'
    }

    def __init__(self, need_spell=False):
        self.__RU_VOWELS = 'аeёиоуыэюя'
        self.__AFFIXES = re.compile(
            r'(^|\s+)(pod|raz|iz|pred|ot|ob|bez|in|trans|(sver|dvu|tr([yj][ёo]|ё))k?h)$',
            re.IGNORECASE
        )
        self.__E_AFFIX = re.compile(r'(^|\s+)[Ss]$', re.IGNORECASE)
        self.__CH_START_REGEX = re.compile(r'(^|\s+)ch$', re.IGNORECASE)
        self.__CH_END_REGEX = re.compile(r'^ch($|\s+|[' + string.punctuation + r']+)', re.IGNORECASE)

        self.__PHONEMES = {
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

        self.__COMPLEX_PHONEMES = {
            'jog': ['й', 'о', 'г'],
            'yog': ['й', 'о', 'г'],
            'tch': ['т', 'ч'],
            'tsh': ['т', 'ш']
        }

        self.__UNCORRECTED_PHONEMES = {
            re.compile(r'ця', re.IGNORECASE): 'тся',
            re.compile(r'цч', re.IGNORECASE): 'тщ',
            re.compile(r'шч', re.IGNORECASE): 'щ',
            re.compile(r'([жш])(ы)', re.IGNORECASE): r'\1и',
            re.compile(r'([' + self.__RU_VOWELS + r'])ы', re.IGNORECASE): r'\1й',
            re.compile(r'([чщ])(я)', re.IGNORECASE): r'\1а',
            re.compile(r'([чщ])(ю)', re.IGNORECASE): r'\1у'
        }

        self.__COMBINATED_PHONEMES = {
            'ie': 'ие',
            'je': 'ье',
            'ye': 'ые'
        }

        self.__COMBINATED_E_PHONEMES = {
            'io': 'ио',
            'jo': 'йо',
            'yo': 'йо'
        }

        for phoneme, val in list(self.__COMBINATED_PHONEMES.items()):
            self.__COMBINATED_PHONEMES[phoneme.capitalize()] = val.capitalize()

        for phoneme, val in list(self.__COMBINATED_E_PHONEMES.items()):
            self.__COMBINATED_E_PHONEMES[phoneme.capitalize()] = val.capitalize()

        self.__need_spell = need_spell
        self.__tokenizer = None
        self.__spell_checker = None

        if self.__need_spell:
            pass
            # self.__tokenizer = NaiveTokenizer()
            # self.__spell_checker = StatisticalSpeller()

        for phoneme in self.__PHONEMES.copy():
            if not self.__is_solid_or_soft_sign(phoneme):
                self.__PHONEMES[phoneme.capitalize()] = [ph.capitalize() for ph in self.__PHONEMES[phoneme]]

        self.__straight_phonemes = {k: v[0] for k, v in self.__PHONEMES.items()}
        self.__inverted_phonemes = {t: k for k, v in self.__PHONEMES.items() for t in v}

        self.__inverted_phonemes['x'] = 'кс'
        self.__inverted_phonemes['qu'] = 'кв'
        self.__inverted_phonemes['iy'] = 'ый'
        self.__inverted_phonemes['ij'] = 'ый'

        self.__inverted_phonemes.update(self.__COMPLEX_PHONEMES)

        self.__keys = str.maketrans(self.__straight_phonemes)

    def __is_shch_exceptions(self, word):
        return word in self.SHCH_EXCEPTIONS

    @staticmethod
    def __is_solid_or_soft_sign(letter):
        return letter in 'ъь'

    @staticmethod
    def __is_of_word_start(elems, i):
        return i == 0 or not elems[-1].isalpha()

    def __has_s_affix(self, text, i):
        return text[i:i + 2] in ['ie', 'ye', 'je'] and self.__E_AFFIX.search(text[:i])

    def __iot_must_changed(self, text, i):
        return text[i:i + 2].lower() in self.IOT_VOWELS and text[i + 2] in 'tdga'
    
    def __starts_with_affix(self, text):
        return self.__AFFIXES.search(text)

    def __is_solid_sign_possible(self, text, i):
        return self.__starts_with_affix(text[:i]) or self.__has_s_affix(text, i)

    def __is_iot_combination(self, charseq):
        return charseq.lower() in self.IAT_VOWELS + self.IET_VOWELS + self.IUT_VOWELS + self.IOT_VOWELS

    def __is_vowel(self, character):
        return character.lower() in self.__RU_VOWELS

    def __transliterate_ij_ending(self, text, elems, i):
        symbol = text[i]
        if symbol == 'i' and self.__is_vowel(elems[-1]):
            return 'й'
        elif symbol in self.__inverted_phonemes:
            return self.__inverted_phonemes[symbol]
        else:
            return symbol

    def __transliterate_vowels_sequence(self, text, answer, elems, i):
        if self.__is_of_word_start(elems, i) or self.__is_vowel(elems[-1]) or elems[-1] == 'ь':
            if self.__is_of_word_start(elems, i) and self.__iot_must_changed(text, i):
                return self.__COMBINATED_E_PHONEMES[text[i:i + 2]]
            return self.__inverted_phonemes[text[i:i + 2]]
        elif (i > 0 or elems[-1].isalpha()) and text[i:i + 2].lower() in self.IOT_VOWELS:
                return self.__inverted_phonemes[text[i:i + 2]]
        elif i > 0 and not self.__is_vowel(elems[-1]) and self.__is_solid_sign_possible(text, i):
            return 'ъ' + self.__inverted_phonemes[text[i:i + 2]]
        else:
            return answer

    def __transliterate_ch_sequence(self, text, i):
        if i + 4 < len(text) and text[i + 2:i + 4] in self.CH_AFTER_SEQ:
            letter = self.CH_AFTER_SEQ[text[i + 2:i + 4]]
            return letter.upper() if text[i:i + 2].istitle() else letter
        else:
            return self.__inverted_phonemes[text[i:i + 2]]

    def __transliterate_ch_end_sequence(self, text, elems, i, is_upper):
        if ''.join(elems[-2:]) in ['ви', 'ны'] and is_upper == 1:
            return self.__inverted_phonemes[text[i:i + 2]]
        elif elems[-1] in 'иы':
            return 'х'
        else:
            return 'ч'

    def __transliterate_vowel_ending(self, text, elems, i):
        return 'ий' if re.search(r'[гджкцчшщ]$', elems[-1]) else self.__inverted_phonemes[text[i:i + 2]]

    def transliterate_two_letter_sequence(self, text, elems, i, is_upper):
        if self.__CH_START_REGEX.search(text[:i + 2]):
            res = self.__transliterate_ch_sequence(text, i)
        elif self.__CH_END_REGEX.search(text[i:]):
            res = self.__transliterate_ch_end_sequence(text, elems, i, is_upper)
        elif self.__is_iot_combination(text[i:i + 2]):
            answer = self.__COMBINATED_PHONEMES[text[i:i + 2]] if text[i:i + 2].lower() in self.IET_VOWELS \
                else self.__COMBINATED_E_PHONEMES[text[i:i + 2]] if text[i:i + 2].lower() in self.IOT_VOWELS \
                else self.__inverted_phonemes[text[i:i + 2]]
            res = self.__transliterate_vowels_sequence(text, answer, elems, i)
        elif text[i:i + 2].lower() in ['ij', 'iy', 'yi', 'yj'] and not text[i + 2].isalnum():
            res = self.__transliterate_vowel_ending(text, elems, i)
        elif text[i:i + 2].lower() in ['ij', 'iy', 'yi', 'yj']:
            res = self.__inverted_phonemes[text[i:i + 1]]
            i -= 1
        else:
            res = self.__inverted_phonemes[text[i:i + 2]]
        return res, i

    def simple_spell_euristic(self, word):
        if not self.__is_shch_exceptions(word):
            for phoneme, replaced in self.__UNCORRECTED_PHONEMES.items():
                word = phoneme.sub(replaced, word, re.IGNORECASE)
        return word

    def transliterate(self, text):
        return text.translate(self.__keys)

    def inverse_transliterate(self, text):
        elems = []
        i = 0
        is_upper = 0

        while i < len(text):
            if i == 0 or text[i - 1].isspace() or text[i - 1] in string.punctuation:
                is_upper = 1 if text[i].isupper() else 0

            if i == len(text) - 1 or text[i + 1] in string.punctuation or text[i + 1].isspace():
                elems += [self.__transliterate_ij_ending(text, elems, i)]
                i += 1
            elif i + 4 <= len(text) and text[i:i + 4] in self.__inverted_phonemes:
                phoneme = self.__inverted_phonemes[text[i:i + 4]]
                elems += [phoneme] if isinstance(phoneme, str) else phoneme
                i += 4
            elif i + 3 <= len(text) and text[i:i + 3] in self.__inverted_phonemes:
                phoneme = self.__inverted_phonemes[text[i:i + 3]]
                elems += [phoneme] if isinstance(phoneme, str) else phoneme
                i += 3
            elif i + 2 <= len(text) and text[i:i + 2] in self.__inverted_phonemes:
                answer, i = self.transliterate_two_letter_sequence(text, elems, i, is_upper)
                elems += answer
                i += 2
            else:
                output_symbol = self.__inverted_phonemes[text[i]] if text[i] in self.__inverted_phonemes else text[i]
                elems += [output_symbol]
                i += 1

        res = ''.join(elems)
        res = self.simple_spell_euristic(res)

        if self.__need_spell:
            pass
            # todo: add spell checker for this case
            '''
            elements = [
                self.__spell_checker.rectify(token.Value) if token.Type == 'WORD' else token.Value
                for token in self.__tokenizer.tokenize(res)
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
    assert translit.inverse_transliterate('Jod i Ioann') == 'Йод и Иоанн'
    assert translit.inverse_transliterate('Iony') == 'Ионы'
    assert translit.inverse_transliterate('Mjod') == 'Мёд'
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
