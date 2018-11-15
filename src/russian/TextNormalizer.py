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

    _ROMAN_REGEX = re.compile(r'^[IVXLCDM]+$', re.IGNORECASE)
    _DECIMAL = re.compile(r'(\d+)[.,](\d+)')

    def __init__(self):
        self.morph = pymorphy2.MorphAnalyzer()

    @staticmethod
    def _number2decomposition(number):
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

    def _roman2arabic(self, roman_str):
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

    def _inflect_word(self, n, word):
        return self.morph.parse(word)[0].make_agree_with_number(n).word

    def convert(self, number, grammems=None, ordered=False):

        def _change_last_word(frac_str):
            last = frac_str.pop()
            if last == 'один':
                frac_str += ['одна']
            elif last == 'два':
                frac_str += ['две']
            else:
                frac_str += [last]
            return frac_str

        if type(number) == float:
            number = str(number)

        if type(number) == str and self._DECIMAL.search(number):
            decimal = self._DECIMAL.search(number)
            b_point, a_point = int(decimal.group(1)), decimal.group(2)

            rem = self.FRAC_REM[len(a_point)]
            a_str = self.convert(b_point).split()
            b_str = self.convert(int(a_point)).split()

            a_str = _change_last_word(a_str)
            b_str = _change_last_word(b_str)

            result = '{} {} {} {}'.format(
                ' '.join(a_str), self._inflect_word(b_point, 'целая'),
                ' '.join(b_str), self._inflect_word(int(a_point), rem)
            )
            return result

        if type(number) == str and self._ROMAN_REGEX.match(number):
            decomposition = self._number2decomposition(self._roman2arabic(number.upper()))
        else:
            decomposition = self._number2decomposition(number)

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
                answer = [self.morph.parse(w)[0].inflect(grammems).word for w in answer]
            else:
                answer.append(self.morph.parse(answer.pop())[0].inflect(grammems).word)
        return ' '.join(answer)


# TODO class TextNormalizer with normalization approach (2км => 2 км => два км OR 2 книги => две книги)
class TextNormalizer:
    pass


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
