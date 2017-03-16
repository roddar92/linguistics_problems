# -*- coding: utf-8 -*-
from random import randint


class MoreOrLessGame:
    def __init__(self):
        self.number = -1
        self.numbers = set()
        self.quizzed_numbers = set()
        self.left, self.right = 1, 100

    def update_fields(self):
        self.number = -1
        self.left, self.right = 1, 100

    def clear_fields(self):
        self.number = -1
        self.numbers.clear()
        self.quizzed_numbers.clear()

    def move(self):
        self.numbers.clear()
        self.number = randint(1, 100)
        while self.number in self.quizzed_numbers:
            self.number = randint(1, 100)
        print("Я загадал число от 1 до 100")

    def check_answer(self, answer):
        try:
            answer = int(answer)
        except:
            raise Exception("Я не понял твоё число.")
        if answer in self.numbers:
            raise Exception("Ты уже называл такое число.")
        elif answer > 100:
            raise Exception("Ой-ой-ой! Моё число не может быть больше 100.")
        elif answer < self.left or answer > self.right:
            raise Exception("Ладно, я тебе подскажу! :) Моё число находится в границах [%d, %d]."
                            % (self.left, self.right))
        else:
            self.numbers.add(answer)
            if answer == self.number:
                self.update_fields()
                self.quizzed_numbers.add(answer)
                print("Ты угадал моё число. Молодец! Сыграешь со мной ещё?")
                self.move()
            else:
                if answer > self.number:
                    ml = "больше"
                    self.right = answer
                else:
                    ml = "меньше"
                    self.left = answer
                print("Твоё число %s моего. Попробуешь ещё разок?" % ml)

    def print_result(self):
        total = len(self.quizzed_numbers)
        if total % 10 == 2 and total % 100 != 12:
            word = "числа"
        elif total % 10 == 1 and total % 100 != 11:
            word = "число"
        else:
            word = "чисел"
        print("Тогда давай закончим игру! Ты угадал %d %s." % (total, word))
        self.clear_fields()


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
              if s == "Да" else "Жаль... :( Тогда поиграем в следующий раз.")
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
