# -*- coding: utf-8 -*-
class Diminutiver(object):
    @staticmethod
    def is_vowel(symbol):
        return symbol in "аеиоуыэя"

    @staticmethod
    def is_sibilant(symbol):
        return symbol in "чшщ"

    @staticmethod
    def is_endings_with_a(symbol):
        return symbol in "влмнрст"

    def get_diminutive(self, name):
        suffix = ""
        if name[-1] == "а":
            if name[-2] == "к":
                return name[:-1] + "уся"
            else:
                if self.is_endings_with_a(name[-2]):
                    suffix = "очк"
                else:
                    suffix = "еньк"
        elif name[-1] == "я":
            if name[-2] == "н":
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
    assert diminutiver.get_diminutive("Таня") == "Танечка"
    assert diminutiver.get_diminutive("Рита") == "Риточка"
    assert diminutiver.get_diminutive("Вика") == "Викуся"
    assert diminutiver.get_diminutive("Диана") == "Дианочка"