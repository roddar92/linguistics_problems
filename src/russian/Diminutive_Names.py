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
        return symbol in "бдвлмнпрст"

    def get_diminutive(self, name):
        suffix = ""
        if not self.is_vowel(name[-1]):
            if name[-1] == "ь":
                return name[:-1] + "ёк"
            return name + "ик"
        elif name[-1] == "а":
            if name[-2] == "к":
                if not self.is_vowel(name[-3]):
                    return "Cannot parse names with suffix '{}'!".format("К")
                return name[:-1] + "уся"
            else:
                if self.is_endings_with_a(name[-2]):
                    suffix = "очк"
                else:
                    suffix = "еньк"
        elif name[-1] == "я":
            if name[-2] == "ь":
                suffix = "юшк" if name[-3] not in "лмн" else "юш"
            elif name[-2] == "н":
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
    assert diminutiver.get_diminutive("Клава") == "Клавочка"
    assert diminutiver.get_diminutive("Клара") == "Кларочка"
    assert diminutiver.get_diminutive("Лапа") == "Лапочка"
    assert diminutiver.get_diminutive("Рита") == "Риточка"
    assert diminutiver.get_diminutive("Влад") == "Владик"
    assert diminutiver.get_diminutive("Вика") == "Викуся"
    assert diminutiver.get_diminutive("Витя") == "Витенька"
    assert diminutiver.get_diminutive("Витька") == "Cannot parse names with suffix '{}'!".format("К")
    assert diminutiver.get_diminutive("Диана") == "Дианочка"
    assert diminutiver.get_diminutive("Дина") == "Диночка"
    assert diminutiver.get_diminutive("Люда") == "Людочка"
    assert diminutiver.get_diminutive("Людка") == "Cannot parse names with suffix '{}'!".format("К")
    assert diminutiver.get_diminutive("Люба") == "Любочка"
    assert diminutiver.get_diminutive("Влада") == "Владочка"
    assert diminutiver.get_diminutive("Лампа") == "Лампочка"
    assert diminutiver.get_diminutive("Лавка") == "Cannot parse names with suffix '{}'!".format("К")
    assert diminutiver.get_diminutive("Дамба") == "Дамбочка"
    assert diminutiver.get_diminutive("Дарья") == "Дарьюшка"
    assert diminutiver.get_diminutive("Илья") == "Ильюша"
    assert diminutiver.get_diminutive("Игорь") == "Игорёк"
