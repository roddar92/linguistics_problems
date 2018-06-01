# -*- coding: utf-8 -*-
import enchant
import random


ATTEMPT_PHRASES = [
    "Попробуешь ещё разок?",
    "Терпение и труд - всё перетрут!",
    "Не сдавайся!",
    "Не сдавайся, развязка всё ближе и ближе!"
]


class SecretLetter(object):

    def __init__(self):
        self.d2w = {1: "Одна", 2: "Две", 3: "Три", 4: "Четыре", 5: "Пять",
                    6: "Шесть", 7: "Семь", 8: "Восемь", 9: "Девять", 10: "Десять"}
        self.status = "undefined"
        self.secret_letter = "А"
        self.alphabet = list("АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ")
        self.ru_dict = enchant.Dict("ru_RU")

    def move(self):
        self.status = "start"
        self.secret_letter = random.choice(self.alphabet)
        print("Я загадал свою букву!")

    def count_letter(self, word):
        count_of_letter = list(word).count(self.secret_letter)
        if count_of_letter > 0:
            return self.d2w[count_of_letter] + "!"
        else:
            raise SecretLetterException("В этом слове нет моей буквы.")

    def check_answer(self, word):
        word = word.upper()
        if word in self.alphabet:
            if word == self.secret_letter:
                self.status = "over"
                print("Молодец, угадал!")
            else:
                raise SecretLetterException("Пока не угадал.")
        elif self.ru_dict.check(word):
            print(self.count_letter(word))
        else:
            raise SecretLetterException("Что-то я не понял твоего слова...")


def is_agree():
    return s in "да давай конечно разумеется yes ага угу".lower().split()


def is_disagree():
    return s.startswith("не") or s.startswith("нет") or s.startswith("No") or s.startswith("no") or \
           s.startswith("конечно нет") or s.startswith("разумеется нет")


def is_end_of_game():
    return s in "конец стоп хватит end".lower().split() or "закончим" in s or "устал" in s


class SecretLetterException(Exception):
    def __init__(self, message):
        self.message = message


if __name__ == "__main__":
    game = SecretLetter()
    while True:
        s = input("Поиграешь со мной ещё раз?" if game.status == "over"
                  else "Привет!\nПоиграешь со мной в игру \"Тайная буква\"? Введи \"Да\" или \"Нет\"\n")

        print("Отлично! :)\nГовори слово, а я буду подсчитывать, сколько раз в слове появилась моя буква."
              " Если ты говоришь букву, я скажу, отгадал или нет."
              "Когда надоест, введи \"Конец\", \"Стоп\" или \"Хватит\""
              if is_agree() else "Жаль... :( Тогда поиграем в следующий раз.")

        if is_agree():
            game.move()
            s = input()
            while True:
                if is_end_of_game():
                    print("Пока-пока!")
                    break
                try:
                    game.check_answer(s)
                    if game.status == "over":
                        break
                    else:
                        s = input()
                except SecretLetterException as sle_msg:
                    s = input(str(sle_msg) + " " + "{}\n".format(random.choice(ATTEMPT_PHRASES)))
        else:
            break
