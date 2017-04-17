# -*- coding: utf-8 -*-
from random import randint
import collections
import enchant


class QuizzLetter(object):

    def __init__(self):
        self.status = "undefined"
        self.current_letter = "А"
        self.alphabet = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
        self.ru_dict = enchant.Dict("ru_RU")

    def move(self):
        self.status = "start"
        self.current_letter = self.alphabet[randint(0, len(self.alphabet) - 1)]
        print("Я загадал свою букву!")

    def count_letter(self, word):
        letters_dict = collections.Counter(word)
        count_of_letter = letters_dict[self.current_letter]
        return str(count_of_letter) + "!" if count_of_letter > 0 else "В этом слове нет моей буквы"

    def check_answer(self, word):
        word = word.upper()
        if word in self.alphabet:
            if word == self.current_letter:
                self.status = "over"
                print("Молодец, угадал!")
            else:
                raise Exception("Пока не угадал.")
        elif self.ru_dict.check(word):
            print(self.count_letter(word))
        else:
            raise Exception("Что-то я не понял твоего слова...")


def is_agree():
    return s in "да давай конечно разумеется yes ага".lower().split()


def is_disagree():
    return s.startswith("не") or s.startswith("нет") or s.startswith("No") or s.startswith("no") or \
           s.startswith("конечно нет") or s.startswith("разумеется нет")


def is_end_of_game():
    return s in "конец стоп хватит Конец Стоп Хватит".split()

if __name__ == "__main__":
    game = QuizzLetter()
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
                except Exception as msg:
                    s = input(str(msg) + " " + "Попробуешь ещё разок?\n")
        else:
            break
