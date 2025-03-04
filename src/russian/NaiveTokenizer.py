import re
import string
from collections import namedtuple


class NaiveTokenizer(object):
    __digit = r'(\d)+'
    __letter = r'[A-ZА-Я]'

    emjoi_pattern = r'([\=\:\;8BX][\-\~\^oc]?[PD3\<\>\}\{\]\[\)\(\/]+)'

    CURRENCY = '$€£¢¥₽'
    OTHER_PUNCT = '#%^~±°'
    PUNCT = string.punctuation
    DIGIT = re.compile(__digit)
    LETTER = re.compile(__letter, re.IGNORECASE)
    NUMBER = re.compile(r'(-?' + __digit + r'([.,]' + __digit + r')?)')
    ABBR_WITH_POINTS = re.compile(r'(' + __letter + r'\.){3,}')
    NUMALPHA = re.compile(r'([/.\w-]+)')
    EMJOI = re.compile(r'(' + emjoi_pattern + r')+')
    EOS = '.?!'
    INS = ',:;'
    QUOTES = '\"\'\`'
    LQUOTES = '«“‘'
    RQUOTES = '»”’'
    LBRACKETS = '<([{'
    RBRACKETS = '>)]}'

    def __init__(self):
        with open('../russian/resources/tokenizer/abbreviations.txt', 'r', encoding='utf-8') as inf:
            self.abbr = {
                line.strip().lower() for line in inf
            }

        with open('../russian/resources/tokenizer/tlds-alpha-by-domain.txt', 'r') as inf:
            self.tlds = [
                line.strip().lower() for i, line in enumerate(inf) if i > 3
            ]

        tld = r'(' + r'|'.join(self.tlds) + r')'
        schema = r'(?:[^:\/]+:\/\/)'
        email = r'(?:([A-Z0-9][\w-]+)@([\w\.-])+[A-Z0-9]\.)'
        domain = r'(?:www\.)?(?:[A-Z0-9][A-Z0-9-]{0,61}[A-Z0-9]\.)+'
        port = r'(?::(\d{1,5}))'
        ip_address = r'(?:\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
        any_path = r'(?:(\/\S+[^\.\,\s]))'

        url = r'('
        url += rf'{schema}?'
        url += rf'((?:{email}|{domain})' + tld + rf'|{ip_address})'
        url += rf'{port}?'
        url += rf'{any_path}?'
        url += r')'

        self.URL = re.compile(url, re.IGNORECASE)

    def tokenize(self, text):

        def isnumalpha(s):
            return self.LETTER.search(s) and self.DIGIT.search(s)

        def get_sequence(cur_token):

            START, CURRENCY, EOS, INS, WORD = range(5)

            cur_tok = ''
            state = START

            for c in cur_token:
                if c in self.QUOTES + self.LQUOTES + self.RQUOTES + self.LBRACKETS + self.RBRACKETS + self.INS:
                    if state == START:
                        state = INS
                        cur_tok += c
                    elif state in (EOS, INS, CURRENCY, WORD):
                        state = INS
                        if cur_tok:
                            yield cur_tok
                            cur_tok = c
                    else:
                        state = INS
                        cur_tok += c
                elif c in self.EOS:
                    if state == START:
                        state = EOS
                        cur_tok += c
                    elif state == EOS:
                        cur_tok += c
                    elif state in (INS, CURRENCY):
                        state = EOS
                        if cur_tok:
                            yield cur_tok
                            cur_tok = c
                    elif state == WORD:
                        state = EOS
                        if cur_tok and ((cur_tok + c).lower() in self.abbr or len(cur_tok) <= 1):
                            cur_tok += c
                        else:
                            yield cur_tok
                            cur_tok = c
                    else:
                        state = EOS
                        cur_tok += c
                elif c in self.CURRENCY or c in self.OTHER_PUNCT:
                    if state == START:
                        state = CURRENCY
                        cur_tok += c
                    elif state == CURRENCY:
                        cur_tok += c
                    elif state in (EOS, INS, WORD):
                        state = CURRENCY
                        if cur_tok:
                            yield cur_tok
                            cur_tok = c
                    else:
                        state = CURRENCY
                        cur_tok += c
                elif c.isspace():
                    if cur_tok:
                        yield cur_tok
                else:
                    if state == START:
                        state = WORD
                        cur_tok += c
                    elif state in (EOS, INS, CURRENCY):
                        state = WORD
                        if cur_tok:
                            yield cur_tok
                            cur_tok = c
                    elif state == WORD:
                        cur_tok += c
                    else:
                        state = WORD
                        cur_tok += c

            if cur_tok:
                yield cur_tok

        def put_token(value):
            token = namedtuple('Token', ('Value', 'Type'))
            if value in self.LBRACKETS:
                return token(value, 'LBR')
            elif value in self.RBRACKETS:
                return token(value, 'RBR')
            elif value in self.LQUOTES:
                return token(value, 'LQUOTE')
            elif value in self.RQUOTES:
                return token(value, 'RQUOTE')
            elif value in self.QUOTES:
                return token(value, 'QUOTE')
            elif value in self.EOS + self.INS:
                return token(value, 'PUNCT')
            elif value in self.CURRENCY + self.OTHER_PUNCT + self.PUNCT:
                return token(value, 'SYMB')
            elif self.URL.search(value):
                return token(value, 'URL')
            elif self.NUMALPHA.search(value):
                return token(value, 'WORD')
            elif self.NUMBER.search(value):
                return token(value, 'NUMBER')
            elif self.EMJOI.search(value):
                return token(value, 'EMJOI')
            else:
                return token(value, 'WORD')

        for expected_token in text.split():
            if self.URL.search(expected_token) or \
                    self.NUMBER.search(expected_token) or \
                    self.ABBR_WITH_POINTS.search(expected_token) or self.EMJOI.search(expected_token):
                if self.URL.search(expected_token):
                    matched_pattern = self.URL.search(expected_token)
                elif self.ABBR_WITH_POINTS.search(expected_token):
                    matched_pattern = self.ABBR_WITH_POINTS.search(expected_token)
                elif self.EMJOI.search(expected_token):
                    matched_pattern = self.EMJOI.search(expected_token)
                elif not isnumalpha(expected_token):
                    matched_pattern = self.NUMBER.search(expected_token)
                else:
                    matched_pattern = self.NUMALPHA.search(expected_token)
                start, end = matched_pattern.start(), matched_pattern.end()
                first, middle, last = expected_token[:start], expected_token[start:end], expected_token[end:]
                if first:
                    for tok in get_sequence(first):
                        yield put_token(tok)
                yield put_token(middle)
                if last:
                    for tok in get_sequence(last):
                        yield put_token(tok)
            else:
                for tok in get_sequence(expected_token):
                    yield put_token(tok)


if __name__ == '__main__':
    tokenizer = NaiveTokenizer()
    # print(list(tokenizer.tokenize('2 + 2 = 4, а 2*2 == 5!')))

    assert [token.Value for token in list(tokenizer.tokenize(
        'За окном -5 градусов. Хорошего дня!'
    ))] == ['За', 'окном', '-5', 'градусов', '.', 'Хорошего', 'дня', '!']

    assert [token.Value for token in list(tokenizer.tokenize(
        'Спешите приобрести последние автомобили Volvo XS60!'
    ))] == ['Спешите', 'приобрести', 'последние', 'автомобили', 'Volvo', 'XS60', '!']

    assert [token.Value for token in list(tokenizer.tokenize(
        'Последняя модель телефона марки Siemens C-60 вызвала большой интерес '
        'у покупателей в течение пары дней с первого дня продажи.'
    ))] == ['Последняя', 'модель', 'телефона', 'марки', 'Siemens', 'C-60', 'вызвала', 'большой', 'интерес',
            'у', 'покупателей', 'в', 'течение', 'пары', 'дней', 'с', 'первого', 'дня', 'продажи', '.']

    assert [token.Value for token in list(tokenizer.tokenize(
        'Курс доллара на сегодняшний день составляет 62.73₽, курс евро - 73,73 ₽.'
    ))] == ['Курс', 'доллара', 'на', 'сегодняшний', 'день', 'составляет', '62.73', '₽', ',',
            'курс', 'евро', '-', '73,73', '₽', '.']

    assert [token.Value for token in list(tokenizer.tokenize(
        'В г. Санкт-Петербург ожидаются дожди с грозами, температура составит около 2-х градусов тепла.'
    ))] == ['В', 'г.', 'Санкт-Петербург', 'ожидаются', 'дожди', 'с', 'грозами', ',',
            'температура', 'составит', 'около', '2-х', 'градусов', 'тепла', '.']

    assert [token.Value for token in list(tokenizer.tokenize(
        'В огороде бузина, а в Киеве - дядька.'
    ))] == ['В', 'огороде', 'бузина', ',', 'а', 'в', 'Киеве', '-', 'дядька', '.']

    assert [token.Value for token in list(tokenizer.tokenize(
        'Нефть стоит $50,67. А в деревне Гадюкино - снова дожди!'
    ))] == ['Нефть', 'стоит', '$', '50,67', '.', 'А', 'в', 'деревне', 'Гадюкино', '-', 'снова', 'дожди', '!']

    assert [token.Value for token in list(tokenizer.tokenize(
        'Нефть стоит $50,67 . А в Кишенёве (моём родном городе) гостит моя тётка ...'
    ))] == ['Нефть', 'стоит', '$', '50,67', '.', 'А', 'в', 'Кишенёве', '(', 'моём', 'родном',
            'городе', ')', 'гостит', 'моя', 'тётка', '...']

    assert [token.Value for token in list(tokenizer.tokenize(
        'Следите за всеми новостями тут : facebook.com/zebrochka.'
    ))] == ['Следите', 'за', 'всеми', 'новостями', 'тут', ':', 'facebook.com/zebrochka', '.']

    assert [token.Value for token in list(tokenizer.tokenize(
        'Следите за всеми новостями тут: https://facebook.com/zebrochka.'
    ))] == ['Следите', 'за', 'всеми', 'новостями', 'тут', ':', 'https://facebook.com/zebrochka', '.']

    assert [token.Value for token in list(tokenizer.tokenize(
        'Пишите все письма на мой электронный ящик : dobro@gmail.com.'
    ))] == ['Пишите', 'все', 'письма', 'на', 'мой', 'электронный', 'ящик', ':', 'dobro@gmail.com', '.']

    assert [token.Value for token in list(tokenizer.tokenize(
        'Следите за моей  страницей здесь : www.vk.com/id777. Подписывайтесь !!!'
    ))] == ['Следите', 'за', 'моей', 'страницей', 'здесь', ':', 'www.vk.com/id777', '.',
            'Подписывайтесь', '!!!']

    assert [token.Value for token in list(tokenizer.tokenize(
        'Следите за новостями здесь : facebook.com/zebrochka.Подписывайтесь на наш "канал" и оставляйте лайки !!!'
    ))] == ['Следите', 'за', 'новостями', 'здесь', ':', 'facebook.com/zebrochka.Подписывайтесь',
            'на', 'наш', '"', 'канал', '"', 'и', 'оставляйте', 'лайки', '!!!']

    assert [token.Value for token in list(tokenizer.tokenize(
        'Максимальная скорость ветра - 5 м/с.'
    ))] == ['Максимальная', 'скорость', 'ветра', '-', '5', 'м/с', '.']

    assert [token.Value for token in list(tokenizer.tokenize(
        'Пл. Ал.Невского, следующая станция Елизаровская.'
    ))] == ['Пл.', 'Ал.', 'Невского', ',', 'следующая', 'станция', 'Елизаровская', '.']

    assert [token.Value for token in list(tokenizer.tokenize(
        'Нефть за $27/барр. обеспечена!'
    ))] == ['Нефть', 'за', '$', '27/барр.', 'обеспечена', '!']

    assert [token.Value for token in list(tokenizer.tokenize(
        'Надо расти и развиваться и т. д. и т. п.'
    ))] == ['Надо', 'расти', 'и', 'развиваться', 'и', 'т.', 'д.', 'и', 'т.', 'п.']

    assert [token.Value for token in list(tokenizer.tokenize(
        'В графе надо указать свои Ф.И.О.'
    ))] == ['В', 'графе', 'надо', 'указать', 'свои', 'Ф.И.О.']

    assert [token.Value for token in list(tokenizer.tokenize(
        'Я очень -очень рада этому событию ;) :^3'
    ))] == ['Я', 'очень', '-очень', 'рада', 'этому', 'событию', ';)', ':^3']

    assert [token.Value for token in list(tokenizer.tokenize(
        'Я рада этому событию ;):^3'
    ))] == ['Я', 'рада', 'этому', 'событию', ';):^3']
