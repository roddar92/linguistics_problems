# -*- coding: utf-8 -*-


class FinnishPredicativeQuestioner(object):
    def __init__(self):
        self.negative = {"MINÄ": "EN", "ME": "EMME",
                         "SINÄ": "ET", "TE": "ETTE",
                         "HÄN": "EI", "HE": "EIVÄT"}

        self.aux_verb = {"MINÄ": "OLEN", "ME": "OLEMME",
                         "SINÄ": "OLET", "TE": "OLETTE",
                         "HÄN": "ON", "HE": "OVAT"}

        self.negative_with_aux_verb = {"EN": "OLEN", "EMME": "OLEMME",
                                       "ET": "OLET", "ETTE": "OLETTE",
                                       "EI": "ON", "EIVÄT": "OVAT"}

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

    def find_person(self, negative):
        for person, neg in self.negative.items():
            if neg == negative:
                return person

    def get_lemma(self, word, person, negative=None):
        if negative:
            if not self.is_single_person(person) and not self.is_plural_person(person):
                if word.endswith("UT"):
                    person = "HÄN"
                elif word.endswith("UT"):
                    person = "HE"
                else:
                    person = self.find_person(negative)

            if word.endswith("EET") or word.endswith("UT"):
                ind = 1 if person == "HE" else 3
                word = "OLI" + self.aux_verb[person][ind:]
            else:
                word = self.aux_verb[person]
        return word + "KO"

    def get_pos_lemma(self, word, negative):
        if word.endswith("EET") or word.endswith("UT"):
            ind = 1 if negative == "EIVÄT" else 3
            aux = self.negative_with_aux_verb[negative]
            return "OLI" + aux[ind:]
        elif word.endswith("OLE"):
            return self.negative_with_aux_verb[negative]
        else:
            return word


    def get_neg_lemma(self, word, person):
        result = []
        if word.startswith("OLI"):
            if self.is_single_person(person) or self.is_plural_person(person):
                result.append(self.negative[person])
                if self.is_single_person(person):
                    result.append("OLUT")
                else:
                    result.append("OLEET")
            else:
                if word[3:] in "VAT MME TTE":
                    result.append("ETTE")
                    result.append("OLEET")
                else:
                    result.append("EI")
                    result.append("OLUT")
        else:
            if self.is_single_person(person) or self.is_plural_person(person):
                result.append(self.negative[person])
            else:
                if word[3:] in "VAT MME TTE":
                    result.append("ETTE")
                else:
                    result.append("EI")
            result.append("OLE")
        return result

    def get_predicative_question(self, sentence):
        sentence = sentence.upper()
        negative = None

        request = []
        for word in sentence.split():
            if self.is_negative_verb(word):
                negative = word
            elif word.endswith("*"):
                word = word[:-1]
                if self.is_aux_verb(word):
                    request.insert(0, (word + "ko").upper())
                else:
                    if negative:
                        normalized = self.get_lemma(word, request[-1], negative)
                    else:
                        normalized = self.get_lemma(word, request[-1])
                    request.insert(0, normalized)
            else:
                request.append(word)

        return " ".join(request) + "?"

    def get_positive_predicative_sentence(self, sentence):
        sentence = sentence.upper()
        words = sentence.split()
        negative = None

        request = []
        for word in words:
            if self.is_negative_verb(word):
                negative = word
            elif word.endswith("*"):
                word = word[:-1]
                if word.endswith("KO"):
                    word = word[:-2]
                request.append(self.get_pos_lemma(word, negative))
            elif word.endswith("?"):
                request.append(word[:-1])
            else:
                request.append(word)

        aux_verb = request[0].split()[0]

        if self.is_aux_verb(aux_verb) or aux_verb.startswith("OLI"):
            request.insert(2, request[0])
            request.remove(request[0])

        return " ".join(request)

    def get_negative_predicative_sentence(self, sentence):
        sentence = sentence.upper()
        words = sentence.split()

        request = []
        for word in words:
            if word.endswith("*"):
                word = word[:-1]
                if word.endswith("KO"):
                    person = words[1]
                    word = word[:-2]
                else:
                    person = request[0]
                request.append(" ".join(self.get_neg_lemma(word, person)))
            elif word.endswith("?"):
                request.append(word[:-1])
            else:
                request.append(word)

        if self.is_negative_verb(request[0].split()[0]):
            request.insert(2, request[0])
            request.remove(request[0])

        return " ".join(request)


if __name__ == "__main__":
    q = FinnishPredicativeQuestioner()
    assert q.get_predicative_question("KISSA ON* KOTONA") == "ONKO KISSA KOTONA?"
    assert q.get_predicative_question("OLEN* SUOMALAINEN") == "OLENKO SUOMALAINEN?"
    assert q.get_predicative_question("HÄN OLI* KOTONA") == "OLIKO HÄN KOTONA?"
    assert q.get_predicative_question("HE OVAT* TÄÄLLÄ") == "OVATKO HE TÄÄLLÄ?"
    assert q.get_predicative_question("HÄN EI OLE* TÄÄLLÄ") == "ONKO HÄN TÄÄLLÄ?"
    assert q.get_predicative_question("ME EMME OLEET* TÄÄLLÄ") == "OLIMMEKO ME TÄÄLLÄ?"
    assert q.get_predicative_question("HE EIVÄT OLEET* TÄÄLLÄ") == "OLIVATKO HE TÄÄLLÄ?"
    assert q.get_predicative_question("OLUT ON* TSEKKILÄISTÄ") == "ONKO OLUT TSEKKILÄISTÄ?"
    assert q.get_predicative_question("OLUT EI OLE* TSEKKILÄISTÄ") == "ONKO OLUT TSEKKILÄISTÄ?"
    assert q.get_predicative_question("OLUT EI OLUT* TSEKKILÄISTÄ") == "OLIKO OLUT TSEKKILÄISTÄ?"
    assert q.get_predicative_question("HÄN EI OLUT* TÄÄLLÄ") == "OLIKO HÄN TÄÄLLÄ?"

    assert q.get_negative_predicative_sentence("OLIKO* HÄN TÄÄLLÄ?") == "HÄN EI OLUT TÄÄLLÄ"
    assert q.get_negative_predicative_sentence("HE OLIVAT* TÄÄLLÄ") == "HE EIVÄT OLEET TÄÄLLÄ"
    assert q.get_negative_predicative_sentence("ONKO* HÄN TÄÄLLÄ?") == "HÄN EI OLE TÄÄLLÄ"
    assert q.get_negative_predicative_sentence("HÄN ON* TÄÄLLÄ?") == "HÄN EI OLE TÄÄLLÄ"

    assert q.get_positive_predicative_sentence("OLIKO* HÄN KOTONA?") == "HÄN OLI KOTONA"
    assert q.get_positive_predicative_sentence("HÄN EI OLUT* TÄÄLLÄ") == "HÄN OLI TÄÄLLÄ"
    assert q.get_positive_predicative_sentence("OVATKO* HE TÄÄLLÄ?") == "HE OVAT TÄÄLLÄ"
    assert q.get_positive_predicative_sentence("HE EIVÄT OLE* TÄÄLLÄ") == "HE OVAT TÄÄLLÄ"
    assert q.get_positive_predicative_sentence("HE EIVÄT OLEET* TÄÄLLÄ") == "HE OLIVAT TÄÄLLÄ"
