# -*- coding: utf-8 -*-
class Diminutiver(object):
    @staticmethod
    def __is_vowel(symbol):
        return symbol in "аеиоуыэюя"

    @staticmethod
    def __is_sibilant(symbol):
        return symbol in "чшщ"

    @staticmethod
    def __is_endings_with_a(symbol):
        return symbol in "бвдзлмнпрст"

    def get_diminutive(self, name):
        if name.endswith("ка"):
            if not self.__is_vowel(name[-3]):
                name = name[:-3] + "я" if name[-3] in "йь" else name[:-2] + "а"
            else:
                return name[:-1] + "уся"
        elif name.endswith("ия"):
            name = name[:-2] + "я"
        elif name.endswith("ль"):
            name = name[:-1] + "я"

        suffix = ""
        if not self.__is_vowel(name[-1]):
            if name[-1] == "й":
                return name[:-1] + "юшка"
            elif name[-1] == "ь":
                return name[:-1] + "ёк"
            elif name.endswith("ам") or name.endswith("ан"):
                return name + "чик"
            elif name.endswith("им"):
                return name + "ка"
            elif name.endswith("илл"):
                return name[:-3] + "юша"
            elif name.endswith("ил"):
                return name + "ушка"
            elif not name.endswith("ик"):
                return name + "ик"
            else:
                return name
        elif name[-1] == "а":
            if self.__is_endings_with_a(name[-2]):
                suffix = "ушк" if name[-3] == "ё" else "очк"
            else:
                suffix = "еньк"
        elif name[-1] == "я":
            if name[-2] == "ь":
                suffix = "юшк" if name[-3] not in "лмн" else "юш"
            elif name[-2] == "л":
                suffix = "ечк" if not self.__is_vowel(name[0].lower()) else "еньк"
            elif name[-2] in "аемн":
                suffix = "ечк"
            else:
                suffix = "еньк"
        suffix += "а"

        return name[:-1] + suffix


if __name__ == "__main__":
    diminutiver = Diminutiver()
    assert diminutiver.get_diminutive("Вова") == "Вовочка"
    assert diminutiver.get_diminutive("Саша") == "Сашенька"
    assert diminutiver.get_diminutive("Вася") == "Васенька"
    assert diminutiver.get_diminutive("Анфиса") == "Анфисочка"
    assert diminutiver.get_diminutive("Женя") == "Женечка"
    assert diminutiver.get_diminutive("Тима") == "Тимочка"
    assert diminutiver.get_diminutive("Манька") == "Манечка"
    assert diminutiver.get_diminutive("Таня") == "Танечка"
    assert diminutiver.get_diminutive("Клава") == "Клавочка"
    assert diminutiver.get_diminutive("Клара") == "Кларочка"
    assert diminutiver.get_diminutive("Алла") == "Аллочка"
    assert diminutiver.get_diminutive("Алёна") == "Алёнушка"
    assert diminutiver.get_diminutive("Лапа") == "Лапочка"
    assert diminutiver.get_diminutive("Рита") == "Риточка"
    assert diminutiver.get_diminutive("Влад") == "Владик"
    assert diminutiver.get_diminutive("Вика") == "Викуся"
    assert diminutiver.get_diminutive("Витя") == "Витенька"
    assert diminutiver.get_diminutive("Васька") == "Васенька"
    assert diminutiver.get_diminutive("Диана") == "Дианочка"
    assert diminutiver.get_diminutive("Дина") == "Диночка"
    assert diminutiver.get_diminutive("Люда") == "Людочка"
    assert diminutiver.get_diminutive("Лиза") == "Лизочка"
    assert diminutiver.get_diminutive("Людка") == "Людочка"
    assert diminutiver.get_diminutive("Люба") == "Любочка"
    assert diminutiver.get_diminutive("Влада") == "Владочка"
    assert diminutiver.get_diminutive("Лампа") == "Лампочка"
    assert diminutiver.get_diminutive("Лавка") == "Лавочка"
    assert diminutiver.get_diminutive("Дамба") == "Дамбочка"
    assert diminutiver.get_diminutive("Дарья") == "Дарьюшка"
    assert diminutiver.get_diminutive("Галя") == "Галечка"
    assert diminutiver.get_diminutive("Емеля") == "Емеленька"
    assert diminutiver.get_diminutive("Лилия") == "Лилечка"
    assert diminutiver.get_diminutive("Юлия") == "Юленька"
    assert diminutiver.get_diminutive("Илья") == "Ильюша"
    assert diminutiver.get_diminutive("Игорь") == "Игорёк"
    assert diminutiver.get_diminutive("Рустам") == "Рустамчик"
    assert diminutiver.get_diminutive("Майка") == "Маечка"
    assert diminutiver.get_diminutive("Самуил") == "Самуилушка"
    assert diminutiver.get_diminutive("Андрей") == "Андреюшка"
    assert diminutiver.get_diminutive("Николай") == "Николаюшка"
    assert diminutiver.get_diminutive("Рая") == "Раечка"
    assert diminutiver.get_diminutive("Менея") == "Менеечка"
