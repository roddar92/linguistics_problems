import re
from src.russian.NaiveTokenizer import NaiveTokenizer


class NaiveSentenceBoundaryDetector(object):
    def __init__(self):
        # self.EMJOI
        self.EOS = '.?!'
        self.MULTI_PUNCT = re.compile(r'([.?!]){2,}')
        self.ABBR_WITH_POINTS = re.compile(r'([A-ZА-Я]\.){3,}')
        self.tokenizer = NaiveTokenizer()

    def is_eos(self, previous_token):
        return previous_token in ['...'] + list(self.EOS)

    @staticmethod
    def is_standard_abbr(current_sentence):
        if len(current_sentence) >= 3 and re.search(r'и т\. [дп]\.', ' '.join(current_sentence[-3:])):
            return True
        elif len(current_sentence) >= 2 and re.search(r'и [дп]р\.', ' '.join(current_sentence[-3:])):
            return True
        else:
            return False

    def extract_sentences(self, text):

        def split_sentence(sentences_list, curr_sentence):
            sentences_list += [' '.join(curr_sentence)]
            curr_sentence[:] = []

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
                if val in self.EOS or self.MULTI_PUNCT.search(val):
                    if val in '?!' or self.MULTI_PUNCT.search(val):
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
                    if (_prev_token in self.EOS or self.MULTI_PUNCT.search(_prev_token)) and val.istitle():
                        if _current_status == _STATUS_MISS:
                            _current_status = _STATUS_SPLIT
                            split_sentence(sentences, current_sentence)
                            _current_status = _STATUS_MISS
                        else:
                            _current_status = _STATUS_MISS
                    elif (self.ABBR_WITH_POINTS.search(_prev_token) or self.is_standard_abbr(current_sentence)) \
                            and val.istitle():
                        _current_status = _STATUS_SPLIT
                        split_sentence(sentences, current_sentence)
                        _current_status = _STATUS_MISS
                    else:
                        _current_status = _STATUS_MISS
                else:
                    _current_status = _STATUS_MISS

            current_sentence += [val]
            _prev_token = val

            if _current_status == _STATUS_SPLIT:
                split_sentence(sentences, current_sentence)

        if current_sentence:
            split_sentence(sentences, current_sentence)
        return sentences


if __name__ == '__main__':
    sbd = NaiveSentenceBoundaryDetector()
    print(sbd.extract_sentences('Сегодня был чудесный день. Я заполнил в анкете свои Ф.И.О. '
                                'и наконец понял, что поступил в университет.'))
    print(sbd.extract_sentences('Сегодня был чудесный день! Я.Ю. Никитенко прогуливался возле дома со своим мопсом.'))
    print(sbd.extract_sentences('"Сегодня был чудесный день!" Я.Ю. Никитенко прогуливался возле дома со своим мопсом.'))
    print(sbd.extract_sentences('"Сегодня был чудесный день!" '
                                'Я.Ю. Никитенко прогуливался (И хочу заметить, не один!) '
                                'возле дома со своим мопсом.'))
    print(sbd.extract_sentences('"Сегодня был чудесный день!" Я.Ю. Никитенко прогуливался со своим мопсом и т. д.'))
    print(sbd.extract_sentences('Сегодня был чудесный день и т. д. Я.Ю. Никитенко прогуливался со своим мопсом.'))
    print(sbd.extract_sentences('Сегодня был чудесный день? Я даже и не думал и т. д. и т. п.'))
    print(sbd.extract_sentences('Сегодня был чудесный день?!. Ну наадо же..'))
    print(sbd.extract_sentences('Сегодня был чудесный день... Не правда ль?..'))
