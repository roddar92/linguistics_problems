# -*- coding: utf-8 -*-

""" This Questioner can generate questions to verbs of Present Simple,
    Past Simple and Present Future Tenses """


class Questioner(object):
    def __init__(self):
        self.irregular_verbs = {}
        with open("irregular_verbs.txt", "r") as f:
            for line in f:
                infinit, irreg_verb, _ = line.strip().split()
                self.irregular_verbs[irreg_verb.upper()] = infinit.upper()

    @staticmethod
    def is_aux_verb(word):
        return word.upper() in "AM IS ARE WAS WERE".split()

    def is_irregular_verb(self, word):
        return word in self.irregular_verbs

    @staticmethod
    def is_have_verb(word):
        return word.upper() in "HAS HAVE".split()

    @staticmethod
    def is_modal_verb(word):
        return word.upper() in "CAN COULD MAY MUST OUGHT SHOULD WOULD".split()

    @staticmethod
    def is_future_verb(word):
        return word.upper() in "SHALL WILL".split()

    @staticmethod
    def is_verb_with_ll(word):
        return word.upper() in "FILL PULL".split()

    def get_question_word(self, word):
        if self.is_irregular_verb(word) or word.endswith("ED"):
            return "DID"
        elif self.is_negative_verb(word):
            return word
        elif word != self.get_verb_lemma(word):
            return 'DOES'
        else:
            return 'DO'

    @staticmethod
    def has_es_ending(word):
        return word[-3] in 'AEIOUHSYXZ'

    @staticmethod
    def has_ie_ending(word):
        return word in "UNDERLIE UNTIE".split()

    @staticmethod
    def has_i_ending(word):
        return word == "SKI"

    @staticmethod
    def has_c_ending(word):
        return word in "BIVOUAC FROLIC MIMIC PANIC PICNIC TRAFFIC".split()

    @staticmethod
    def has_double_consonants(word):
        return word[-4:-2] in "BB GG LL PP TT RR".split()

    @staticmethod
    def has_double_consonants_endings(word):
        return word[-4:-2] in "SS ZZ CH SH".split()

    @staticmethod
    def has_it_et_endings(word):
        return word[-4:-2] in "IT ET".split()

    @staticmethod
    def has_two_vowels(word):
        return word[-5] in 'AEIOU' and word[-4] in 'AEIOU'

    @staticmethod
    def has_ee_oe_ye_endings(word):
        return word[-3:-1] in 'EE OE YE'.split()

    @staticmethod
    def has_not_pronounced_e_ending(word):
        return word[-3] in 'BDGKLTZ'

    @staticmethod
    def is_negative_verb(word):
        return word.endswith("N'T") or word.endswith("NOT")

    def get_verb_lemma(self, word):
        word = word.upper()
        if self.is_irregular_verb(word):
            return self.irregular_verbs[word]
        elif word[:-1].endswith("IE"):
            if self.has_i_ending(word[:-2]):
                return word[:-2]
            elif len(word[:-3]) <= 1 or self.has_ie_ending(word[:-1]):
                return word[:-1]
            else:
                return word[:-3] + "Y"
        elif self.has_ee_oe_ye_endings(word):
            if word[:-2].endswith("OY"):
                return word[:-2]
            elif word[:len(word)-2] in 'GO DO'.split():
                return word[:-2]
            else:
                return word[:-1]
        elif self.is_verb_with_ll(word[:-2]):
            return word[:-2]
        elif self.has_double_consonants(word) or self.has_c_ending(word[:-3]):
            return word[:-3]
        elif self.has_double_consonants_endings(word):
            return word[:-2]
        elif word.endswith('S') and not word.endswith('SS'):
            return word[:-1]
        elif word.endswith('ED') or word.endswith('ES'):
            if self.has_it_et_endings(word):
                return word[:-2]
            elif self.has_two_vowels(word):
                return word[:-2]
            elif self.has_not_pronounced_e_ending(word):
                return word[:-1]
            else:
                return word[:-2]
        else:
            return word

    def request(self, statement):
        request = []
        for word in statement.strip().upper().split():
            if word.endswith('*'):
                word = word[:-1]
                if self.is_aux_verb(word) or self.is_modal_verb(word) or self.is_future_verb(word):
                    request.insert(0, word)
                else:
                    if self.is_negative_verb(word):
                        request.insert(0, self.get_question_word(word))
                    else:
                        request.insert(0, self.get_question_word(word))
                        request.append(self.get_verb_lemma(word))
            else:
                request.append(word)
        return ' '.join(request) + '?'


if __name__ == "__main__":
    q = Questioner()
    assert q.request("KATE GOES* TO SCHOOL") == "DOES KATE GO TO SCHOOL?"
    assert q.request("ERIC WENT* TO SCHOOL") == "DID ERIC GO TO SCHOOL?"
    assert q.request("ALEX IS* TALL") == "IS ALEX TALL?"
    assert q.request("WINTER USUALLY COMES* LATE") == "DOES WINTER USUALLY COME LATE?"
    assert q.request("STUDENTS OFTEN COME* LATE") == "DO STUDENTS OFTEN COME LATE?"
    assert q.request("TOM CAN* SWIM") == "CAN TOM SWIM?"
    assert q.request("I HAVE* A CAR") == "DO I HAVE A CAR?"
    assert q.request("I WORRY* ABOUT THE TEST") == "DO I WORRY ABOUT THE TEST?"
    assert q.request("SHE WORRIES* ABOUT THE TEST") == "DOES SHE WORRY ABOUT THE TEST?"
    assert q.request("LIBRARY OF CONGRESS POSSESSES* BOOKS") == "DOES LIBRARY OF CONGRESS POSSESS BOOKS?"
    assert q.request("I MISS* MY DOG") == "DO I MISS MY DOG?"
    assert q.request("THEY FIX* EVERYTHING") == "DO THEY FIX EVERYTHING?"
    assert q.request("SARAH WAS* IN SCHOOL EVERY DAY") == "WAS SARAH IN SCHOOL EVERY DAY?"
    assert q.request("THEY WERE* IN LONDON") == "WERE THEY IN LONDON?"
    assert q.request("MAX IS* READING NOW") == "IS MAX READING NOW?"
    assert q.request("ANDREW WATCHES* TV") == "DOES ANDREW WATCH TV?"
    assert q.request("PETER CATCHES* THE BUTTERFLY") == "DOES PETER CATCH THE BUTTERFLY?"
    assert q.request("ANDREW WATCHED* TV") == "DID ANDREW WATCH TV?"
    assert q.request("ANDREW CRASHES* HIS CAR") == "DOES ANDREW CRASH HIS CAR?"
    assert q.request("DANIEL COPIES* THE DOCUMENT") == "DOES DANIEL COPY THE DOCUMENT?"
    assert q.request("EMILIA APPLIES* FOR A GRANT") == "DOES EMILIA APPLY FOR A GRANT?"
    assert q.request("ANDREW BUYS* THE SCOOTER TO HIS SISTER") == "DOES ANDREW BUY THE SCOOTER TO HIS SISTER?"
    assert q.request("ANN SKIES* IN THE GARDEN") == "DOES ANN SKI IN THE GARDEN?"
    assert q.request("ANDREW'S SISTER KISSES* HIM TO THE CHEEKS") == "DOES ANDREW'S SISTER KISS HIM TO THE CHEEKS?"
    assert q.request("ANDREW'S SISTER KISSED* HIM TO THE CHEEKS") == "DID ANDREW'S SISTER KISS HIM TO THE CHEEKS?"
    assert q.request("YOU DIE* IN THE WAR") == "DO YOU DIE IN THE WAR?"
    assert q.request("HE ALWAYS LIES* TO HIS PARENTS") == "DOES HE ALWAYS LIE TO HIS PARENTS?"
    assert q.request("HE DIES* IN THE WAR") == "DOES HE DIE IN THE WAR?"
    assert q.request("THE LITTLE BEE BUZZES* OVER MY HEAD") == "DOES THE LITTLE BEE BUZZ OVER MY HEAD?"
    assert q.request("MICHAEL PLAYS* FOOTBALL") == "DOES MICHAEL PLAY FOOTBALL?"
    assert q.request("EDWARD ENJOYS* HIS PLAY") == "DOES EDWARD ENJOY HIS PLAY?"
    assert q.request("MARY CRIES* IN THE SANDBOX") == "DOES MARY CRY IN THE SANDBOX?"
    assert q.request("SAM LIKES* BIKE") == "DOES SAM LIKE BIKE?"
    assert q.request("PAUL DOES* HIS HOMEWORK") == "DOES PAUL DO HIS HOMEWORK?"
    assert q.request("WILLY WRITES* THE LETTER") == "DOES WILLY WRITE THE LETTER?"
    assert q.request("JANE DYES* HAIR") == "DOES JANE DYE HAIR?"
    assert q.request("PETER CAN* SWIM VERY WELL") == "CAN PETER SWIM VERY WELL?"
    assert q.request("YOU WOULD* OPEN THE DOOR") == "WOULD YOU OPEN THE DOOR?"
    assert q.request("I WILL* GO ABROAD TOMORROW") == "WILL I GO ABROAD TOMORROW?"
    assert q.request("NICOLAS WROTE* THE LETTER") == "DID NICOLAS WRITE THE LETTER?"
    assert q.request("MARY SMILED* TO ME") == "DID MARY SMILE TO ME?"
    assert q.request("TED TRAVELLED* IN ASIA") == "DID TED TRAVEL IN ASIA?"
    assert q.request("MARY ENJOYED* THE TRIP") == "DID MARY ENJOY THE TRIP?"
    assert q.request("TIM PICNICKED* ON THE BEACH") == "DID TIM PICNIC ON THE BEACH?"
    assert q.request("ANDREW COPIED* THE DOCUMENT") == "DID ANDREW COPY THE DOCUMENT?"
    assert q.request("THOMAS SCALED* THE MATRIX") == "DID THOMAS SCALE THE MATRIX?"
    assert q.request("ANDY STOPPED* HIS CAR") == "DID ANDY STOP HIS CAR?"
    assert q.request("TIM CHANGED* HIS LAST NAME") == "DID TIM CHANGE HIS LAST NAME?"
    assert q.request("KING FREED* THE PRISONER") == "DID KING FREE THE PRISONER?"
    assert q.request("QUEEN VISITED* THE HOSPITAL") == "DID QUEEN VISIT THE HOSPITAL?"
    assert q.request("QUEEN ORGANIZED* THE FESTIVAL") == "DID QUEEN ORGANIZE THE FESTIVAL?"
    assert q.request("DOCTOR TREATED* HIS PATIENTS") == "DID DOCTOR TREAT HIS PATIENTS?"
    assert q.request("HELEN BAKED* CAKES YESTERDAY") == "DID HELEN BAKE CAKES YESTERDAY?"
    assert q.request("HELEN MET* HER FATHER IN THE AIRPORT YESTERDAY") == "DID HELEN MEET HER FATHER IN THE AIRPORT YESTERDAY?"
    assert q.request("I FILLED* UP THE BOTTLE WITH WATER") == "DID I FILL UP THE BOTTLE WITH WATER?"
    assert q.request("SAM DOSEN'T* LIKE BIKE") == "DOSEN'T SAM LIKE BIKE?"
    assert q.request("I WOULDN'T* LIKE A CUP OF COFFEE") == "WOULDN'T I LIKE A CUP OF COFFEE?"
