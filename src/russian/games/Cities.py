# -*- coding: utf-8 -*-
import random
from collections import defaultdict, Counter


class CitiesGameException(Exception):
    def __init__(self, msg):
        self.msg = msg


class Game(object):
    def __init__(self):
        self.allowed_cities = list()
        self.current_cities = list()

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

        self.allowed_letters = Counter([
            city[0] for city in self.allowed_cities
        ])

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

    def _register_used_first_letter(self, name):
        self.used_letters[name[0]] += 1

    def _is_cities_exausted(self, letter):
        return self.used_letters[letter] == self.allowed_letters[letter]

    def _find_index_of_right_letter(self, previous_city):
        ind = -1
        last_letter = previous_city[ind]
        while self.has_except_endings(last_letter) or self._is_cities_exausted(last_letter):
            ind -= 1
            last_letter = previous_city[ind]
        return ind

    def _check_rules(self, word):
        if len(self.current_cities) != 0:
            previous_city = self.current_cities[-1]
            ind = self._find_index_of_right_letter(previous_city)
            return previous_city[ind] == word[0]

        return True

    def check_city(self, city):
        if city not in self.allowed_cities:
            raise CitiesGameException(random.choice(self.UNKNOWN_CITY))
        elif city in self.current_cities:
            raise CitiesGameException(random.choice(self.USED_CITY))
        elif not self._check_rules(city):
            raise CitiesGameException("Этот город не начинается с буквы \'{}\'!"
                            .format(self.current_cities[-1][self._find_index_of_right_letter(self.current_cities[-1])]
                                    .upper()))
        else:
            self._make_city_used(s)

    def _make_city_used(self, city):
        self.current_cities.append(city)
        self._register_used_first_letter(city)

    def move(self):
        ind = self._find_index_of_right_letter(self.current_cities[-1])
        letter = self.current_cities[-1][ind]
        cities_starts_with_letter = [word for word in self.allowed_cities
                                     if word.startswith(letter) and word not in self.current_cities]
        city = random.choice(cities_starts_with_letter)
        self._make_city_used(city)
        print(self.get_city_name(city))


if __name__ == "__main__":
    game = Game()
    s = input("Приветствую!\nНачинай игру первым и введи город:\n").lower()
    while True:
        if len(game.allowed_cities) == len(game.current_cities) or s == "Конец".lower():
            print("Пока-пока! До новых встреч!")
            break

        try:
            game.check_city(s)
            game.move()
            s = input().lower()
        except Exception as msg:
            print(msg)
            s = input().lower()
