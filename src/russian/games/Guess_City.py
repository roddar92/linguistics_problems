# -*- coding: utf-8 -*-
import random
from collections import defaultdict


class GuessCityGameException(Exception):
    def __init__(self, msg):
        self.msg = msg


class GuessCity(object):
    def __init__(self):
        self.__allowed_cities = defaultdict(list)
        self.__guessed_cities = set()
        self.__asked_cities = set()
        self.__city_name = "Unknown"

        self.__whole_moves_count = 0
        self.__attempts = 0
        self.__ind = 1

        with open("../resources/ru_cities.txt", "r", encoding='utf-8') as f:
            for city in f:
                city = city.strip()
                if city:
                    self.__allowed_cities[city[0]].append(city)

    @staticmethod
    def get_city_name(city_name):
        if '-' in city_name:
            return "-".join([w.title() for w in city_name.split("-")])
        elif ' ' in city_name:
            return " ".join([w.title() for w in city_name.split()])
        else:
            return city_name.title()

    def print_final_text(self):
        if self.__whole_moves_count <= 5:
            print("WOW! You are lucky!")
        elif 5 < self.__whole_moves_count <= 8:
            print("You have a great intuition!")
        elif 8 < self.__whole_moves_count <= 12:
            print("Very nice work!")
        elif 12 < self.__whole_moves_count <= 18:
            print("Not bad...")
        else:
            print("How long you have to solve puzzles!.. But not upset! :) Get ready for the next time!")

    def choose_city(self):
        self.move()
        return input("Your answer: ").lower()

    def __get_hint(self):
        self.__ind += 1
        self.__attempts = 0
        if self.__ind == len(self.__city_name):
            self.__ind = 1
            self.choose_city()
        else:
            print("Well, I shall prompt you another letter!")
            self.__shift_letter(self.__ind)

    def get_guessed_city(self):
        return self.__city_name

    def __make_city_used(self):
        self.__guessed_cities.add(self.__city_name)
        self.__city_name = ""

    def __make_city_asked(self, city_name):
        self.__asked_cities.add(city_name)

    def reset_current_params(self):
        self.__make_city_used()
        self.__clear_asked_cities()

        self.__whole_moves_count = 0
        self.__attempts = 0
        self.__ind = 1
    
    def __clear_asked_cities(self):
        self.__asked_cities.clear()

    def __was_city_asked(self, city_name):
        return city_name in self.__asked_cities

    def __was_city_guessed(self, city_name):
        return city_name in self.__guessed_cities

    def __is_city_exists(self, city_name):
        return city_name in self.__allowed_cities[city_name[0]]
    
    def __shift_letter(self, index):
        if index == len(self.__city_name):
            print(f"The guessed city was {self.__city_name}. This game was over :(")
        else:
            print(self.__city_name[:index] + "...")

    def check_city(self, city_name):
        if self.__was_city_asked(city_name):
            raise GuessCityGameException("You have already asked this city!")
        elif self.__was_city_guessed(city_name):
            raise GuessCityGameException("This city has already guessed!")
        elif not self.__is_city_exists(city_name):
            raise GuessCityGameException("This city was not exists!")

    def move(self):
        random_letter = random.choice(list(self.__allowed_cities.keys()))
        city_names = [word for word in self.__allowed_cities[random_letter] if word not in self.__guessed_cities]
        self.__city_name = self.get_city_name(random.choice(city_names))
        print(f"My guessed city is {self.__city_name[0]}...")

    def generate_fail_answer(self, city=None, catched_ex=None):
        if self.__attempts == 2:
            self.__get_hint()
        elif catched_ex:
            self.__attempts += 1
            print(e)
            print("Try to guess my city again!")
        else:
            self.__make_city_asked(city)
            self.__attempts += 1
            print(f"No... It isn't {self.get_city_name(city)} :( Try to guess my city again!")


if __name__ == "__main__":
    gc = GuessCity()
    print("By welcome! Let's guess cities!")

    s = gc.choose_city()

    while True:
        if s == "the end":
            print("Bye-bye! I hope to see you soon :)")
            break
        try:
            gc.check_city(s)
            if gc.get_city_name(s) == gc.get_guessed_city():
                print(f"Yes! The guessed city was {gc.get_guessed_city()}!")
                gc.print_final_text()
                gc.reset_current_params()
                s = gc.choose_city()
            else:
                gc.generate_fail_answer(s)
                s = input("And your answer is: ").lower()
        except Exception as e:
            gc.generate_fail_answer(catched_ex=e)
            s = input("And your answer is: ").lower()
