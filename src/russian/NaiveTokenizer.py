import re, string


class NaiveTokenizer(object):

    def __init__(self):
        with open('../russian/resources/tokenizer/abbreviations.txt', 'r') as inf:
            self.abbr = [
                line.strip().lower() for line in inf
            ]

        # self.domains = []
        self.CURRENCY = '$€£¢¥₽'
        self.DIGIT = re.compile(r'(\d)+([\.,](\d)+)?')
        self.EOS = '.?!'
        self.INS = ',:;'
        self.QUOTES = '\"\'\`'
        self.LBRACKETS = '([{'
        self.RBRACKETS = ')]}'

    def tokenize(self, text):

        def get_sequence(token):

            START, CURRENCY, EOS, BRACK, WORD = range(5)

            toks = []
            cur_tok = ''
            state = START

            for c in token:
                if c in self.QUOTES + self.LBRACKETS + self.RBRACKETS + self.INS:
                    if state == START:
                        state = BRACK
                        cur_tok += c
                    elif state in (EOS, BRACK, CURRENCY, WORD):
                        state = BRACK
                        if cur_tok:
                            toks += cur_tok
                            cur_tok += c
                    else:
                        state = BRACK
                        cur_tok += c
                elif c in self.EOS:
                    if state == START:
                        state = EOS
                        cur_tok += c
                    elif state == EOS:
                        cur_tok += c
                    elif state in (BRACK, CURRENCY):
                        state = EOS
                        if cur_tok:
                            toks += cur_tok
                            cur_tok += c
                    elif state == WORD:
                        state = EOS
                        if cur_tok and cur_tok + c not in self.abbr:
                            toks += [cur_tok]
                            cur_tok += c
                        else:
                            cur_tok += c
                    else:
                        state = EOS
                        cur_tok += c
                elif c in self.CURRENCY or \
                        (c in string.punctuation and c not in self.QUOTES +
                         self.LBRACKETS + self.RBRACKETS + self.INS + self.EOS):
                    if state == START:
                        state = CURRENCY
                        cur_tok += c
                    elif state == CURRENCY:
                        cur_tok += c
                    elif state in (EOS, BRACK, WORD):
                        state = CURRENCY
                        if cur_tok:
                            toks += cur_tok
                            cur_tok += c
                    else:
                        state = CURRENCY
                        cur_tok += c
                elif c.isspace():
                    if cur_tok:
                        toks += cur_tok
                else:
                    if state == START:
                        state = WORD
                        cur_tok += c
                    elif state in (EOS, BRACK, CURRENCY):
                        state = WORD
                        if cur_tok:
                            toks += cur_tok
                            cur_tok += c
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
                start, end = self.URL.search(excpected_token).start(), self.URL.search(excpected_token).end()
                if not (start or end):
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

            """if excpected_token[0] in self.CURRENCY:
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
            elif excpected_token[-1] in self.EOS + self.INS:
                yield excpected_token[:-1]
                yield excpected_token[-1]
            else:
                yield excpected_token"""


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
