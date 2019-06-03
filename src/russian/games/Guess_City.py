# -*- coding: utf-8 -*-
import random
from collections import defaultdict


class GuessCityGameException(Exception):
    def __init__(self, msg):
        self.msg = msg


class GuessCity(object):
    def __init__(self):
        self.allowed_cities = defaultdict(list)
        self.guessed_cities = set()
        self.asked_cities = set()
        self.city_name = "Unknown"

        self.whole_moves_count = 0
        self.attempts = 0
        self.ind = 1

        with open("../resources/ru_cities.txt", "r", encoding='utf-8') as f:
            for city in f:
                city = city.strip()
                if city:
                    self.allowed_cities[city[0]] += [city]

    @staticmethod
    def get_city_name(city_name):
        if '-' in city_name:
            return "-".join([w.title() for w in city_name.split("-")])
        elif ' ' in city_name:
            return " ".join([w.title() for w in city_name.split()])
        else:
            return city_name.title()

    def print_final_text(self):
        if self.whole_moves_count <= 5:
            print("WOW! You are lucky!")
        elif 5 < self.whole_moves_count <= 8:
            print("You have a great intuition!")
        elif 8 < self.whole_moves_count <= 12:
            print("Very nice work!")
        elif 12 < self.whole_moves_count <= 18:
            print("Not bad...")
        else:
            print("How long you have to solve puzzles!.. But not upset! :) Get ready for the next time!")

    def choose_city(self):
        self.move()
        return input("Your answer: ").lower()

    def get_hint(self):
        self.ind += 1
        self.attempts = 0
        if self.ind == len(self.city_name):
            self.ind = 1
            gc.choose_city()
        else:
            print("Well, I shall prompt you another letter!")
            gc.shift_letter(self.ind)

    def get_guessed_city(self):
        return self.city_name

    def _make_city_used(self):
        self.guessed_cities.add(self.city_name)
        self.city_name = ""

    def make_city_asked(self, city_name):
        self.asked_cities.add(city_name)

    def reset_current_params(self):
        self._make_city_used()
        self._clear_asked_cities()

        self.whole_moves_count = 0
        self.attempts = 0
        self.ind = 1
    
    def _clear_asked_cities(self):
        self.asked_cities.clear()

    def _was_city_asked(self, city_name):
        return city_name in self.asked_cities

    def _was_city_guessed(self, city_name):
        return city_name in self.guessed_cities

    def _is_city_exists(self, city_name):
        return city_name in self.allowed_cities[city_name[0]]

    def check_city(self, city_name):
        if self._was_city_asked(city_name):
            raise GuessCityGameException("You have already asked this city!")
        elif self._was_city_guessed(city_name):
            raise GuessCityGameException("This city has already guessed!")
        elif not self._is_city_exists(city_name):
            raise GuessCityGameException("This city was not exists!")

    def move(self):
        random_letter = random.choice(list(self.allowed_cities.keys()))
        city_names = [word for word in self.allowed_cities[random_letter] if word not in self.guessed_cities]
        self.city_name = self.get_city_name(random.choice(city_names))
        print(f"My guessed city is {self.city_name[0]}...")

    def shift_letter(self, index):
        if index == len(self.city_name):
            print(f"The guessed city was {self.city_name}. This game was over :(")
        else:
            print(self.city_name[:index] + "...")

    def generate_fail_answer(self, city=None, catched_ex=None):
        if self.attempts == 2:
            self.get_hint()
        elif catched_ex:
            self.attempts += 1
            print(e)
            print("Try to guess my city again!")
        else:
            self.make_city_asked(city)
            self.attempts += 1
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
