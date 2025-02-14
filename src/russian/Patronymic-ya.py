# -*- coding: utf-8 -*-
class Patronymer(object):
    @staticmethod
    def __is_vowel(symbol):
        return symbol in "аеиоуыэюя"

    def __syllables_count(self, name):
        return len(list(filter(lambda l: self.__is_vowel(l), name.lower())))

    @staticmethod
    def __is_except_consonant(letter):
        return letter in "жцчшщ"

    @staticmethod
    def __is_consonant_before_iy(letter):
        return letter in "кхц"

    @staticmethod
    def __is_ends_with_ail(name):
        return name.endswith("аил") or name.endswith("уил")

    @staticmethod
    def __is_ends_with_iil(name):
        return name.endswith("иил")

    @staticmethod
    def __is_names_with_emphasis_endings(name):
        return name in ["Фока", "Мина"]

    def __is_double_consonants(self, letter_group):
        letter_group = letter_group.lower()
        return letter_group != "нт" and \
            not self.__is_vowel(letter_group[0]) and \
            not self.__is_vowel(letter_group[-1])

    def get_patro(self, name, feminine=False):
        if name == "Пётр":
            name = name.replace("ё", "е")

        if name == "Павел":
            name = "Павлов"

        if name == "Лев":
            name = "Львов"

        if name == "Яков":
            name = "Яковлев"

        if feminine:
            if name[-1] in "ая" and name[-2:] not in "ея ия".split():
                suffix = "ична"
            else:
                suffix = "на"
        else:
            suffix = "ич"

        base_of_name, whose_suffix = "", ""
        if name.endswith("й") or name[-2:] in "ея ия".split():
            if name[-2:] == "ий" and \
                    not (self.__is_consonant_before_iy(name[-3]) or self.__is_double_consonants(name[-4:-2])):
                whose_suffix = "ьев"
                base_of_name = name[:-2]
            else:
                whose_suffix = "ев"
                base_of_name = name[:-1]
        elif self.__is_vowel(name[-1]):
            base_of_name = name[:-1]
            if name[-1] in "ая" and self.__syllables_count(name) <= 2 and \
                    not self.__is_names_with_emphasis_endings(name) and \
                    not (0 <= name.find("а") <= len(name) - 2):
                if feminine:
                    whose_suffix = "ин"
            elif name[-1] == "а" and name[-2] in "лмн":
                whose_suffix = "ов"
                if feminine:
                    suffix = "на"
            elif name[-1] in "ео":
                whose_suffix = "в"
                base_of_name += name[-1]
            elif name[-1] == "и":
                whose_suffix = "ев"
                base_of_name += name[-1]
        elif self.__is_except_consonant(name[-1]) or name.endswith("ь"):
            whose_suffix = "ев"
            base_of_name = name if self.__is_except_consonant(name[-1]) else name[:-1]
        else:
            if not (name.endswith("ов") or name.endswith("ев")):
                whose_suffix = "ов"
            if self.__is_ends_with_iil(name):
                base_of_name = name[:-2] + name[-1]
            elif self.__is_ends_with_ail(name):
                base_of_name = name[:-2] if name.endswith("аил") else name[:-3] + "о"
                base_of_name += "йл"
            else:
                base_of_name = name
        return base_of_name + whose_suffix + suffix


if __name__ == "__main__":
    p = Patronymer()
    assert p.get_patro("Иван") == "Иванович"
    assert p.get_patro("Виктор") == "Викторович"
    assert p.get_patro("Пётр") == "Петрович"
    assert p.get_patro("Лев") == "Львович"
    assert p.get_patro("Зосима") == "Зосимович"
    assert p.get_patro("Акакий") == "Акакиевич"
    assert p.get_patro("Андрей") == "Андреевич"
    assert p.get_patro("Кондратий") == "Кондратьевич"
    assert p.get_patro("Прокофий") == "Прокофьевич"
    assert p.get_patro("Дмитрий") == "Дмитриевич"
    assert p.get_patro("Димитрий") == "Димитриевич"
    assert p.get_patro("Георгий") == "Георгиевич"
    assert p.get_patro("Николай") == "Николаевич"
    assert p.get_patro("Кирилл") == "Кириллович"
    assert p.get_patro("Владимир") == "Владимирович"
    assert p.get_patro("Глеб") == "Глебович"
    assert p.get_patro("Гаврила") == "Гаврилович"
    assert p.get_patro("Иона") == "Ионович"
    assert p.get_patro("Фома") == "Фомич"
    assert p.get_patro("Фока") == "Фокич"
    assert p.get_patro("Никита") == "Никитич"
    assert p.get_patro("Жорж") == "Жоржевич"
    assert p.get_patro("Фока", True) == "Фокична"
    assert p.get_patro("Фёдор", True) == "Фёдоровна"
    assert p.get_patro("Фома", True) == "Фоминична"
    assert p.get_patro("Егор") == "Егорович"
    assert p.get_patro("Фрол") == "Фролович"
    assert p.get_patro("Фаддей") == "Фаддеевич"
    assert p.get_patro("Эмиль") == "Эмилевич"
    assert p.get_patro("Игорь") == "Игоревич"
    assert p.get_patro("Лазарь") == "Лазаревич"
    assert p.get_patro("Яков") == "Яковлевич"
    assert p.get_patro("Ярослав") == "Ярославович"
    assert p.get_patro("Савва") == "Саввич"
    assert p.get_patro("Илья") == "Ильич"
    assert p.get_patro("Павел") == "Павлович"
    assert p.get_patro("Валерий") == "Валерьевич"
    assert p.get_patro("Захар") == "Захарович"
    assert p.get_patro("Захарий") == "Захарьевич"
    assert p.get_patro("Юрий") == "Юрьевич"
    assert p.get_patro("Василий") == "Васильевич"
    assert p.get_patro("Андрей", True) == "Андреевна"
    assert p.get_patro("Семён", True) == "Семёновна"
    assert p.get_patro("Пётр", True) == "Петровна"
    assert p.get_patro("Лев", True) == "Львовна"
    assert p.get_patro("Илья", True) == "Ильинична"
    assert p.get_patro("Савва", True) == "Саввична"
    assert p.get_patro("Василий", True) == "Васильевна"
    assert p.get_patro("Павел", True) == "Павловна"
    assert p.get_patro("Никита", True) == "Никитична"
    assert p.get_patro("Кузьма", True) == "Кузьминична"
    assert p.get_patro("Евгений", True) == "Евгеньевна"
    assert p.get_patro("Виктор", True) == "Викторовна"
    assert p.get_patro("Михаил", True) == "Михайловна"
    assert p.get_patro("Данила", True) == "Даниловна"
    assert p.get_patro("Всеволод", True) == "Всеволодовна"
    assert p.get_patro("Гаврила", True) == "Гавриловна"
    assert p.get_patro("Даниил", True) == "Даниловна"
    assert p.get_patro("Менея", True) == "Менеевна"
    assert p.get_patro("Пров", True) == "Провна"
    assert p.get_patro("Вилли", True) == "Виллиевна"
    assert p.get_patro("Вяйне") == "Вяйневич"
    assert p.get_patro("Василько") == "Василькович"
    assert p.get_patro("Мина") == "Минович"
