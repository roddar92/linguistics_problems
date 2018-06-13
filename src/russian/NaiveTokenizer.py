import re


class NaiveTokenizer(object):

    def __init__(self):
        with open('../russian/resources/tokenizer/abbreviations.txt', 'r') as inf:
            self.abbr = [
                line.strip().lower() for line in inf
            ]

        with open('../russian/resources/tokenizer/tlds-alpha-by-domain.txt', 'r') as inf:
            self.tlds = [
                line.strip().lower() for i, line in enumerate(inf) if i > 3
            ]

        url = r'('
        url += r'(?:(https?|s?ftp):\/\/)?'
        url += r'(?:www\.)?'
        url += r'('
        url += r'(?:(?:([A-Z0-9][A-Z0-9-_]+)@([A-Z0-9-_\.])+[A-Z0-9]\.)' \
               r'|(?:[A-Z0-9][A-Z0-9-]{0,61}[A-Z0-9]\.)+)'

        tld = r'(' + self.tlds[0]
        for i in range(1, len(self.tlds)):
            tld += r'|{}'.format(self.tlds[i])
        tld += r')'

        url += tld
        url += r'|(?:\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
        url += r')'
        url += r'(?::(\d{1,5}))?'
        url += r'(?:(\/[^\.\,\s]+))?'
        url += r')'

        self.URL = re.compile(url, re.IGNORECASE)
        self.CURRENCY = '$€£¢¥₽'
        self.OTHER_PUNCT = '#%'
        self.DIGIT = re.compile(r'((\d)+([.,](\d)+)?)')
        self.EOS = '.?!'
        self.INS = ',:;'
        self.QUOTES = '\"\'\`«»“”‘’'
        self.LBRACKETS = '([{'
        self.RBRACKETS = ')]}'

    def tokenize(self, text):

        def get_sequence(cur_token):

            START, CURRENCY, EOS, INS, WORD = range(5)

            toks = []
            cur_tok = ''
            state = START

            for c in cur_token:
                if c in self.QUOTES + self.LBRACKETS + self.RBRACKETS + self.INS:
                    if state == START:
                        state = INS
                        cur_tok += c
                    elif state in (EOS, INS, CURRENCY, WORD):
                        state = INS
                        if cur_tok:
                            toks += [cur_tok]
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
                            toks += [cur_tok]
                            cur_tok = c
                    elif state == WORD:
                        state = EOS
                        if cur_tok and ((cur_tok + c).lower() in self.abbr or len(cur_tok) <= 1):
                            cur_tok += c
                        else:
                            toks += [cur_tok]
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
                            toks += [cur_tok]
                            cur_tok = c
                    else:
                        state = CURRENCY
                        cur_tok += c
                elif c.isspace():
                    if cur_tok:
                        toks += [cur_tok]
                else:
                    if state == START:
                        state = WORD
                        cur_tok += c
                    elif state in (EOS, INS, CURRENCY):
                        state = WORD
                        if cur_tok:
                            toks += [cur_tok]
                            cur_tok = c
                    elif state == WORD:
                        cur_tok += c
                    else:
                        state = WORD
                        cur_tok += c

            if cur_tok:
                toks += [cur_tok]

            return toks

        for excpected_token in text.split():
            if self.URL.search(excpected_token) or self.DIGIT.search(excpected_token):
                if self.URL.search(excpected_token):
                    start, end = self.URL.search(excpected_token).start(), self.URL.search(excpected_token).end()
                else:
                    start, end = self.DIGIT.search(excpected_token).start(), \
                                 self.DIGIT.search(excpected_token).end()
                first, middile, last = excpected_token[:start], excpected_token[start:end], excpected_token[end:]
                if first:
                    for token in get_sequence(first):
                        yield token
                yield middile
                if last:
                    for token in get_sequence(last):
                        yield token
            else:
                for token in get_sequence(excpected_token):
                    yield token


if __name__ == '__main__':
    tokenizer = NaiveTokenizer()

    assert list(tokenizer.tokenize(
        'Курс доллара на сегодняшний день составляет 62.73, курс евро - 73,73.'
    )) == ['Курс', 'доллара', 'на', 'сегодняшний', 'день', 'составляет', '62.73', ',',
           'курс', 'евро', '-', '73,73', '.']

    assert list(tokenizer.tokenize(
        'В г. Санкт-Петербург ожидаются дожди с грозами, температура составит около 2-х градусов тепла.'
    )) == ['В', 'г.', 'Санкт-Петербург', 'ожидаются', 'дожди', 'с', 'грозами', ',',
           'температура', 'составит', 'около', '2', '-х', 'градусов', 'тепла', '.']

    assert list(tokenizer.tokenize(
        'В огороде бузина, а в Киеве - дядька.'
    )) == ['В', 'огороде', 'бузина', ',', 'а', 'в', 'Киеве', '-', 'дядька', '.']

    assert list(tokenizer.tokenize(
        'Нефть стоит $50,67. А в деревне Гадюкино - снова дожди!'
    )) == ['Нефть', 'стоит', '$', '50,67', '.', 'А', 'в', 'деревне', 'Гадюкино', '-', 'снова', 'дожди', '!']

    assert list(tokenizer.tokenize(
        'Нефть стоит $50,67 . А в Кишенёве (моём родном городе) гостит моя тётка ...'
    )) == ['Нефть', 'стоит', '$', '50,67', '.', 'А', 'в', 'Кишенёве', '(', 'моём', 'родном',
           'городе', ')', 'гостит', 'моя', 'тётка', '...']

    assert list(tokenizer.tokenize(
        'Следите за всеми новостями тут : facebook.com/zebrochka.'
    )) == ['Следите', 'за', 'всеми', 'новостями', 'тут', ':', 'facebook.com/zebrochka', '.']

    assert list(tokenizer.tokenize(
        'Пишите все письма на мой электронный ящик : dobro@gmail.com.'
    )) == ['Пишите', 'все', 'письма', 'на', 'мой', 'электронный', 'ящик', ':', 'dobro@gmail.com', '.']

    assert list(tokenizer.tokenize(
        'Следите за новостями здесь : facebook.com/zebrochka.Подписывайтесь на наш "канал" и оставляйте лайки !!!'
    )) == ['Следите', 'за', 'новостями', 'здесь', ':', 'facebook.com/zebrochka', '.',
           'Подписывайтесь', 'на', 'наш', '"', 'канал', '"', 'и', 'оставляйте', 'лайки', '!!!']
