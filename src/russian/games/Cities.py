# -*- coding: utf-8 -*-
import random
from collections import defaultdict, Counter


class CitiesGameException(Exception):
    def __init__(self, msg):
        self.msg = msg


class Game(object):
    def __init__(self):
        self.UNKNOWN_CITY = [
            "Такого города не существует! Предложи другой:",
            "Не знаю такой город, назови другой:",
            "Такого города нет в моём списке. Предложи другой город:"
        ]
        self.USED_CITY = [
            "Этот город уже был! Давай вспомним какой-нибудь другой город:",
            "Этот город уже был в игре, назови другой:"
        ]
        self.BYE_PHRASES = [
            "конец",
            "хватит",
            "устал",
            "надоело",
            "отстань"
        ]

        self.allowed_cities = list()
        self.current_cities = list()
        self.status = "init"

        self.used_letters = defaultdict(int)

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

    def _is_all_cities_exausted(self):
        return set(self.allowed_cities) == set(self.current_cities)

    def _find_index_of_right_letter(self, previous_city):
        ind = -1
        last_letter = previous_city[ind]
        while self.has_except_endings(last_letter) or self._is_cities_exausted(last_letter):
            ind -= 1
            last_letter = previous_city[ind]
        return ind

    def _get_last_city(self):
        return self.current_cities[-1]

    def _check_rules(self, word):
        if len(self.current_cities) != 0:
            previous_city = self.current_cities[-1]
            ind = self._find_index_of_right_letter(previous_city)
            return previous_city[ind] == word[0]

        return True

    def _make_city_used(self, city):
        self.current_cities.append(city)
        self._register_used_first_letter(city)

    def check_city(self, city):
        if city not in self.allowed_cities:
            raise CitiesGameException(random.choice(self.UNKNOWN_CITY))
        elif city in self.current_cities:
            raise CitiesGameException(random.choice(self.USED_CITY))
        elif not self._check_rules(city):
            previous_city = self._get_last_city()
            correct_letter_index = self._find_index_of_right_letter(previous_city)
            raise CitiesGameException("Этот город не начинается с буквы \'{}\'!".format(
                previous_city[correct_letter_index].upper()
            ))
        else:
            self._make_city_used(city)

    def move(self):
        last_city = self._get_last_city()
        ind = self._find_index_of_right_letter(last_city)
        letter = last_city[ind]
        cities_starts_with_letter = [word for word in self.allowed_cities
                                     if word.startswith(letter) and word not in self.current_cities]
        city = random.choice(cities_starts_with_letter)
        self._make_city_used(city)
        print(self.get_city_name(city))

    def check_and_move(self, city):
        if city.lower() in self.BYE_PHRASES:
            self.status = "over"
        else:
            self.check_city(s)
            self.status = "over" if self._is_all_cities_exausted() else "proceed"
            self.move()

    def is_over(self):
        return self.status == "over"


if __name__ == "__main__":
    game = Game()
    s = input("Приветствую!\nНачинай игру первым и введи город:\n").lower()
    while True:
        try:
            game.check_and_move(s)

            if game.is_over():
                print("Пока-пока! До новых встреч!")
                break

            s = input().lower()
        except Exception as e:
            print(e)
            s = input().lower()
