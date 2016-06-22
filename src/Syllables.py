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

    def russian_syllables_count(self, word):
        """Retirn count of thw word syllables"""
        word = word.lower()
        cnt = 0
        for letter in word:
            if self.is_russian_vowel(letter):
                cnt += 1

        return cnt

    def english_syllables_count(self, word):
        word = word.lower()
        leng = len(word)
        if word[-1] == "e":
            leng -= 1

        cnt = 0
        prev = ""
        for i in range(leng):
            if (prev == "" or self.is_english_consonant(prev)) and self.is_english_vowel(word[i]):
                cnt += 1
            prev = word[i]

        return cnt

    def russian_syllables(self, word):
        """Return list of the word syllables"""
        word = word.lower()
        if self.russian_syllables_count(word) <= 1:
            return [word]

        syllables = []
        cur_syllab = ""

        for letter in word:
            cur_syllab += letter
            if self.is_russian_vowel(letter):
                syllables.append(cur_syllab)
                cur_syllab = ""
            if syllables:
                if letter == "ь" or self.is_russian_vowel(syllables[len(syllables)-1][-1]) and letter == "й":
                    last = syllables.pop(len(syllables) - 1)
                    syllables.append(last + cur_syllab)
                    cur_syllab = ""

        if cur_syllab:
            last = syllables.pop(len(syllables) - 1)
            syllables.append(last + cur_syllab)

        return syllables

if __name__ == "__main__":
    sm = SyllableModule()
    assert sm.russian_syllables_count("Вова") == 2
    assert sm.russian_syllables_count("Вовочка") == 3
    assert sm.russian_syllables("Вовочка") == ["во", "во", "чка"]
    assert sm.russian_syllables_count("Коронация") == 5
    assert sm.russian_syllables_count("водоПад") == 3
    assert sm.russian_syllables("Анфиса") == ["а", "нфи", "са"]
    assert sm.russian_syllables("снайпер") == ["снай", "пер"]
    assert sm.russian_syllables("Петрополь") == ["пе", "тро", "поль"]
    assert sm.russian_syllables_count("жест") == 1
    assert sm.russian_syllables("жест") == ["жест"]
    assert sm.russian_syllables("коронация") == ["ко", "ро", "на", "ци", "я"]
    assert sm.russian_syllables_count("санаторий") == 4
    assert sm.russian_syllables("санаторий") == ["са", "на", "то", "рий"]
    assert sm.russian_syllables_count("Ломоносовская") == 6
    assert sm.russian_syllables_count("Кошка") == 2
    assert sm.russian_syllables("Кошка") == ["ко", "шка"]
    assert sm.russian_syllables("польский") == ["поль", "ский"]
    assert sm.russian_syllables("ласточка") == ["ла", "сто", "чка"]
    assert sm.russian_syllables_count("Василеостровская") == 7
    assert sm.russian_syllables_count("лапа") == 2
    assert sm.russian_syllables("наледь") == ["на", "ледь"]
    assert sm.russian_syllables("дождь") == ["дождь"]
    assert sm.russian_syllables("ветерочек") == ["ве", "те", "ро", "чек"]
    assert sm.russian_syllables("кашалот") == ["ка", "ша", "лот"]
    assert sm.russian_syllables_count("резюме") == 3
    assert sm.russian_syllables("резюме") == ["ре", "зю", "ме"]
    assert sm.russian_syllables_count("вечер") == 2
    assert sm.russian_syllables_count("землетрясение") == 6
    assert sm.russian_syllables("землетрясение") == ["зе", "мле", "тря", "се", "ни", "е"]
    assert sm.russian_syllables_count("Исландия") == 4
    assert sm.russian_syllables("Шотландия") == ["шо", "тла", "нди", "я"]