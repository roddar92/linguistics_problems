import re


class NaiveTokenizer(object):

    def __init__(self):
        with open('../russian/resources/tokenizer/abbreviations.txt', 'r') as inf:
            self.abbr = [
                line.strip().lower() for line in inf
            ]

        # self.domains = []
        self.CURRENCY = '$€£¢¥₽'
        self.DIGIT = re.compile(r'(\d)+([\.,](\d)+)?')
        self.EOS = '.,?!'

    def tokenize(self, text):
        for excpected_token in text.split():
            if excpected_token[0] in self.CURRENCY:
                yield excpected_token[0]
                excpected_token = excpected_token[1:]

            if excpected_token.endswith(','):
                yield excpected_token[:-1]
                yield excpected_token[-1]
            elif ',' in excpected_token and not self.DIGIT.match(excpected_token):
                ind = excpected_token.find(',')
                yield excpected_token[:ind]
                yield excpected_token[ind]
                yield excpected_token[ind + 1:]
            elif excpected_token.endswith('.') and \
                    (excpected_token in self.abbr or len(excpected_token[:-1]) <= 1):
                yield excpected_token
            elif excpected_token[-1] in self.EOS:
                yield excpected_token[:-1]
                yield excpected_token[-1]
            else:
                yield excpected_token


if __name__ == '__main__':
    tokenizer = NaiveTokenizer()

    assert list(tokenizer.tokenize(
        'Курс доллара на сегодняшний день составляет 62.73, курс евро - 73,73.'
    )) == ['Курс', 'доллара', 'на', 'сегодняшний', 'день', 'составляет', '62.73', ',',
          'курс', 'евро', '-', '73,73', '.']

    assert list(tokenizer.tokenize(
        'В г. Санкт-Петербург ожидаются дожди с грозами, температура составит около 2-х градусов тепла.'
    )) == ['В', 'г.', 'Санкт-Петербург', 'ожидаются', 'дожди', 'с', 'грозами', ',',
          'температура', 'составит', 'около', '2-х', 'градусов', 'тепла', '.']

    assert list(tokenizer.tokenize(
        'В огороде бузина, а в Киеве - дядька.'
    )) == ['В', 'огороде', 'бузина', ',', 'а', 'в', 'Киеве', '-', 'дядька', '.']

    assert list(tokenizer.tokenize(
        'Нефть стоит $50,67. А в деревне Гадюкино - снова дожди!'
    )) == ['Нефть', 'стоит', '$', '50,67', '.', 'А', 'в', 'деревне', 'Гадюкино', '-', 'снова', 'дожди', '!']
