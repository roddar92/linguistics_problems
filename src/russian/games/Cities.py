# -*- coding: utf-8 -*-
import random
from collections import defaultdict


class Game(object):
    def __init__(self):
        self.allowed_cities = list()
        self.current_cities = list()
        self.allowed_letters = defaultdict(int)
        self.used_letters = defaultdict(int)
        self.UNKNOWN_CITY = [
            "Такого города не существует! Предложи другой:",
            "Не знаю такой город, назови другой:",
            "Такого города нет в моём списке. Предложи другой город:"
        ]
        self.USED_CITY = [
            "Этот город уже был! Давай вспомним какой-нибудь другой город:",
            "Этот город уже был в игре, назови другой:"
        ]

        with open("../resources/ru_cities.txt", "r", encoding='utf-8') as f:
            for line in f:
                name = line.strip()
                self.allowed_cities.append(name)
                self._register_first_letter(name)

    @staticmethod
    def get_city_name(city):
        if '-' in city:
            return "-".join([w.title() for w in city.split("-")])
        elif ' ' in city:
            return " ".join([w.title() for w in city.split()])
        else:
            return city.title()

    @staticmethod
    def has_except_endings(word):
        return word in 'ъыь'

    def _register_first_letter(self, name):
        self.allowed_letters[name[0]] += 1

    def _register_first_letter_in_use_dict(self, name):
        self.used_letters[name[0]] += 1

    def _find_index_of_right_letter(self, previous_city):
        ind = -1
        while self.has_except_endings(previous_city[ind]) \
                or self.used_letters[previous_city[ind]] == self.allowed_letters[previous_city[ind]]:
            ind -= 1
            if not self.has_except_endings(previous_city[ind]) and previous_city[ind] not in self.used_letters:
                break
        return ind

    def _check_rules(self, word):
        if len(self.current_cities) != 0:
            previous_city = self.current_cities[-1]
            ind = self._find_index_of_right_letter(previous_city)
            return previous_city[ind] == word[0]

        return True

    def check_city(self, city):
        if city not in self.allowed_cities:
            raise Exception(random.choice(self.UNKNOWN_CITY))
        elif not self._check_rules(city):
            raise Exception("Этот город не начинается с буквы \'{}\'!"
                            .format(self.current_cities[-1][self._find_index_of_right_letter(self.current_cities[-1])]
                                    .upper()))
        elif city in self.current_cities:
            raise Exception(random.choice(self.USED_CITY))

    def make_city_used(self, city):
        self.current_cities.append(city)
        self._register_first_letter_in_use_dict(city)

    def move(self):
        ind = self._find_index_of_right_letter(self.current_cities[-1])
        letter = self.current_cities[-1][ind]
        cities_starts_with_letter = [word for word in self.allowed_cities
                                     if word.startswith(letter) and word not in self.current_cities]
        city = random.choice(cities_starts_with_letter)
        self.make_city_used(city)
        print(self.get_city_name(city))


if __name__ == "__main__":
    game = Game()
    s = input("Приветствую!\nНачинай игру первым и введи город:\n").lower()
    while True:
        if len(game.allowed_cities) == len(game.current_cities) or s == "Конец".lower():
            print("До новых встреч!")
            break

        try:
            game.check_city(s)
            game.make_city_used(s)
            game.move()
            s = input().lower()
        except Exception as msg:
            print(msg)
            s = input().lower()
