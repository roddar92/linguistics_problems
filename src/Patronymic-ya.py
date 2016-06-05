# -*- coding: utf-8 -*-
class Patronymer(object):
    @staticmethod
    def is_vowel(symbol):
        return symbol in "аеиоуыэя"

    @staticmethod
    def is_unusually_names_with_ending_y(name):
        return name in ["Акакий", "Георгий", "Дмитрий", "Димитрий", "Лукий"]

    @staticmethod
    def is_names_with_emphasis_endings(name):
        return name in ["Илья", "Кузьма", "Лука", "Фома"]

    def get_patro(self, name, feminine=False):
        if name == "Пётр":
            name = name.replace("ё", "е")

        if name == "Павел":
            name = name.replace("е", "")

        if name == "Лев":
            name = name.replace("е", "ь")

        if name == "Михаил":
            name = "Михайл"

        if feminine:
            if self.is_vowel(name[-1]):
                suffix = "ична"
            else:
                suffix = "на"
        else:
            suffix = "ич"

        if self.is_vowel(name[-1]):
            if self.is_names_with_emphasis_endings(name):
                return name[:-1] + "ин" + suffix if feminine else name[:-1] + suffix
            elif name[-1] == "а" and name[-2] in "лмн":
                if feminine:
                    suffix = "на"
                return name[:-1] + "ов" + suffix
            else:
                return name[:-1] + suffix
        elif name.endswith("й"):
            if name[-2] == "и":
                return name[:-1] + "ев" + suffix if self.is_unusually_names_with_ending_y(name) \
                    else name[:-2] + "ьев" + suffix
            else:
                return name[:-1] + "ев" + suffix
        elif name.endswith("ь"):
            return name[:-1] + "ев" + suffix if name[-2] == "р" else name + "ев" + suffix
        else:
            return name + "лев" + suffix if name == "Яков" else name + "ов" + suffix


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
    assert p.get_patro("Фока", True) == "Фокична"
    assert p.get_patro("Фёдор", True) == "Фёдоровна"
    assert p.get_patro("Фома", True) == "Фоминична"
    assert p.get_patro("Егор") == "Егорович"
    assert p.get_patro("Фрол") == "Фролович"
    assert p.get_patro("Фаддей") == "Фаддеевич"
    assert p.get_patro("Эмиль") == "Эмильевич"
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
