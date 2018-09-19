import re
from src.russian.NaiveTokenizer import NaiveTokenizer


class NaiveSentenceBoundaryDetector(object):
    def __init__(self):
        # self.EMJOI
        self.EOS = '.?!'
        self.ABBR_WITH_POINTS = re.compile(r'([A-ZА-Я]\.){3,}')
        self.tokenizer = NaiveTokenizer()

    def is_eos(self, previous_token):
        return previous_token in ['...'] + list(self.EOS)

    def extract_sentences(self, text):
        _STATUS_START = 0
        _STATUS_SPLIT = 1
        _STATUS_MISS = 2
        _brackets_count = 0
        _inside_quotes = False

        _current_status = _STATUS_START
        _prev_token = ''

        sentences = []
        current_sentence = []
        for token in self.tokenizer.tokenize(text):
            val = token.Value
            if token.Type not in ['WORD', 'DIGIT', 'URL', 'QUOTE', 'LBR', 'LQUOTE', 'RBR', 'RQUOTE']:
                if val in self.EOS or val == '...':
                    if val in ['...', '?', '!']:
                        _current_status = _STATUS_MISS
                    elif val == '.':
                        if len(_prev_token) <= 1:
                            _current_status = _STATUS_MISS
                        else:
                            _current_status = _STATUS_SPLIT
            elif token.Type == 'QUOTE':
                _inside_quotes = not _inside_quotes

                if not _inside_quotes and self.is_eos(_prev_token):
                    _current_status = _STATUS_SPLIT
                else:
                    _current_status = _STATUS_MISS
            elif token.Type in ['LBR', 'LQUOTE']:
                _brackets_count += 1
            elif token.Type in ['RBR', 'RQUOTE']:
                _brackets_count -= 1

                if _brackets_count == 0 and self.is_eos(_prev_token) and val.istitle():
                    _current_status = _STATUS_SPLIT
                else:
                    _current_status = _STATUS_MISS
            else:
                if _prev_token:
                    if _prev_token in self.EOS and val.istitle():
                        _current_status = _STATUS_SPLIT
                    elif self.ABBR_WITH_POINTS.search(_prev_token) and val.istitle():
                        _current_status = _STATUS_SPLIT
                    else:
                        _current_status = _STATUS_MISS

            current_sentence += [val]
            _prev_token = val

            if _current_status == _STATUS_SPLIT:
                sentences += [' '.join(current_sentence)]
                current_sentence = []
                _current_status = _STATUS_MISS

        return sentences


if __name__ == '__main__':
    sbd = NaiveSentenceBoundaryDetector()
    print(sbd.extract_sentences(
        'Сегодня был чудесный день. Я заполнил в анкете свои Ф.И.О. и наконец понял, что поступил в университет.'))
    print(sbd.extract_sentences('Сегодня был чудесный день! Я.Ю. Никитенко прогуливался возле дома со своим мопсом.'))
    print(sbd.extract_sentences('"Сегодня был чудесный день!" Я.Ю. Никитенко прогуливался возле дома со своим мопсом.'))
    print(sbd.extract_sentences('"Сегодня был чудесный день!" Я.Ю. Никитенко прогуливался (И хочу заметить, не один!) возле дома со своим мопсом.'))
