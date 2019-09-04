import pymorphy2
import re


class Number2TextConverter:

    SIMPLE_NUMBERS = {
        0: {0: 'нуль', 1: 'нулевой'},
        1: {0: 'один', 1: 'первый'},
        2: {0: 'два', 1: 'второй'},
        3: {0: 'три', 1: 'третий'},
        4: {0: 'четыре', 1: 'четвертый'},
        5: {0: 'пять', 1: 'пятый'},
        6: {0: 'шесть', 1: 'шестой'},
        7: {0: 'семь', 1: 'седьмой'},
        8: {0: 'восемь', 1: 'восьмой'},
        9: {0: 'девять', 1: 'девятый'},
        11: {0: 'одиннадцать', 1: 'одиннадцатый'},
        12: {0: 'двенадцать', 1: 'двенадцатый'},
        13: {0: 'тринадцать', 1: 'тринадцатый'},
        14: {0: 'четырнадцать', 1: 'четырнадцатый'},
        15: {0: 'пятнадцать', 1: 'пятнадцатый'},
        16: {0: 'шестнадцать', 1: 'шестнадцатый'},
        17: {0: 'семнадцать', 1: 'семнадцатый'},
        18: {0: 'восемнадцать', 1: 'восемнадцатый'},
        19: {0: 'девятнадцать', 1: 'девятнадцатый'}
    }

    DOZENS = {
        10: {0: 'десять', 1: 'десятый'},
        20: {0: 'двадцать', 1: 'двадцатый'},
        30: {0: 'тридцать', 1: 'тридцатый'},
        40: {0: 'сорок', 1: 'сороковой'},
        50: {0: 'пятьдесят', 1: 'пятьдесятый'},
        60: {0: 'шестьдесят', 1: 'шестьдесятый'},
        70: {0: 'семьдесят', 1: 'семидесятый'},
        80: {0: 'восемьдесят', 1: 'восьмидесятый'},
        90: {0: 'девяносто', 1: 'девяностый'}
    }

    HUNDREDS = {
        100: {0: 'сто', 1: 'сотый'},
        200: {0: 'двести', 1: 'двухсотый'},
        300: {0: 'триста', 1: 'трехсотый'},
        400: {0: 'четыреста', 1: 'четырехсотый'},
        500: {0: 'пятьсот', 1: 'пятисотый'},
        600: {0: 'шестьсот', 1: 'шестисотый'},
        700: {0: 'семьсот', 1: 'семисотый'},
        800: {0: 'восемсот', 1: 'восьмисотый'},
        900: {0: 'девятьсот', 1: 'девятисотый'}
    }

    THOUSANDS = {
        1000: {0: 'тысяча', 1: 'тысячный'},
        1000000: {0: 'миллион', 1: 'миллионный'},
        1000000000: {0: 'миллиард', 1: 'миллиардный'}
    }

    ROMAN = {
        "I": 1, "V": 5,
        "X": 10, "L": 50,
        "C": 100, "D": 500,
        "M": 1000
    }

    FRAC_REM = {
        1: 'десятая',
        2: 'сотая',
        3: 'тысячная',
        4: 'десятитысячная',
        5: 'стотысячная',
        6: 'миллионная',
        7: 'десятимиллионная',
    }

    __ROMAN_REGEX = re.compile(r'^[IVXLCDM]+$', re.IGNORECASE)
    __DECIMAL = re.compile(r'(\d+)[.,](\d+)', re.IGNORECASE)

    def __init__(self):
        self.morph = pymorphy2.MorphAnalyzer()

    @staticmethod
    def __number2decomposition(number):
        decomposition = []
        k = 1
        while number > 0:
            rem = number % 10
            if rem > 0:
                t = rem * k
                if t == 10:
                    digit = decomposition.pop()
                    t += digit
                decomposition.append(t)
            k *= 10
            number //= 10
        return decomposition[::-1]

    def roman2arabic(self, roman_str):
        number = 0
        i = 0
        while i < len(roman_str):
            first = self.ROMAN[roman_str[i]]
            second = self.ROMAN[roman_str[i + 1]] if i < len(roman_str) - 1 else -1
            if first >= second:
                number += first
                i += 1
            else:
                number += second - first
                i += 2
        return number

    def __inflect_word(self, n, word):
        return self.morph.parse(word)[0].make_agree_with_number(n).word

    def convert(self, number, grammems=None, ordered=False):

        def _change_last_word(frac_str):
            last_word = frac_str.pop()
            if last_word == 'один':
                frac_str += ['одна']
            elif last_word == 'два':
                frac_str += ['две']
            else:
                frac_str += [last_word]
            return frac_str

        if type(number) == float:
            number = str(number)

        if type(number) == str and self.__DECIMAL.search(number):
            decimal = self.__DECIMAL.search(number)
            b_point, a_point = int(decimal.group(1)), decimal.group(2)

            rem = self.FRAC_REM[len(a_point)]
            a_str = self.convert(b_point).split()
            b_str = self.convert(int(a_point)).split()

            a_str = _change_last_word(a_str)
            b_str = _change_last_word(b_str)

            first, second = ' '.join(a_str), ' '.join(b_str)
            n_word, rem_word = self.__inflect_word(b_point, 'целая'), self.__inflect_word(int(a_point), rem)
            result = f'{first} {n_word} {second} {rem_word}'
            return result

        if type(number) == str and self.__ROMAN_REGEX.match(number):
            decomposition = self.__number2decomposition(self.roman2arabic(number.upper()))
        else:
            decomposition = self.__number2decomposition(number)

        answer = []
        for i, n in enumerate(decomposition):
            ordered_condition = ordered and i == len(decomposition) - 1
            key = 1 if ordered_condition else 0
            if n >= 1000:
                if n >= 1000000000:
                    t = 1000000000
                elif n >= 1000000:
                    t = 1000000
                elif n >= 1000:
                    t = 1000
                k = n // t

                if 3 <= k <= 4 and ordered_condition:
                    w = self.SIMPLE_NUMBERS[k][0][:-2] + 'ех'
                elif k > 5 and k in self.SIMPLE_NUMBERS and ordered_condition:
                    w = self.SIMPLE_NUMBERS[k][0][:-1] + 'и'
                elif k in self.DOZENS and k != 90 and ordered_condition:
                    w = self.DOZENS[k][1][:-2] + 'и'
                elif k in self.DOZENS and ordered_condition:
                    w = self.DOZENS[k][0]
                elif k == 3 and n > 1000:
                    w = 'трех' if ordered_condition else 'две'
                elif k == 2 and n > 1000:
                    w = 'двух' if ordered_condition else 'две'
                elif k > 100:
                    w = self.HUNDREDS[k][key][:-2] if ordered_condition else self.HUNDREDS[k][key]
                elif k == 100:
                    w = self.HUNDREDS[k][0]
                elif k >= 10 and not (11 <= k <= 19):
                    w = self.DOZENS[k][key]
                else:
                    w = self.SIMPLE_NUMBERS[k][key]

                if k > 1 and not ordered_condition:
                    answer.append(w)
                thousand = self.THOUSANDS[t]
                word_for_thousand = thousand[1] if ordered_condition else self._inflect_word(k, thousand[0])
                if ordered_condition:
                    word_for_thousand = (w if k > 1 else '') + word_for_thousand
                answer.append(word_for_thousand)
            elif n >= 100:
                answer += [self.HUNDREDS[n][key]]
            elif n >= 10 and not (11 <= n <= 19):
                answer += [self.DOZENS[n][key]]
            else:
                answer += [self.SIMPLE_NUMBERS[n][key]]

        if grammems:
            if not ordered:
                answer = [
                    self.morph.parse(w)[0].inflect(grammems).word
                    if self.morph.parse(w)[0].inflect(grammems) is not None else w
                    for w in answer
                ]
            else:
                last = answer.pop()
                answer.append(
                    self.morph.parse(last)[0].inflect(grammems).word
                    if self.morph.parse(last)[0].inflect(grammems) is not None else last
                )
        return ' '.join(answer)


# TODO class TextNormalizer with normalization approach (2км => 2 км => два км OR 2 книги => две книги)
class TextNormalizer:
    __NUMB_WITH_ORD_ENDINGS = re.compile(r'(\d+)-?([оыьа][ехя]|[ео]?го|[еоы]?й|е|х)', re.IGNORECASE)
    __NUMB_WITH_ENDINGS = re.compile(r'(\d+)-?([мт]?и|(ть)?ю)', re.IGNORECASE)
    __NUMBERS = re.compile(r'^(\d+([.,]\d+)?)$', re.IGNORECASE)
    __NUMBERS_WITH_ZEROS = re.compile(r'(?<=\d)(\s)(000)', re.IGNORECASE)
    __ROMAN_REGEX = re.compile(r'^[IVXLCDM]+$', re.IGNORECASE)
    __MONTHS = re.compile(r'^(янв(ар[ья])?|фев(рал[ья])?|марта?|апр(ел[ья])?|'
                         r'ма[йя]|июня?|июля?|авг(уст)?а?|'
                         r'сент?(ябр[ья])?|окт(ябр[ья])?|ноя(бр[ья])?|дек(абр[ья])?)$', re.IGNORECASE)
    __YEAR_CENTURY = re.compile(r'^(век(а|е|ов)|вв?|год[ау]|гг?)$', re.IGNORECASE)

    ENDING_TO_GRAMMEME = {
        'ая': {'femn'},
        'ое': {'neut'},
        'ье': {'neut'},
        'й': {'masc'},
        'ый': {'masc'},
        'ой': {'masc'},
        'е': {'plur'},
        'ые': {'plur'},
        'го': {'gent'},
        'его': {'gent'},
        'ого': {'gent'},
        'х': {'plur', 'gent'},
        'ых': {'plur', 'gent'},
        'ми': {'gent'},
        'ти': {'gent'},
        'ю': {'ablt'},
        'тью': {'ablt'},
        'м': {'loc2'},
        'ом': {'loc2'},
        'му': {'datv'},
        'ому': {'datv'},
        'ым': {'plur', 'datv'}
    }

    SPEC_UNITS = {
        'г': {'DATE': 'год', 'OTHER': 'грамм'},
        'м': {'OTHER': 'метр', 'TIME': 'минута'}
    }

    UNITS = {
        'в': 'век',
        'вв': 'века',
        'гг': 'годы',
        'г': 'грамм',
        'т': 'тонна',
        'кг': 'килограмм',
        'Вт': 'ватт',
        'кВт': 'киловатт',
        'Гц': 'герц',
        'кГц': 'килогерц',
        'л': 'литр',
        'сек': 'секунда',
        'мин': 'минута',
        'мм': 'миллиметр',
        'см': 'сантиметр',
        'дм': 'дециметр',
        'км': 'километр'
    }

    PREP_CASE_DICT = {
        'в': ['accs', 'loct', 'loc2'],
        'над': ['ablt'],
        'с': ['ablt', 'gent'],
        'к': ['datv'],
        'кроме': ['gent'],
        'от': ['gent'],
        'о': ['loct', 'accs'],
        'об': ['loct', 'accs'],
        'обо': ['loct', 'accs'],
        'до': ['gent'],
        'у': ['gent', 'gen2'],
        'при': ['loct'],
        'про': ['accs'],
        'по': ['datv', 'loct']
    }

    def __init__(self):
        self.morph = pymorphy2.MorphAnalyzer()
        self.numb2text = Number2TextConverter()

    @classmethod
    def remove_spaces_between_zeros(cls, text):
        return cls.__NUMBERS_WITH_ZEROS.sub(r'\2', text)

    def __extract_parameters_for_number(self, text):
        match = self.__NUMB_WITH_ORD_ENDINGS.search(text)
        match2 = self.__NUMB_WITH_ENDINGS.search(text)
        if match:
            number, ending = int(match.group(1)), match.group(2)
        else:
            number, ending = int(match2.group(1)), match2.group(2)
        grammems = self.ENDING_TO_GRAMMEME[ending]
        ordered = match is not None
        return number, ordered, grammems

    def calculate_parameters_by_neighbours(self, text_fragment):
        grammems, ordered = set(), False
        gender, number, case = (False, False, False)
        for token in text_fragment:
            if self.__YEAR_CENTURY.match(token) or self.__MONTHS.match(token) or \
                    self.morph.parse(token)[0].normal_form in ['быть', 'стать']:
                ordered = True
                if self.__YEAR_CENTURY.match(token):
                    parse = self.morph.parse(token)
                    if parse:
                        grammems = {parse[0].tag.number, parse[0].tag.case}
                        case = True
                        number = True
                    else:
                        grammems = {'masc', 'gent'}
                        case = True
                        gender = True
                elif self.__MONTHS.search(token):
                    grammems = {'neut'}
                    case = True
                elif self.morph.parse(token)[0].normal_form in ['быть', 'стать']:
                    grammems = {'ablt'}
                    case = True
            elif token not in self.UNITS:
                parse = self.morph.parse(token)
                if not gender and parse[0].tag.gender:
                    grammems.add(parse[0].tag.gender)
                    gender = True
                if not number and parse[0].tag.number:
                    grammems.add(parse[0].tag.number)
                    number = True
                if not case and parse[0].tag.case:
                    grammems.add(parse[0].tag.case)
                    case = True

        return ordered, grammems

    def normalize(self, tokens, neighbours=2):
        result = []
        for i, token in enumerate(tokens):
            if self.__ROMAN_REGEX.match(token) or self.__NUMBERS.match(token):
                # TODO: improve/train ordered and grammems parameters
                a = 0 if i < neighbours else i - neighbours
                b = len(tokens) if i + neighbours > len(tokens) + 1 else i + neighbours
                ordered, grammems = self.calculate_parameters_by_neighbours(
                    tokens[a:i] + tokens[i:b])

            if self.__NUMB_WITH_ORD_ENDINGS.search(token) or self.__NUMB_WITH_ENDINGS.search(token):
                number, ordered, grammems = self.__extract_parameters_for_number(token)
                if number in [2, 3] and token.endswith('х'):
                    result += ['двух' if number == 2 else 'трех']
                else:
                    result += [self.numb2text.convert(number, grammems=grammems, ordered=ordered)]
            elif self.__ROMAN_REGEX.match(token):
                result += [self.numb2text.convert(token, grammems=grammems, ordered=ordered)]
            elif self.__NUMBERS.match(token):
                result += [self.numb2text.convert(int(token), grammems=grammems, ordered=ordered)]
            elif token in self.UNITS:
                units = self.UNITS[token]
                if self.__ROMAN_REGEX.match(tokens[i - 1]) or self.__NUMBERS.match(tokens[i - 1]):
                    prev_token = tokens[i - 1]
                    n = self.numb2text.roman2arabic(prev_token) \
                        if self.__ROMAN_REGEX.match(prev_token) else int(prev_token)
                    units_parse = self.morph.parse(units)
                    if units_parse:
                        for unit in units_parse:
                            if 'nomn' in unit.tag:
                                units = unit.make_agree_with_number(n).word
                result += [units]
            else:
                result += [token]
        return result


if __name__ == '__main__':
    converter = Number2TextConverter()
    assert converter.convert(234) == 'двести тридцать четыре'
    assert converter.convert(234, ordered=True) == 'двести тридцать четвертый'
    assert converter.convert(234, grammems={'gent'}) == 'двухсот тридцати четырёх'
    assert converter.convert(234, ordered=True, grammems={'gent'}) == 'двести тридцать четвёртого'
    assert converter.convert(1) == 'один'
    assert converter.convert(1, grammems={'gent', 'plur'}) == 'одних'
    assert converter.convert(1, grammems={'femn', 'gent'}) == 'одной'
    assert converter.convert(1, ordered=True) == 'первый'
    assert converter.convert(22, ordered=True) == 'двадцать второй'
    assert converter.convert(100) == 'сто'
    assert converter.convert(100, ordered=True) == 'сотый'
    assert converter.convert(114) == 'сто четырнадцать'
    assert converter.convert(114, ordered=True) == 'сто четырнадцатый'
    assert converter.convert(200, ordered=True) == 'двухсотый'
    assert converter.convert(1234) == 'тысяча двести тридцать четыре'
    assert converter.convert(1234, ordered=True) == 'тысяча двести тридцать четвертый'
    assert converter.convert('xIX', ordered=True) == 'девятнадцатый'
    assert converter.convert('MCmlXXxiV', ordered=True) == 'тысяча девятьсот восемьдесят четвертый'
    assert converter.convert(2000) == 'две тысячи'
    assert converter.convert(2000, ordered=True) == 'двухтысячный'
    assert converter.convert(2000, ordered=True, grammems={'plur'}) == 'двухтысячные'
    assert converter.convert(2020) == 'две тысячи двадцать'
    assert converter.convert(2020, ordered=True) == 'две тысячи двадцатый'
    assert converter.convert(4000) == 'четыре тысячи'
    assert converter.convert(4000, ordered=True) == 'четыехтысячный'
    assert converter.convert(6000) == 'шесть тысяч'
    assert converter.convert(6000, ordered=True) == 'шеститысячный'
    assert converter.convert(60000) == 'шестьдесят тысяч'
    assert converter.convert(60000, ordered=True) == 'шестьдесятитысячный'
    assert converter.convert(90000) == 'девяносто тысяч'
    assert converter.convert(90000, ordered=True) == 'девяностотысячный'
    assert converter.convert(1114) == 'тысяча сто четырнадцать'
    assert converter.convert(1114, ordered=True) == 'тысяча сто четырнадцатый'
    assert converter.convert(2345) == 'две тысячи триста сорок пять'
    assert converter.convert(2345, ordered=True) == 'две тысячи триста сорок пятый'
    assert converter.convert(10000, ordered=True) == 'десятитысячный'
    assert converter.convert(10234) == 'десять тысяч двести тридцать четыре'
    assert converter.convert(10234, ordered=True) == 'десять тысяч двести тридцать четвертый'
    assert converter.convert(100000, ordered=True) == 'стотысячный'
    assert converter.convert(200000, ordered=True) == 'двухсоттысячный'  # ???
    assert converter.convert(100234) == 'сто тысяч двести тридцать четыре'
    assert converter.convert(100234, ordered=True) == 'сто тысяч двести тридцать четвертый'
    assert converter.convert(1000214) == 'миллион двести четырнадцать'
    assert converter.convert(1000214, ordered=True) == 'миллион двести четырнадцатый'
    assert converter.convert(5000214) == 'пять миллионов двести четырнадцать'
    assert converter.convert(5000214, ordered=True) == 'пять миллионов двести четырнадцатый'
    assert converter.convert(3.31) == 'три целые тридцать одна сотая'
    assert converter.convert(2.35) == 'две целые тридцать пять сотых'

    normalizer = TextNormalizer()
    assert normalizer.normalize(['80-е'])[-1] == 'восьмидесятые'
    assert normalizer.normalize(['80-х'])[-1] == 'восьмидесятых'
    assert normalizer.normalize(['21й'])[-1] == 'двадцать первый'
    assert normalizer.normalize(['3х'])[-1] == 'трех'
    assert ' '.join(normalizer.normalize(['21', 'июня'])) == 'двадцать первое июня'
    assert ' '.join(normalizer.normalize(['23', 'июля', '1806', 'года'])) == \
           'двадцать третье июля тысяча восемсот шестого года'
    assert ' '.join(normalizer.normalize(['23', 'июля', '1806', 'года'], neighbours=4)) == \
           'двадцать третьего июля тысяча восемсот шестого года'

    test_text = TextNormalizer.remove_spaces_between_zeros('20 000 000 тонн').split()
    assert ' '.join(normalizer.normalize(test_text)) == 'двадцать миллионов тонн'
    assert ' '.join(normalizer.normalize(['25', 'кг'])) == 'двадцать пять килограмм'
