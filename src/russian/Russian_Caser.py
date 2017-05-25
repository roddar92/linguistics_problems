# -*- coding: utf-8 -*-
class RussianCaser(object):
    @staticmethod
    def is_vowel(symbol):
        return symbol in "аеиоуыэя"

    @staticmethod
    def is_without_ending(word):
        # see words list: http://morphemeonline.ru/words-without-ending.html
        return word in "адажио ассорти денди депо дефиле дзюдо жалюзи " \
                       "кабаре каратэ кафе кино колибри кофе метро кенгуру пальто панно паспарту пенсне пианино " \
                       "табу такси тире фламинго фортепиано фото хачапури шимпанзе шоссе эскимо эссе".split()

    """ Return word in Russian dative case
        :param word is Russian lemma
        :param gen is gender of word, if gen is None then first word in plural form, otherwise single
        :return word in Russian dative case

        !!! Often works not correctly for plural form !!!
    """
    def dative(self, word, gen=None):
        if self.is_without_ending(word):
            return word
        else:
            if gen == 'f':
                if word in ['мать', 'дочь']:
                    return word[:-1] + 'ери'
                elif word.endswith('ожь'):
                    if word == 'дрожь':
                        return word[:-1] + 'и'
                    else:
                        return word[:-3] + 'жи'
                elif word[-1] == 'ь':
                    return word[:-1] + 'и'
                elif word[-1] in 'ая':
                    return word[:-1] + 'е'
            elif gen == 'm':
                if word[-1] in 'йь':
                    return word[:-1] + 'ю'
                elif word.endswith('ец'):
                    return word[:-2] + 'цу'
                else:
                    return word + 'у'
            elif gen == 'n':
                return word[:-1] + 'у'
            else:
                if word in ['мать', 'дочь']:
                    return word[:-1] + 'ерям'
                elif word in ['брат', 'стул']:
                    return word + 'ьям'
                elif word == 'сын':
                    return word + 'овьям'
                elif word == 'друг':
                    return word + 'зьям'
                elif word == 'дерево':
                    return word[:-1] + 'ьям'
                elif word[-1] in 'йь':
                    return word[:-1] + 'ям'
                elif not self.is_vowel(word[-1]):
                    return word + 'ам'
                else:
                    return word + 'м'


if __name__ == "__main__":
    caser = RussianCaser()
    assert caser.dative('ложь', 'f') == "лжи"
    assert caser.dative('рожь', 'f') == "ржи"
    assert caser.dative('дрожь', 'f') == "дрожи"
    assert caser.dative("ванна", 'f') == "ванне"
    assert caser.dative("мать", 'f') == "матери"
    assert caser.dative("мать") == "матерям"
    assert caser.dative("дочь", 'f') == "дочери"
    assert caser.dative("рать", 'f') == "рати"
    assert caser.dative("верёвка", 'f') == "верёвке"
    assert caser.dative("капля", 'f') == "капле"
    assert caser.dative("ванна") == "ваннам"
    assert caser.dative("капель", 'f') == "капели"
    assert caser.dative("дверь") == "дверям"
    assert caser.dative("апрель", 'm') == "апрелю"
    assert caser.dative("молодец", 'm') == "молодцу"
    assert caser.dative("санаторий", 'm') == "санаторию"
    assert caser.dative("санаторий") == "санаториям"
    assert caser.dative("ковчег", 'm') == "ковчегу"
    assert caser.dative("такт", 'm') == "такту"
    assert caser.dative("село", 'n') == "селу"
    assert caser.dative("ковчег") == "ковчегам"
    assert caser.dative("брат") == "братьям"
    assert caser.dative("дерево") == "деревьям"
    assert caser.dative("пальто") == "пальто"
