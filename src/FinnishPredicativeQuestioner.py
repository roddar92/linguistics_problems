# -*- coding: utf-8 -*-

class FinnishPredicativeQuestioner(object):
    def __init__(self):
        self.negative = {"MINÄ": "EN", "ME": "EMME",
                         "SINÄ": "ET", "TE": "ETTE",
                         "HÄN": "EI", "HE": "EIVÄT"}

        self.aux_verb = {"MINÄ": "OLEN", "ME": "OLEMME",
                         "SINÄ": "OLET", "TE": "OLETTE",
                         "HÄN": "ON", "HE": "OVAT"}

    @staticmethod
    def is_finnish_vowel(symbol):
        return symbol in "AÄEIOÖUY"

    @staticmethod
    def is_finnish_consonant(symbol):
        return symbol in "BCDFGHJKLMNPQRSTVWXZ"

    @staticmethod
    def is_single_person(word):
        return word in "MINÄ SINÄ HÄN".split()

    @staticmethod
    def is_plural_person(word):
        return word in "ME TE HE".split()

    @staticmethod
    def is_aux_verb(verb):
        return verb in "OLEN OLEMME OLET OLETTE ON OVAT".split()

    @staticmethod
    def is_negative_verb(verb):
        return verb in "EN EMME ET ETTE EI EIVÄT".split()

    def get_lemma(self, word, person, negative=False):
        if negative:
            if word.endswith("EET") or word.endswith("UT"):
                word = "OLI" + self.aux_verb[person][1:] if person == "HE" else "OLI" + self.aux_verb[person][3:]
            else:
                word = self.aux_verb[person]
        return word + "KO"


    def predicative_question(self, sentence):
        sentence = sentence.upper()
        negative = False

        request = []
        for word in sentence.split():
            if self.is_negative_verb(word):
                negative = True
            elif word.endswith("*"):
                word = word[:-1]
                if self.is_aux_verb(word):
                    request.insert(0, (word + "ko").upper())
                else:
                    normalized = self.get_lemma(word, request[0], negative) if negative else self.get_lemma(word, request[0])
                    request.insert(0, normalized)
            else:
                request.append(word)

        return " ".join(request) + "?"


if __name__ == "__main__":
    q = FinnishPredicativeQuestioner()
    assert q.predicative_question("KISSA ON* KOTONA") == "ONKO KISSA KOTONA?"
    assert q.predicative_question("OLEN* SUOMALAINEN") == "OLENKO SUOMALAINEN?"
    assert q.predicative_question("HÄN OLI* KOTONA") == "OLIKO HÄN KOTONA?"
    assert q.predicative_question("HE OVAT* TÄÄLLÄ") == "OVATKO HE TÄÄLLÄ?"
    assert q.predicative_question("HÄN EI OLE* TÄÄLLÄ") == "ONKO HÄN TÄÄLLÄ?"
    assert q.predicative_question("ME EMME OLEET* TÄÄLLÄ") == "OLIMMEKO ME TÄÄLLÄ?"
    assert q.predicative_question("HE EIVÄT OLEET* TÄÄLLÄ") == "OLIVATKO HE TÄÄLLÄ?"
    assert q.predicative_question("HÄN EI OLUUT* TÄÄLLÄ") == "OLIKO HÄN TÄÄLLÄ?"