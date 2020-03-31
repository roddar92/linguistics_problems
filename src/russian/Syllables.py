# -*- coding: utf-8 -*-
class SyllableModule(object):

    def syllables(self, word):
        """Return list of the word syllables"""
        pass

    def syllables_count(self, word):
        """Return count of thw word syllables"""
        pass


class RussianSyllableModule(SyllableModule):
    _RU_ALPHABET = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"
    _RU_VOWELS = "аеёиоуыэюя"
    _RU_CONSONANTS = "".join(set(_RU_ALPHABET) - set(_RU_VOWELS))

    def __is_russian_double_consonants(self, seq):
        return len(seq) == 2 and self.__is_russian_consonant(seq[-1]) and seq[0] == seq[-1]

    @staticmethod
    def __is_russian_sonour(symbol):
        return symbol not in 'лмнр'

    @staticmethod
    def __is_russian_reflexive_suffix(seq):
        return seq in 'сь ся'.split()

    def __is_vowel(self, symbol):
        return symbol in self._RU_VOWELS

    def __is_russian_consonant(self, symbol):
        return symbol in self._RU_CONSONANTS

    def syllables_count(self, word):
        """Return count of the word syllables"""
        word = word.lower()
        cnt = 0
        for letter in word:
            if self.__is_vowel(letter):
                cnt += 1

        return cnt

    def syllables(self, word):
        """Return list of the word syllables"""
        word = word.lower()

        syllables = []
        cur_syllable = []

        for _, letter in enumerate(word):
            cur_syllable += [letter]
            if self.__is_vowel(letter):
                syllables.append(''.join(cur_syllable))
                cur_syllable = []
            if syllables:
                if self.__is_russian_reflexive_suffix(syllables[-1]):
                    last = syllables.pop()
                    prelast = syllables.pop()
                    if prelast.endswith('т'):
                        ind = -1
                    elif prelast.endswith('ть'):
                        ind = -2
                    else:
                        ind = len(prelast)
                    syllables.append(prelast[:ind])
                    syllables.append(prelast[ind:] + last)
                elif letter in "ьъ" or self.__is_vowel(syllables[-1][-1]) and letter == "й":
                    last = syllables.pop()
                    syllables.append(last + ''.join(cur_syllable))
                    cur_syllable = []
                elif len(cur_syllable) >= 2 and self.__is_russian_consonant(letter) and \
                        not (self.__is_russian_sonour(cur_syllable[0]) or
                             self.__is_russian_double_consonants(cur_syllable)):
                    last = syllables.pop()
                    syllables.append(last + cur_syllable[0])
                    cur_syllable.pop(0)

        if cur_syllable:
            last = syllables.pop()
            syllables.append(last + ''.join(cur_syllable[:]))

        return syllables


class FinnishSyllableModule(SyllableModule):
    _FI_VOWELS = "aäeioöuy"

    @staticmethod
    def __is_diphthong(vowels):
        return vowels in "ai äi oi öi ui yi ei au ou eu iu äy öy ie uo yö".split()

    @staticmethod
    def __is_double_vowel(vowels):
        return vowels[-1] == vowels[-2]

    def __is_vowel(self, symbol):
        return symbol in self._FI_VOWELS

    def __contains_only_consonants(self, cur_syllable):
        return all(not self.__is_vowel(letter) for letter in cur_syllable)

    def syllables_count(self, word):
        """Return count of the word syllables"""
        word = word.lower()

        cnt = 0
        prev_letter = ""
        for letter in word:
            if self.__is_vowel(letter) and \
                    not self.__is_diphthong(prev_letter + letter) and prev_letter != letter:
                cnt += 1
            prev_letter = letter

        return cnt

    def syllables(self, word):
        """Return list of the word syllables"""
        word = word.lower()

        syllables = []
        cur_syllable = ""
        for _, letter in enumerate(word):
            cur_syllable += letter
            if len(cur_syllable) >= 2:
                if self.__is_vowel(letter):
                    if self.__is_vowel(cur_syllable[-2]):
                        if self.__is_diphthong(cur_syllable[-2:]) or self.__is_double_vowel(cur_syllable[-2:]):
                            syllables.append(cur_syllable)
                            cur_syllable = ""
                        elif self.__is_vowel(cur_syllable[-2]) and self.__is_vowel(cur_syllable[-1]):
                            syllables.append(cur_syllable[:-1])
                            cur_syllable = cur_syllable[-1]
                else:
                    if not self.__is_vowel(cur_syllable[-2]):
                        if syllables:
                            last = syllables.pop()
                            syllables.append(last + cur_syllable[:-1])
                        else:
                            syllables.append(cur_syllable[:-1])
                        cur_syllable = cur_syllable[-1]
                    else:
                        syllables.append(cur_syllable[:-1])
                        cur_syllable = cur_syllable[-1]

        if cur_syllable:
            if syllables and self.__contains_only_consonants(cur_syllable):
                last = syllables.pop()
                syllables.append(last + cur_syllable)
            else:
                syllables.append(cur_syllable)

        return syllables


class EstonianSyllableModule(FinnishSyllableModule):
    _EE_VOWELS = "aäeioöõuü"

    @staticmethod
    def __is_diphthong(vowels):
        return vowels in "ai äi oi öi õi ui üi ei " \
                         "ao au ae äu oa ou ea eo " \
                         "eu iu äe öa öe õe ie uo " \
                         "ua oe õu õa äa äo õo".split()

    def __is_vowel(self, symbol):
        return symbol in self._EE_VOWELS


class EnglishSyllableModule(SyllableModule):
    _EN_ALPHABET = "abcdefghijklmnopqrstuvwxyz"
    _EN_VOWELS = "aeiouy"
    _EN_CONSONANTS = "".join(set(_EN_ALPHABET) - set(_EN_VOWELS))

    @staticmethod
    def __is_english_double_consonants(seq):
        return seq in "bb ll mm nn pp ss".split()

    @staticmethod
    def __has_silent_ending(consonants):
        return consonants in "ch sh dg ng gh th ck rk gn rn".split()

    @staticmethod
    def __is_diphthong(vowels):
        return vowels in "ea ia oa ua ae ee ie oe ue ai ei oi ui eo io oo au ou ay ey oy".split()

    @staticmethod
    def __is_triphthong(vowels):
        return vowels in "eau iou eye oye"

    def is_english_vowel(self, symbol):
        return symbol in self._EN_VOWELS

    def __is_english_consonant(self, symbol):
        return symbol in self._EN_CONSONANTS

    def syllables_count(self, word):
        """Return count of the word syllables"""
        if len(word) <= 3 and any(letter in word for letter in "aeiouy"):
            return 1

        word = word.lower()
        leng = len(word)

        if word[-2:] in ["ed", "ly"] or word[leng - 2:leng] in ["er", "es"]:
            leng -= 2
        elif word[-3:] in ["est", "ful"]:
            leng -= 3
        elif word[-4:] in ["less", "ment", "ness"]:
            leng -= 4

        if (word[-2:] in ["ed", "es", "er"] or word.endswith("est")) and \
                self.__is_english_consonant(word[leng - 1]) and \
                not word[:leng] in ["ll", word[leng - 1] + word[leng - 1]]:
            leng -= 1

        if word[leng - 1] == "e":
            leng -= 1

        cnt = 0
        for i in range(leng):
            if self.is_english_vowel(word[i]):
                cnt += 1
            if (i >= 1 and self.__is_diphthong(word[i - 1] + word[i])) or \
                    (i >= 2 and self.__is_triphthong(word[i - 2:i] + word[i])):
                cnt -= 1

        if word.endswith("ed"):
            bef_ed = word[-4:-2]
            if (not (self.__is_english_double_consonants(bef_ed) or self.__has_silent_ending(bef_ed)) and
                not (word[-3] not in "dt" and self.__is_english_consonant(word[-3]) and
                     self.is_english_vowel(word[-4])) and
                not (self.is_english_vowel(word[-3]) and self.is_english_vowel(word[-4]))) or \
                    self.is_english_vowel(word[-4]) and word[-3] in "dt":
                cnt += 1
        elif word.endswith("es") and not (self.__is_english_consonant(word[-3]) and self.is_english_vowel(word[-4])):
            cnt += 1

        if word.endswith("le") and self.__is_english_consonant(word[-3]):
            cnt += 1

        if word.endswith("ery"):
            if word[-4] == "v" and word == "every" or word[-4] == "w":
                cnt -= 1

        if word[-4:] in ["less", "ment", "ness"] or \
                word.endswith("ness") or word[-2:] in ["er", "ly"] or \
                word[-3:] in ["est", "ful"]:
            cnt += 1

        return cnt


if __name__ == "__main__":
    esm = EnglishSyllableModule()
    fsm = FinnishSyllableModule()
    rsm = RussianSyllableModule()

    test_pairs = [
        ('Вова', 2),
        ('Вовочка', 3),
        ('Коронация', 5),
        ('водоПад', 3),
        ('жест', 1),
        ('санаторий', 4),
        ('жест', 1),
        ('Ломоносовская', 6),
        ('Кошка', 2),
        ('Василеостровская', 7),
        ('лапа', 2),
        ('тьма', 1),
        ('резюме', 3),
        ('вечер', 2),
        ('лемма', 2),
        ('землетрясение', 6),
        ('Исландия', 4)
    ]

    for expect_arg, actual_result in test_pairs:
        assert rsm.syllables_count(expect_arg) == actual_result

    assert rsm.syllables("Вовочка") == ["во", "во", "чка"]
    assert rsm.syllables("уезжать") == ["у", "е", "зжать"]
    assert rsm.syllables("инаогурация") == ["и", "на", "о", "гу", "ра", "ци", "я"]
    assert rsm.syllables("Анфиса") == ["ан", "фи", "са"]
    assert rsm.syllables("снайпер") == ["снай", "пер"]
    assert rsm.syllables("Петрополь") == ["пе", "тро", "поль"]
    assert rsm.syllables("жест") == ["жест"]
    assert rsm.syllables("коронация") == ["ко", "ро", "на", "ци", "я"]
    assert rsm.syllables("йогурт") == ["йо", "гурт"]
    assert rsm.syllables("дверца") == ["двер", "ца"]
    assert rsm.syllables("корка") == ["кор", "ка"]
    assert rsm.syllables("санаторий") == ["са", "на", "то", "рий"]
    assert rsm.syllables("Кошка") == ["ко", "шка"]
    assert rsm.syllables("польский") == ["поль", "ский"]
    assert rsm.syllables("ласточка") == ["ла", "сто", "чка"]
    assert rsm.syllables("тьма") == ["тьма"]
    assert rsm.syllables("наледь") == ["на", "ледь"]
    assert rsm.syllables("слякоть") == ["сля", "коть"]
    assert rsm.syllables("дождь") == ["дождь"]
    assert rsm.syllables("ветерочек") == ["ве", "те", "ро", "чек"]
    assert rsm.syllables("развиваться") == ["ра", "зви", "ва", "ться"]
    assert rsm.syllables("кашалот") == ["ка", "ша", "лот"]
    assert rsm.syllables("доченька") == ["до", "чень", "ка"]
    assert rsm.syllables("резюме") == ["ре", "зю", "ме"]
    assert rsm.syllables("белочка") == ["бе", "ло", "чка"]
    assert rsm.syllables("землетрясение") == ["зем", "ле", "тря", "се", "ни", "е"]
    assert rsm.syllables("царскосельский") == ["цар", "ско", "сель", "ский"]
    assert rsm.syllables("интервенция") == ["ин", "тер", "вен", "ци", "я"]
    assert rsm.syllables("Шотландия") == ["шо", "тлан", "ди", "я"]
    assert rsm.syllables("фальшь") == ["фальшь"]
    assert rsm.syllables("фильм") == ["фильм"]
    assert rsm.syllables("стажировка") == ["ста", "жи", "ро", "вка"]
    assert rsm.syllables("славься") == ["славь", "ся"]
    assert rsm.syllables("майся") == ["май", "ся"]
    assert rsm.syllables("одесса") == ["о", "де", "сса"]
    assert rsm.syllables("лемма") == ["ле", "мма"]
    assert rsm.syllables("ткань") == ["ткань"]
    assert rsm.syllables("хвойный") == ["хвой", "ный"]
    assert rsm.syllables("сухой") == ["су", "хой"]
    assert rsm.syllables("старинный") == ["ста", "ри", "нный"]
    assert rsm.syllables("морозный") == ["мо", "ро", "зный"]
    assert rsm.syllables("подъезд") == ["подъ", "езд"]
    assert rsm.syllables("булка") == ["бул", "ка"]
    assert rsm.syllables("мошка") == ["мо", "шка"]
    assert rsm.syllables("равный") == ["ра", "вный"]
    assert rsm.syllables("диктор") == ["ди", "ктор"]
    assert rsm.syllables("ночник") == ["но", "чник"]
    assert rsm.syllables("взбодриться") == ["взбо", "дри", "ться"]
    assert rsm.syllables("горская") == ["гор", "ска", "я"]
    assert rsm.syllables("подготовьтесь") == ["по", "дго", "товь", "тесь"]

    assert fsm.syllables_count('mies') == 1
    assert fsm.syllables_count('Joensuu') == 3
    assert fsm.syllables_count('Vaalimaa') == 3
    assert fsm.syllables_count('äiti') == 2
    assert fsm.syllables_count('Rovaniemi') == 4
    assert fsm.syllables('mies') == ['mies']
    assert fsm.syllables('Joensuu') == ['jo', 'en', 'suu']
    assert fsm.syllables('Vaalimaa') == ['vaa', 'li', 'maa']
    assert fsm.syllables('Ranska') == ['rans', 'ka']
    assert fsm.syllables('aamiainen') == ['aa', 'mi', 'ai', 'nen']
    assert fsm.syllables('Eurooppa') == ['eu', 'roop', 'pa']
    assert fsm.syllables('Rovaniemi') == ['ro', 'va', 'nie', 'mi']
    assert fsm.syllables('kortti') == ['kort', 'ti']
    assert fsm.syllables('aamu') == ['aa', 'mu']
    assert fsm.syllables('isoäitini') == ['i', 'so', 'äi', 'ti', 'ni']
    assert fsm.syllables('sairaanhoitaja') == ['sai', 'raan', 'hoi', 'ta', 'ja']
    assert fsm.syllables('Kittilä') == ['kit', 'ti', 'lä']
    assert fsm.syllables('äiti') == ['äi', 'ti']
    assert fsm.syllables('asua') == ['a', 'su', 'a']
    assert fsm.syllables('isä') == ['i', 'sä']
    assert fsm.syllables('roiskuu') == ['rois', 'kuu']
    assert fsm.syllables('haluaisin') == ['ha', 'lu', 'ai', 'sin']
    assert fsm.syllables(
        'e-pä-jär-jes-tel-mäl-lis-tyt-tä-mät-tö-myy-del-län-sä-kään-kö-hän'.replace(
            '-', '')) == ['e', 'pä', 'jär', 'jes', 'tel', 'mäl',
                          'lis', 'tyt', 'tä', 'mät', 'tö', 'myy',
                          'del', 'län', 'sä', 'kään', 'kö', 'hän']

    test_pairs = [
        ('eye', 1), ('bed', 1), ('skinned', 1), ('apple', 2),
        ('beer', 1), ('plates', 1), ('bridges', 2), ('tasted', 2),
        ('close', 1), ('closed', 1), ('they', 1), ('their', 1),
        ('sway', 1), ('waits', 1), ('bought', 1), ('please', 1),
        ('fates', 1), ('chess', 1), ('sees', 1), ('cheese', 1),
        ('little', 2), ('some', 1), ('synchronized', 3), ('coughed', 1),
        ('oil', 1), ('bread', 1), ('cocked', 1), ('piled', 1),
        ('train', 1), ('training', 2), ('haiku', 2), ('every', 2),
        ('very', 2), ('sad', 1), ('fixed', 1), ('mirror', 2),
        ('tattoos', 2), ('freshly', 2), ('attractive', 3), ('bouquet', 2),
        ('butter', 2), ('machine', 2), ('machinery', 4), ('syllable', 3),
        ('technology', 4), ('tattoo', 2), ('brewery', 2), ('lovely', 2),
        ('family', 3), ('bravery', 3), ('trickery', 3), ('peaceful', 2),
        ('beautiful', 3), ('tilted', 2), ('environment', 4), ('likes', 1),
        ('liked', 1), ('tangled', 2), ('limited', 3), ('unfortunately', 5),
        ('square', 1), ('load', 1), ('watches', 2), ('loaded', 2),
        ('bee', 1), ('air', 1), ('handmade', 2), ('payed', 1),
        ('sadness', 2), ('played', 1), ('player', 2), ('later', 2),
        ('latest', 2), ('statement', 2), ('missed', 1), ('designed', 2),
        ('marked', 1), ('punishment', 3), ('committed', 3), ('pushed', 1), ('turned', 1)
    ]

    for expect_arg, actual_result in test_pairs:
        assert esm.syllables_count(expect_arg) == actual_result
