import re
from src.russian.NaiveTokenizer import NaiveTokenizer


class NaiveSentenceBoundaryDetector(object):
    DOT = '.'
    QUESTION = '?'
    EXPRESSION = '!'
    __EOS = (DOT, QUESTION, EXPRESSION, '...')
    MULTI_PUNCT = re.compile(r'([.?!]){2,}')
    ABBR_WITH_POINTS = re.compile(r'([A-ZА-Я]\.){3,}')
    ITD = re.compile(r'и т\. [дп]\.', re.I)
    IDR = re.compile(r'и [дп]р\.', re.I)

    def __init__(self):
        self.tokenizer = NaiveTokenizer()

    def __is_eos(self, token):
        return token in self.__EOS

    def __is_standard_abbr(self, curr_sent):
        if len(curr_sent) >= 3 and self.ITD.search(f'{curr_sent[-3]} {curr_sent[-2]} {curr_sent[-1]}'):
            return True
        elif len(curr_sent) >= 2 and self.IDR.search(f'{curr_sent[-2]} {curr_sent[-1]}'):
            return True
        else:
            return False

    def extract_sentences(self, text):
        _STATUS_START, _STATUS_SPLIT, _STATUS_MISS, _STATUS_EXPTED = range(4)
        _brackets_count = 0
        _inside_quotes = False

        _current_status = _STATUS_START
        _prev_token, _prev_ttype = '', ''

        current_sentence = []
        for token in self.tokenizer.tokenize(text):
            ttype, val = token.Type, token.Value
            if ttype not in ('WORD', 'NUMBER', 'URL', 'QUOTE', 'LBR', 'LQUOTE', 'RBR', 'RQUOTE'):
                if self.__is_eos(val) or self.MULTI_PUNCT.search(val):
                    if val in (self.QUESTION, self.EXPRESSION) or self.MULTI_PUNCT.search(val):
                        _current_status = _STATUS_MISS
                    elif val == self.DOT:
                        if len(_prev_token) <= 1:
                            _current_status = _STATUS_MISS
                        else:
                            _current_status = _STATUS_EXPTED
            elif ttype == 'QUOTE':
                _inside_quotes = not _inside_quotes

                if not _inside_quotes and (self.__is_eos(_prev_token) or self.MULTI_PUNCT.search(_prev_token)):
                    _current_status = _STATUS_EXPTED
                else:
                    _current_status = _STATUS_MISS
            elif ttype in ('LBR', 'LQUOTE'):
                _brackets_count += 1
            elif ttype in ('RBR', 'RQUOTE'):
                _brackets_count -= 1

                if _brackets_count == 0 and (self.__is_eos(_prev_token) or self.MULTI_PUNCT.search(_prev_token)):
                    _current_status = _STATUS_EXPTED
                else:
                    _current_status = _STATUS_MISS
            else:
                if _prev_token:
                    if self.__is_eos(_prev_token) or self.MULTI_PUNCT.search(_prev_token):
                        _current_status = _STATUS_EXPTED
                    elif _prev_ttype in ('RBR', 'RQUOTE'):
                        _current_status = _STATUS_EXPTED
                    elif _prev_ttype == 'QUOTE' and not _inside_quotes:
                        _current_status = _STATUS_EXPTED
                    elif self.ABBR_WITH_POINTS.search(_prev_token) or self.__is_standard_abbr(current_sentence):
                        _current_status = _STATUS_EXPTED
                    elif _current_status == _STATUS_EXPTED and val.istitle():
                        _current_status = _STATUS_SPLIT
                    else:
                        _current_status = _STATUS_MISS
                else:
                    _current_status = _STATUS_MISS

            if _current_status == _STATUS_EXPTED and val[0].isupper():
                _current_status = _STATUS_SPLIT
            else:
                _current_status = _STATUS_MISS

            if _current_status == _STATUS_SPLIT:
                yield ' '.join(current_sentence)
                current_sentence = []

            current_sentence += [val]

            _prev_token = val
            _prev_ttype = ttype

        if current_sentence:
            yield ' '.join(current_sentence)


if __name__ == '__main__':

    test_texts = [
        'Сегодня был чудесный день. Я заполнил в анкете свои Ф.И.О. и наконец понял, что поступил в университет.',
        'Сегодня чудесный день. Я.Ю. Никитенко прогуливался возле дома со своим мопсом.',
        'Сегодня был чудесный день! Я.Ю. Никитенко и Ко прогуливался возле дома со своим мопсом.',
        '«Сегодня был чудесный день!» Я.Ю. Никитенко гулял возле дома с таксой.',
        '"Сегодня был чудесный день!" '
        'Я.Ю. Никитенко прогуливался (И хочу заметить, не один!) '
        'возле дома со своим мопсом.',
        '"Сегодня был чудесный день!" Я.Ю. Никитенко прогуливался со своим мопсом и т. д.',
        'Сегодня был чудесный день и т. д. Я.Ю. Никитенко гулял со своим мопсом.',
        'Сегодня был чудесный день? Я даже и не думал и т. д. и т. п.',
        'Сегодня был чудесный день?!. Ну наадо же..',
        'В 999 г. н.э. Древний Мир уже имел свою историю. Проф. Ивановский к тому времени записал новый альбом.',
        'Сегодня был чудесный день... Не правда ль?..',
        'Какой чудесный день.Какой чудесный пень. Какой чудесный я и песенка моя! Ля-ля-ля!',
        'В фильме снимались: Петя, Вася, Серёга и др. '
        'Сегодня хорошая погода, не правда ль?..'
    ]

    sbd = NaiveSentenceBoundaryDetector()
    for test_text in test_texts:
        for sentence in list(sbd.extract_sentences(test_text)):
            print(sentence)
        print()
