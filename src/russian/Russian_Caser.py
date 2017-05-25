# -*- coding: utf-8 -*-
class RussianCaser(object):
    @staticmethod
    def is_vowel(symbol):
        return symbol in "аеиоуыэя"

    @staticmethod
    def is_without_ending(word):
        # see words list: http://morphemeonline.ru/words-without-ending.html
        return word in "адажио ассорти денди депо дефиле дзюдо жалюзи " \
                       "кабаре каратэ кафе кино колибри кофе лото " \
                       "метро кенгуру пальто панно паспарту пенсне пианино " \
                       "табу такси тире фламинго фортепиано фото хачапури шимпанзе шоссе эскимо эссе".split()

    """ Return word in Russian dative case
        :param word is Russian lemma
        :param gen is gender of word, if gen is None then first word of non-defined gender, otherwise male of female
        :param single defines single or plural form of lemma
        :return word in Russian dative case

        !!! Method architecture has refactored due to incorrectly working with plural form !!!
    """
    def dative(self, word, gen=None, single=True):
        if self.is_without_ending(word):
            return word
        else:
            if single:
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
                    elif word.endswith('чек'):
                        return word[:-2] + 'ку'
                    elif word.endswith('ёк'):
                        return word[:-2] + 'ьку'
                    elif word.endswith('ок') and word[-3] in 'нтчш' and len(word) > 4:
                        return word[:-2] + 'ку'
                    elif word.endswith('ец'):
                        return word[:-2] + 'цу'
                    else:
                        return word + 'у'
                else:
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
    assert caser.dative("мать", 'f', False) == "матерям"
    assert caser.dative("дочь", 'f') == "дочери"
    assert caser.dative("рать", 'f') == "рати"
    assert caser.dative("верёвка", 'f') == "верёвке"
    assert caser.dative("капля", 'f') == "капле"
    assert caser.dative("ванна", 'f', False) == "ваннам"
    assert caser.dative("капель", 'f') == "капели"
    assert caser.dative("дверь", 'f', False) == "дверям"
    assert caser.dative("апрель", 'm') == "апрелю"
    assert caser.dative("молодец", 'm') == "молодцу"
    assert caser.dative("замочек", 'm') == "замочку"
    assert caser.dative("ключик", 'm') == "ключику"
    assert caser.dative("горшок", 'm') == "горшку"
    assert caser.dative("шок", 'm') == "шоку"
    assert caser.dative("станок", 'm') == "станку"
    assert caser.dative("завиток", 'm') == "завитку"
    assert caser.dative("старичок", 'm') == "старичку"
    assert caser.dative("лоток", 'm') == "лотку"
    assert caser.dative("ток", 'm') == "току"
    assert caser.dative("ларёк", 'm') == "ларьку"
    assert caser.dative("харёк", 'm') == "харьку"
    assert caser.dative("порок", 'm') == "пороку"
    assert caser.dative("санаторий", 'm') == "санаторию"
    assert caser.dative("санаторий", 'm', False) == "санаториям"
    assert caser.dative("ковчег", 'm') == "ковчегу"
    assert caser.dative("такт", 'm') == "такту"
    assert caser.dative("село", 'n') == "селу"
    assert caser.dative("ковчег", 'm', False) == "ковчегам"
    assert caser.dative("брат", 'm', False) == "братьям"
    assert caser.dative("дерево", 'm', False) == "деревьям"
    assert caser.dative("пальто") == "пальто"
