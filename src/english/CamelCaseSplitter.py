import re


class CamelCaseSplitter:
    def __init__(self):
        self.other = re.compile(r'^(\d|[^a-zа-яё])$', re.IGNORECASE)

    def split(self, text):
        _start = 0
        _is_upper = 1
        _is_lower = 2
        _other = 3

        curr_state = _start
        answer = []
        word = ''
        for ch in text:
            if ch.isupper():
                if curr_state in [_is_lower, _other, _start]:
                    if word:
                        answer += [word]
                        word = ''
                    curr_state = _is_upper
                word += ch
            elif ch.islower():
                if curr_state in [_is_upper, _other, _start]:
                    if word.isupper() and len(word) > 1:
                        answer += [word[:-1]]
                        word = word[-1] + ch
                    elif word and not word.isupper():
                        answer += [word]
                        word = ch
                    else:
                        word += ch
                    curr_state = _is_lower
                else:
                    word += ch
            else:
                if self.other.match(ch) and curr_state != _other:
                    if word:
                        answer += [word]
                        word = ''
                    curr_state = _other
                word += ch

        if word:
            answer += [word]
            del word

        return answer


if __name__ == "__main__":
    ccs = CamelCaseSplitter()
    assert ccs.split('TypeOfWord') == ['Type', 'Of', 'Word']
    assert ccs.split('formOfVerb') == ['form', 'Of', 'Verb']
    assert ccs.split('WordHTML') == ['Word', 'HTML']
    assert ccs.split('eHTML') == ['e', 'HTML']
    assert ccs.split('HTMLPage') == ['HTML', 'Page']
    assert ccs.split('TypeHTMLWord') == ['Type', 'HTML', 'Word']
    assert ccs.split('MultipleHTML4VerbsHandler') == ['Multiple', 'HTML', '4', 'Verbs', 'Handler']
    assert ccs.split('Type4HTMLWord') == ['Type', '4', 'HTML', 'Word']
    assert ccs.split('Type123Word') == ['Type', '123', 'Word']
    assert ccs.split('123Type4Word') == ['123', 'Type', '4', 'Word']
    assert ccs.split('123type4word') == ['123', 'type', '4', 'word']
    assert ccs.split('type4THEWord') == ['type', '4', 'THE', 'Word']
    assert ccs.split('helloWorld') == ['hello', 'World']
    assert ccs.split('hello-MyWorld') == ['hello', '-', 'My', 'World']
