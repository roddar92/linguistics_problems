# -*- coding: utf-8 -*-
from random import randint


class MoreOrLessGame:
    def __init__(self):
        self.__number = -1
        self.__numbers = set()
        self.__quizzed_numbers = set()
        self.__left, self.__right = 1, 100

    def __update_fields(self):
        self.__number = -1
        self.__left, self.__right = 1, 100

    def __clear_fields(self):
        self.__number = -1
        self.__numbers.clear()
        self.__quizzed_numbers.clear()

    def move(self):
        self.__numbers.clear()
        self.__number = randint(1, 100)
        while self.__number in self.__quizzed_numbers:
            self.__number = randint(1, 100)
        print("Я загадал число от 1 до 100")

    def check_answer(self, answer):
        try:
            answer = int(answer)
        except:
            raise Exception("Я не понял твоё число.")
        if answer in self.__numbers:
            raise Exception("Ты уже называл такое число.")
        elif answer > 100:
            raise Exception("Ой-ой-ой! Моё число не может быть больше 100.")
        elif answer < self.__left or answer > self.__right:
            raise Exception("Ладно, я тебе подскажу! :) Моё число находится в границах [%d, %d]."
                            % (self.__left, self.__right))
        else:
            self.__numbers.add(answer)
            if answer == self.__number:
                self.__update_fields()
                self.__quizzed_numbers.add(answer)
                print("Ты угадал моё число. Молодец! Сыграешь со мной ещё?")
                self.move()
            else:
                if answer > self.__number:
                    ml = "больше"
                    self.__right = answer
                else:
                    ml = "меньше"
                    self.__left = answer
                print("Твоё число %s моего. Попробуешь ещё разок?" % ml)

    def print_result(self):
        total = len(self.__quizzed_numbers)
        if total % 10 == 2 and total % 100 != 12:
            word = "числа"
        elif total % 10 == 1 and total % 100 != 11:
            word = "число"
        else:
            word = "чисел"
        print("Тогда давай закончим игру! Ты угадал %d %s." % (total, word))
        self.__clear_fields()


def is_agree():
    return s in "Да да Давай давай Yes yes".split()


def is_disagree():
    return s.startswith("не") or s.startswith("нет")


def is_end_of_game():
    return s in "конец стоп хватит Конец Стоп Хватит".split()


if __name__ == "__main__":
    game = MoreOrLessGame()
    s = input("Привет!\nПоиграешь со мной в игру \"Угадай число\"? Введи \"Да\" или \"Нет\"\n")
    print("Отлично! :)\nЯ загадываю числа, а ты отгадываешь их. "
          "Когда надоест, введи \"Конец\", \"Стоп\" или \"Хватит\""
              if is_agree() else "Жаль... :( Тогда поиграем в следующий раз.")
    if is_agree():
        game.move()
        s = input()
        while True:
            if is_end_of_game():
                game.print_result()
                break
            try:
                game.check_answer(s)
                s = input()
            except Exception as msg:
                s = input(str(msg) + " " + "Попробуешь ещё разок?\n")
