# -*- coding: utf-8 -*-
import random


class OppositesGame(object):
    def __init__(self):
        self.status = "unknown"
        self.opposites_dictionary = dict()
        self.answers = list()
        self.current_key = ''
        self.current_vals = list()
        self.attempts = 1

        with open("ru_opposites.txt", "r", encoding='utf-8') as f:
            for line in f:
                (word, opposites) = line.split()
                opposites = opposites.split(",")
                if word not in self.opposites_dictionary:
                    self.opposites_dictionary[word] = list(opposites)
                else:
                    self.opposites_dictionary[word].extend(list(opposites))
                for opposite in opposites:
                    if opposite not in self.opposites_dictionary:
                        self.opposites_dictionary[opposite] = list()
                    self.opposites_dictionary[opposite].append(word)

                    # TODO refactoring links for synonyms
                    for w in self.opposites_dictionary[opposite]:
                        if opposite not in self.opposites_dictionary[w]:
                            self.opposites_dictionary[w].append(opposite)

    def synonyms(self, values):
        synonyms = list()
        for value in values:
            synonyms.extend(self.opposites_dictionary[value])
        return set(synonyms)

    def move(self):
        i = random.randint(0, len(list(self.opposites_dictionary)) - 2)
        self.current_key = list(self.opposites_dictionary.keys())[i]
        self.current_vals = self.opposites_dictionary[self.current_key]
        print(self.current_key)

    def check_answer(self, word):
        if is_end_of_game(word):
            self.status = "over"
            print("Тогда давай закончим игру! Мы правильно ответили на " +
                  str(sum([i for i in self.answers if i == 1])) + " вопросов из " + str(len(self.answers)) + ".")
            self.answers.clear()
        elif word in self.current_vals:
            self.attempts = 1
            self.answers.append(1)
            print("Да, всё правильно! :)")
        elif self.attempts == 1 and (word == self.current_key or word in self.synonyms(self.current_vals)):
            self.attempts += 1
            raise Exception("Ты угадал синоним, но не противоположное слово.")
        else:
            if self.attempts == 2:
                self.attempts = 1
                self.answers.append(0)
                print("Увы, правильный ответ - " + random.choice(self.current_vals))
            else:
                self.attempts += 1
                raise Exception("Извини, но я не понял твоего ответа.")


def is_agree(string):
    return string in "да давай конечно разумеется yes ага".lower().split()


def is_disagree(string):
    return string.startswith("не") or string.lower().startswith("нет") or string.lower().startswith("no") or \
           string.startswith("конечно нет") or string.startswith("разумеется нет")


def is_end_of_game(string):
    return string in "конец стоп хватит end".lower().split() or "закончим" in string or "устал" in string


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
