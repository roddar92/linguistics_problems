# -*- coding: utf-8 -*-
class SwedenNounLemmatizer:
    ARTICLE = {
        'n': 'en', 't': 'ett'
    }

    def __init__(self):
        self.irregular_nouns = {}
        with open("resources/irregular_nouns.txt", "r") as f:
            for line in f:
                norm, plural = line.strip().split()
                self.irregular_nouns[plural] = norm

    def get_lemma(self, word, is_plural=False):
        word = word.lower()
        if not is_plural:
            last = word[-1]
            before = word[-2]
            if before == 'e':
                if (word[:-2].endswith('nn') or word[:-2].endswith('mm')) and word not in ('kranen', 'sonen'):
                    return f'{self.ARTICLE[last]} {word[:-3]}'
                elif word[-3] in 'fk' or word[-4:-2] == 'pl':
                    return f'{self.ARTICLE[last]} {word[:-1]}'
                else:
                    return f'{self.ARTICLE[last]} {word[:-2]}'
            lemma = word[:-2] if before == 'e' and last == 'n' else word[:-1]
            return f'{self.ARTICLE[last]} {lemma}'
        else:
            if word in self.irregular_nouns:
                return self.irregular_nouns[word]
            elif word.endswith('erna'):
                return word[:-4]
            elif word.endswith('larna'):
                return word[:-5] + 'el'
            return word[:-2] + 'a' if word.endswith('or') else word[:-4]


if __name__ == "__main__":
    q = SwedenNounLemmatizer()
    assert q.get_lemma("mödrar", is_plural=True) == "mor"
    assert q.get_lemma("skolan") == "en skola"
    assert q.get_lemma("katterna", is_plural=True) == "katt"
    assert q.get_lemma("katten") == "en katt"
    assert q.get_lemma("kaffet") == "ett kaffe"
    assert q.get_lemma("systern") == "en syster"
    assert q.get_lemma("pojken") == "en pojke"
    assert q.get_lemma("sängen") == "en säng"
    assert q.get_lemma("sockeret") == "ett socker"
    assert q.get_lemma("tomaten") == "en tomat"
    assert q.get_lemma("gaffeln") == "en gaffel"
    assert q.get_lemma("faglarna", is_plural=True) == "fagel"
    assert q.get_lemma("äpplet") == "ett äpple"
    assert q.get_lemma("barnet") == "ett barn"
    assert q.get_lemma("älgen") == "en älg"
    assert q.get_lemma("rummet") == "ett rum"
