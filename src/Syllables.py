# -*- coding: utf-8 -*-
class SyllableModule(object):
    @staticmethod
    def is_russian_vowel(symbol):
        return symbol in "аеёиоуыэюя"

    @staticmethod
    def is_russian_consonant(symbol):
        return symbol in "бвгджзйклмнпрстфчцчшщъь"

    @staticmethod
    def is_english_vowel(symbol):
        return symbol in "aeiouy"

    @staticmethod
    def is_english_consonant(symbol):
        return symbol in "bcdfghjklmnpqrstvwxz"

    @staticmethod
    def has_silent_ending(consonants):
        return consonants in "ch sh dg ng gh ck rk"

    @staticmethod
    def is_diphthong(vowels):
        return vowels in "ea ia oa ua ae ee ie oe ue ai oi ui eo io oo au ou ay oy"

    @staticmethod
    def is_triphthong(vowels):
        return vowels in "eau iou"

    def english_syllables_count(self, word):
        """Return count of thw word syllables"""
        if len(word) <= 3 and ("a" in word or "e" in word or "i" in word or "o" in word or "u" in word or "y" in word):
            return 1

        word = word.lower()
        leng = len(word)

        if word.endswith("ed") or word[:leng].endswith("er") or word[:leng].endswith("es") or word.endswith("ly"):
            leng -= 2
        elif word.endswith("ful") or word.endswith("est"):
            leng -= 3
        elif word.endswith("less"):
            leng -= 4

        if (word.endswith("ed") or word.endswith("es") or word.endswith("er") or word.endswith("est")) and \
                self.is_english_consonant(word[leng - 1]) and \
                not word[:leng].endswith("ll") and word[:leng].endswith(word[leng - 1] + word[leng - 1]):
            leng -= 1

        if word[leng - 1] == "e":
            leng -= 1

        cnt = 0
        for i in range(leng):
            if self.is_english_vowel(word[i]):
                cnt += 1
            if (i >= 1 and self.is_diphthong(word[i - 1] + word[i])) or \
                    (i >= 2 and self.is_triphthong(word[i - 2:i] + word[i])):
                cnt -= 1

        if word.endswith("ed"):
            if (word[-4:-2] not in "bb ll mm nn pp ss" and
                not self.has_silent_ending(word[-4:-2]) and
                not (word[-3] not in "dt" and self.is_english_consonant(word[-3])
                     and self.is_english_vowel(word[-4])) and
                not (self.is_english_vowel(word[-3]) and self.is_english_vowel(word[-4]))) or \
                            self.is_english_vowel(word[-4]) and word[-3] in "dt":
                cnt += 1
        elif word.endswith("es") and not (self.is_english_consonant(word[-3]) and self.is_english_vowel(word[-4])):
            cnt += 1

        if word.endswith("le") and self.is_english_consonant(word[-3]):
            cnt += 1

        if word.endswith("ery"):
            if word[-4] == "v" and word == "every" or word[-4] == "w":
                cnt -= 1

        if word.endswith("ful") or word.endswith("less") or word.endswith("ly") \
                or word.endswith("er") or word.endswith("est"):
            cnt += 1

        return cnt

    def russian_syllables_count(self, word):
        """Return count of the word syllables"""
        word = word.lower()
        cnt = 0
        for letter in word:
            if self.is_russian_vowel(letter):
                cnt += 1

        return cnt

    def russian_syllables(self, word):
        """Return list of the word syllables"""
        word = word.lower()

        syllables = []
        cur_syllable = ""

        for letter in word:
            cur_syllable += letter
            if self.is_russian_vowel(letter):
                syllables.append(cur_syllable)
                cur_syllable = ""
            if syllables:
                if letter == "ь" or self.is_russian_vowel(syllables[len(syllables) - 1][-1]) and letter == "й":
                    last = syllables.pop(len(syllables) - 1)
                    syllables.append(last + cur_syllable)
                    cur_syllable = ""
                elif len(cur_syllable) >= 2 and cur_syllable[-2] in "лмнр" and cur_syllable not in "лл мм нн рр" \
                        and self.is_russian_consonant(letter):
                    last = syllables.pop(len(syllables) - 1)
                    syllables.append(last + cur_syllable[0])
                    cur_syllable = cur_syllable[1:]

        if cur_syllable:
            last = syllables.pop(len(syllables) - 1)
            syllables.append(last + cur_syllable)

        if syllables[-1] == "ся" and syllables[-2].endswith("ть"):
            last = syllables.pop(len(syllables) - 1)
            prev = syllables.pop(len(syllables) - 1)
            syllables += [prev[:-2], prev[-2:] + last]

        return syllables


if __name__ == "__main__":
    sm = SyllableModule()
    assert sm.russian_syllables_count("Вова") == 2
    assert sm.russian_syllables_count("Вовочка") == 3
    assert sm.russian_syllables("Вовочка") == ["во", "во", "чка"]
    assert sm.russian_syllables_count("Коронация") == 5
    assert sm.russian_syllables_count("водоПад") == 3
    assert sm.russian_syllables("Анфиса") == ["ан", "фи", "са"]
    assert sm.russian_syllables("снайпер") == ["снай", "пер"]
    assert sm.russian_syllables("Петрополь") == ["пе", "тро", "поль"]
    assert sm.russian_syllables_count("жест") == 1
    assert sm.russian_syllables("жест") == ["жест"]
    assert sm.russian_syllables("коронация") == ["ко", "ро", "на", "ци", "я"]
    assert sm.russian_syllables("йогурт") == ["йо", "гурт"]
    assert sm.russian_syllables("дверца") == ["двер", "ца"]
    assert sm.russian_syllables("корка") == ["кор", "ка"]
    assert sm.russian_syllables_count("санаторий") == 4
    assert sm.russian_syllables("санаторий") == ["са", "на", "то", "рий"]
    assert sm.russian_syllables_count("Ломоносовская") == 6
    assert sm.russian_syllables_count("Кошка") == 2
    assert sm.russian_syllables("Кошка") == ["ко", "шка"]
    assert sm.russian_syllables("польский") == ["поль", "ский"]
    assert sm.russian_syllables("ласточка") == ["ла", "сто", "чка"]
    assert sm.russian_syllables_count("Василеостровская") == 7
    assert sm.russian_syllables_count("лапа") == 2
    assert sm.russian_syllables_count("тьма") == 1
    assert sm.russian_syllables("тьма") == ["тьма"]
    assert sm.russian_syllables("наледь") == ["на", "ледь"]
    assert sm.russian_syllables("слякоть") == ["сля", "коть"]
    assert sm.russian_syllables("лемма") == ["ле", "мма"]
    assert sm.russian_syllables("дождь") == ["дождь"]
    assert sm.russian_syllables("ветерочек") == ["ве", "те", "ро", "чек"]
    assert sm.russian_syllables("развиваться") == ["ра", "зви", "ва", "ться"]
    assert sm.russian_syllables("кашалот") == ["ка", "ша", "лот"]
    assert sm.russian_syllables("доченька") == ["до", "чень", "ка"]
    assert sm.russian_syllables_count("резюме") == 3
    assert sm.russian_syllables("резюме") == ["ре", "зю", "ме"]
    assert sm.russian_syllables("белочка") == ["бе", "ло", "чка"]
    assert sm.russian_syllables_count("вечер") == 2
    assert sm.russian_syllables_count("лемма") == 2
    assert sm.russian_syllables_count("землетрясение") == 6
    assert sm.russian_syllables("землетрясение") == ["зем", "ле", "тря", "се", "ни", "е"]
    assert sm.russian_syllables("интервенция") == ["ин", "тер", "вен", "ци", "я"]
    assert sm.russian_syllables_count("Исландия") == 4
    assert sm.russian_syllables("Шотландия") == ["шо", "тлан", "ди", "я"]
    assert sm.russian_syllables("фальшь") == ["фальшь"]
    assert sm.russian_syllables("фильм") == ["фильм"]
    assert sm.russian_syllables("стажировка") == ["ста", "жи", "ро", "вка"]

    assert sm.english_syllables_count("bed") == 1
    assert sm.english_syllables_count("skinned") == 1
    assert sm.english_syllables_count("apple") == 2
    assert sm.english_syllables_count("beer") == 1
    assert sm.english_syllables_count("plates") == 1
    assert sm.english_syllables_count("bridges") == 2
    assert sm.english_syllables_count("tasted") == 2
    assert sm.english_syllables_count("close") == 1
    assert sm.english_syllables_count("closed") == 1
    assert sm.english_syllables_count("sway") == 1
    assert sm.english_syllables_count("waits") == 1
    assert sm.english_syllables_count("bought") == 1
    assert sm.english_syllables_count("please") == 1
    assert sm.english_syllables_count("fates") == 1
    assert sm.english_syllables_count("chess") == 1
    assert sm.english_syllables_count("sees") == 1
    assert sm.english_syllables_count("cheese") == 1
    assert sm.english_syllables_count("little") == 2
    assert sm.english_syllables_count("some") == 1
    assert sm.english_syllables_count("synchronized") == 3
    assert sm.english_syllables_count("coughed") == 1
    assert sm.english_syllables_count("oil") == 1
    assert sm.english_syllables_count("bread") == 1
    assert sm.english_syllables_count("cocked") == 1
    assert sm.english_syllables_count("piled") == 1
    assert sm.english_syllables_count("train") == 1
    assert sm.english_syllables_count("training") == 2
    assert sm.english_syllables_count("haiku") == 2
    assert sm.english_syllables_count("every") == 2
    assert sm.english_syllables_count("very") == 2
    assert sm.english_syllables_count("sad") == 1
    assert sm.english_syllables_count("fixed") == 1
    assert sm.english_syllables_count("mirror") == 2
    assert sm.english_syllables_count("tattoos") == 2
    assert sm.english_syllables_count("freshly") == 2
    assert sm.english_syllables_count("attractive") == 3
    assert sm.english_syllables_count("bouquet") == 2
    assert sm.english_syllables_count("butter") == 2
    assert sm.english_syllables_count("machine") == 2
    assert sm.english_syllables_count("machinery") == 4
    assert sm.english_syllables_count("syllable") == 3
    assert sm.english_syllables_count("technology") == 4
    assert sm.english_syllables_count("tattoo") == 2
    assert sm.english_syllables_count("brewery") == 2
    assert sm.english_syllables_count("lovely") == 2
    assert sm.english_syllables_count("family") == 3
    assert sm.english_syllables_count("bravery") == 3
    assert sm.english_syllables_count("trickery") == 3
    assert sm.english_syllables_count("peaceful") == 2
    assert sm.english_syllables_count("beautiful") == 3
    assert sm.english_syllables_count("tilted") == 2
    assert sm.english_syllables_count("environment") == 4
    assert sm.english_syllables_count("likes") == 1
    assert sm.english_syllables_count("liked") == 1
    assert sm.english_syllables_count("tangled") == 2
    assert sm.english_syllables_count("limited") == 3
    assert sm.english_syllables_count("unfortunately") == 5
    assert sm.english_syllables_count("square") == 1
    assert sm.english_syllables_count("load") == 1
    assert sm.english_syllables_count("watches") == 2
    assert sm.english_syllables_count("loaded") == 2
    assert sm.english_syllables_count("bee") == 1
    assert sm.english_syllables_count("air") == 1
    assert sm.english_syllables_count("handmade") == 2
    assert sm.english_syllables_count("payed") == 1
    assert sm.english_syllables_count("played") == 1
    assert sm.english_syllables_count("player") == 2
    assert sm.english_syllables_count("later") == 2
    assert sm.english_syllables_count("latest") == 2
    assert sm.english_syllables_count("missed") == 1
    assert sm.english_syllables_count("marked") == 1
    assert sm.english_syllables_count("committed") == 3
