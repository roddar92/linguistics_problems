import re


class CamelCaseSplitter:
    def __init__(self):
        self.other = re.compile(r'^(\d|[^a-zа-яё])$', re.IGNORECASE)

    def split(self, text):
        _start, _is_upper, _is_lower, _other = range(4)

        curr_state = _start
        word = ''
        for ch in text:
            if ch.isupper():
                if curr_state in (_is_lower, _other, _start):
                    if word:
                        yield word
                        word = ''
                    curr_state = _is_upper
                word += ch
            elif ch.islower():
                if curr_state in (_is_upper, _other, _start):
                    if word.isupper() and len(word) > 1:
                        yield word[:-1]
                        word = word[-1] + ch
                    elif word and not word.isupper():
                        yield word
                        word = ch
                    else:
                        word += ch
                    curr_state = _is_lower
                else:
                    word += ch
            else:
                if self.other.match(ch) and curr_state != _other:
                    if word:
                        yield word
                        word = ''
                    curr_state = _other
                word += ch

        if word:
            yield word


if __name__ == "__main__":
    ccs = CamelCaseSplitter()

    test_pairs = [
        ('TypeOfWord', ['Type', 'Of', 'Word']),
        ('formOfVerb', ['form', 'Of', 'Verb']),
        ('WordHTML', ['Word', 'HTML']),
        ('eHTML', ['e', 'HTML']),
        ('HTMLPage', ['HTML', 'Page']),
        ('TypeHTMLWord', ['Type', 'HTML', 'Word']),
        ('MultipleHTML4VerbsHandler', ['Multiple', 'HTML', '4', 'Verbs', 'Handler']),
        ('Type4HTMLWord', ['Type', '4', 'HTML', 'Word']),
        ('Type123Word', ['Type', '123', 'Word']),
        ('123Type4Word', ['123', 'Type', '4', 'Word']),
        ('123type4word', ['123', 'type', '4', 'word']),
        ('type4THEWord', ['type', '4', 'THE', 'Word']),
        ('helloWorld', ['hello', 'World']),
        ('hello-MyWorld', ['hello', '-', 'My', 'World'])
    ]

    for arg, expected in test_pairs:
        assert list(ccs.split(arg)) == expected
