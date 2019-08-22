# -*- coding: utf-8 -*-
import random
from collections import defaultdict


class OppositesGame(object):
    def __init__(self):
        self.status = "unknown"
        self.__opposites_dictionary = defaultdict(list)
        self.__answers = ''
        self.__quessed_keys = list()
        self.__current_key = ''
        self.__current_vals = list()
        self.__attempts = 1

        self.RIGHT_ANSWER = [
            "Да, всё правильно! :)",
            "Здорово! Так держать! :)",
            "Правильно. Молодец!"
        ]

        with open("../resources/ru_opposites.txt", "r", encoding='utf-8') as f:
            for line in f:
                (word, opposites) = line.split()
                opposites = opposites.split(",")
                self.__opposites_dictionary[word].extend(list(opposites))
                for opposite in opposites:
                    if opposite not in self.__opposites_dictionary:
                        self.__opposites_dictionary[opposite] = list()
                    self.__opposites_dictionary[opposite].append(word)

                    # TODO refactoring links for synonyms
                    for w in self.__opposites_dictionary[opposite]:
                        if opposite not in self.__opposites_dictionary[w]:
                            self.__opposites_dictionary[w].append(opposite)

    def __synonyms(self, values):
        synonyms = list()
        for value in values:
            synonyms.extend(self.__opposites_dictionary[value])
        return set(synonyms)

    def move(self):
        self.__current_key = random.choice(
            [key for key in self.__opposites_dictionary.keys() if key not in self.__quessed_keys]
        )
        self.__current_vals = self.__opposites_dictionary[self.__current_key]
        print(self.__current_key)

    def check_answer(self, word):
        if is_end_of_game(word):
            self.status = "over"
            print("Тогда давай закончим игру! Мы правильно ответили на " +
                  str(self.__answers.count('1')) + " вопросов из " + str(len(self.__answers)) + ".")
            self.__answers = ''
        elif word in self.__current_vals:
            self.__attempts = 1
            self.__quessed_keys.append(self.__current_key)
            self.__answers += '1'
            print(random.choice(self.RIGHT_ANSWER))
        elif self.__attempts == 1 and (word == self.__current_key or word in self.__synonyms(self.__current_vals)):
            self.__attempts += 1
            raise Exception("Ты угадал синоним, но не противоположное слово.")
        else:
            if self.__attempts == 2:
                self.__attempts = 1
                self.__answers += '0'
                print("Увы, правильный ответ - " + random.choice(self.__current_vals))
            else:
                self.__attempts += 1
                raise Exception("Извини, но я не понял твоего ответа.")


def is_agree(string):
    return string in "да давай конечно разумеется yes ага".lower().split()


def is_disagree(string):
    return string.startswith("не") or string.lower().startswith("нет") or string.lower().startswith("no") or \
           string.startswith("конечно нет") or string.startswith("разумеется нет")


def is_end_of_game(string):
    return string in "конец стоп хватит end".lower().split() or \
           "закончим" in string or string == "устал" or string == "устала"


if __name__ == "__main__":
    game = OppositesGame()
    while True:
        s = input("Поиграешь со мной ещё?\n" if game.status == "over"
                  else "Привет!\nПоиграешь со мной в игру \"Противоположности\"?\n")

        print("Отлично! :)\nЯ говорю слово, а ты подбираешь слово, противоположное моему.\n"
              "Когда надоест, введи \"Конец\", \"Стоп\" или \"Хватит\""
              if is_agree(s) else "Жаль... :( Тогда поиграем в следующий раз.")

        if is_agree(s):
            game.move()
            s = input()
            while True:
                try:
                    game.check_answer(s)
                    if game.status == "over":
                        break
                    else:
                        game.move()
                        s = input()
                except Exception as sle_msg:
                    s = input(str(sle_msg) + " " + "Попробуешь ещё разок?\n")
        else:
            break
