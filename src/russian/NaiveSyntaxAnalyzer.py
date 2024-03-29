import string

import pymystem3
from collections import namedtuple


class GrammemeExtractor:
    def __init__(self):
        self.__analyzer = pymystem3.Mystem()

    @staticmethod
    def create_base_token():
        return namedtuple('Token', ('Value', 'Grammems'))

    def extract_grammems(self, sentence):
        grammems = []

        self.__analyzer.start()
        for part in self.__analyzer.analyze(sentence):
            word, gram = '', ''
            if 'analysis' in part and part['analysis'] is not None:
                grammems_set = part['analysis'][0]['gr']
                # print(grammems_set)
                gram = grammems_set.split('|', 1)[0]
                gram = gram.replace('(', '')
                gram = gram.replace(')', '')

            if 'text' in part:
                word = part['text']

            if not word.isspace():
                token = self.create_base_token()
                grammems += [token(word, gram)]

                self.__analyzer.close()

        return grammems


class Chunker:
    PHRASE_TYPES = ['NP', 'VP', 'ALL']

    @staticmethod
    def __extract_phrase_grammes(phrase):
        if not phrase:
            return ''
        i = -1
        while i + len(phrase) > 0 and not phrase[-1].Grammems:
            i -= 1
        return phrase[i].Grammems

    @staticmethod
    def __get_phrase_type(grams):
        if 'S,' in grams or 'S=' in grams or 'прич,' in grams:
            return 'NP'
        elif 'V' in grams and 'ADV' not in grams:
            return 'VP'
        else:
            return 'OTHER'

    @staticmethod
    def create_base_phrase():
        return namedtuple('Phrase', ('Type', 'Text', 'Grammems'))

    @staticmethod
    def __get_pos_tags(tokens):
        pos_tags = []
        for token in tokens:
            if not token.Grammems and token.Value.strip() in string.punctuation:
                pos_tags += ['PUNCT']
            else:
                token_grammems = token.Grammems
                eq_index = token_grammems.find('=')
                comma_index = token_grammems.find(',')

                if eq_index > 0 and comma_index > 0:
                    delimiter = token_grammems[min(eq_index, comma_index)]
                elif eq_index > 0:
                    delimiter = '='
                elif comma_index > 0:
                    delimiter = ','
                else:
                    delimiter = ''

                if delimiter:
                    pos_tags += [token_grammems.split(delimiter)[0]]
        return pos_tags

    @staticmethod
    def __was_apro_in_pos(pos_tags, i, dist):
        return any(pos_tags[j] == 'APRO' for j in range(i - dist, i))

    def __update_phrases(self, phrases_array, curr_phrase):
        txt = ' '.join(tok.Value for tok in curr_phrase)
        gram = self.__extract_phrase_grammes(curr_phrase)
        ph_type = self.__get_phrase_type(gram)

        if txt and gram:
            tok = self.create_base_phrase()
            phrases_array += [tok(ph_type, txt, gram)]
        return phrases_array

    def reduce_sentence(self, tagged_tokens):
        phrases = []
        current_phrase = []

        pos_tags = self.__get_pos_tags(tagged_tokens)

        i = 0
        while i < len(tagged_tokens):
            token = tagged_tokens[i]

            if current_phrase:
                last_token = current_phrase[-1]
            else:
                last_token = GrammemeExtractor.create_base_token()('', '')

            if i >= len(pos_tags):
                break

            if pos_tags[i] == 'PR':
                current_phrase += [token]
                i += 1
            elif pos_tags[i] == 'S':
                while i < len(pos_tags) and pos_tags[i] == 'S':
                    token = tagged_tokens[i]
                    if current_phrase:
                        last_token = current_phrase[-1]
                    if pos_tags[i] == 'S' and 'им,' in token.Grammems and 'им,' not in last_token.Grammems:
                        phrases = self.__update_phrases(phrases, current_phrase)
                        current_phrase = [token]
                    else:
                        current_phrase += [token]
                    i += 1
            elif pos_tags[i] in 'A APRO'.split() or (pos_tags[i] == 'V' and 'прич,' in token.Grammems):
                if current_phrase and i > 0 and pos_tags[i - 1] not in 'A APRO PR':
                    phrases = self.__update_phrases(phrases, current_phrase)
                    current_phrase = [token]
                    i += 1

                while i < len(pos_tags) and \
                        (pos_tags[i] in 'A APRO S CONJ'.split() or (pos_tags[i] == 'V' and 'прич,' in token.Grammems)):
                    token = tagged_tokens[i]
                    current_phrase += [token]
                    i += 1

                phrases = self.__update_phrases(phrases, current_phrase)
                current_phrase = []
            elif pos_tags[i] in 'V ADV'.split():
                if current_phrase and i > 0 and pos_tags[i - 1] != 'V':
                    phrases = self.__update_phrases(phrases, current_phrase)
                    current_phrase = [token]
                    i += 1

                while i < len(pos_tags) and pos_tags[i] in 'V ADV CONJ'.split():
                    token = tagged_tokens[i]
                    current_phrase += [token]
                    i += 1

                phrases = self.__update_phrases(phrases, current_phrase)
                current_phrase = []
            elif pos_tags[i] == 'PUNCT' and token.Value.strip() == ',':
                while i < len(pos_tags) and \
                        (pos_tags[i] in 'A APRO S CONJ PUNCT'.split() or
                         (pos_tags[i] == 'V' and ('прич,' in token.Grammems or self.__was_apro_in_pos(pos_tags, i, 3)))):
                    token = tagged_tokens[i]
                    current_phrase += [token]
                    i += 1

                phrases = self.__update_phrases(phrases, current_phrase)
                current_phrase = []
            else:
                if token.Value.strip() != '.':
                    current_phrase += [token]
                i += 1

        if current_phrase:
            phrases = self.__update_phrases(phrases, current_phrase)

        return phrases

    # def chunk(self, tagged_tokens, phrase_type='ALL'):
    #    assert phrase_type in self.PHRASE_TYPES
    #    pass


if __name__ == '__main__':

    texts = [
        'На освещённой солнцем поляне жил слон, который был розовым.',
        'Володя хочет съесть мороженое.',
        'После отставки мужа Марья Ивановна ушла в благотворительный фонд.',
        'На солнечной поляне жил розовый слон.',
        'Маруся всё поёт да пляшет.'
    ]

    extractor = GrammemeExtractor()
    chunker = Chunker()

    for text in texts:
        token_stream = extractor.extract_grammems(text)
        print(token_stream)
        phrase_stream = chunker.reduce_sentence(token_stream)
        print(phrase_stream)
