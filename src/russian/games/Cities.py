# -*- coding: utf-8 -*-
import random
from collections import defaultdict


class CitiesGameException(Exception):
    def __init__(self, msg):
        self.msg = msg


class Game(object):
    UNKNOWN_CITY = [
        "Такого города не существует! Предложи другой:",
        "Не знаю такой город, назови другой:",
        "Такого города нет в моём списке. Предложи другой:"
    ]
    USED_CITY = [
        "Этот город уже был! Давай вспомним какой-нибудь другой:",
        "Этот город уже был в игре, назови другой:"
    ]
    BYE_PHRASES = [
        "стоп",
        "конец",
        "хватит",
        "устал",
        "надоело",
        "отстань"
    ]

    def __init__(self):
        self.allowed_cities = defaultdict(list)
        self.guessed_cities = set()
        self.previous_city = None
        self.status = "init"

        with open("../resources/ru_cities.txt", "r", encoding='utf-8') as f:
            for city in f:
                city = city.strip()
                if city:
                    self.allowed_cities[city[0]] += [city]

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

    def _is_cities_exausted(self, letter):
        return self.allowed_cities[letter] == []

    def _is_all_cities_exausted(self):
        return not self.allowed_cities

    def _find_index_of_right_letter(self, previous_city):
        ind = -1
        last_letter = previous_city[ind]
        while self.has_except_endings(last_letter) or self._is_cities_exausted(last_letter):
            ind -= 1
            last_letter = previous_city[ind]
        return ind

    def _get_last_city(self):
        return self.previous_city

    def _check_rules(self, word):
        if len(self.guessed_cities) != 0:
            ind = self._find_index_of_right_letter(self.previous_city)
            return self.previous_city[ind] == word[0]

        return True

    def _make_city_used(self, city):
        self.previous_city = city
        self.guessed_cities.add(city)
        self.allowed_cities[city[0]].remove(city)
        if len(self.allowed_cities[city[0]]) == 0:
            del self.allowed_cities[city[0]]

    def check_city(self, city):
        if city in self.guessed_cities:
            raise CitiesGameException(random.choice(self.USED_CITY))
        elif city[0] not in self.allowed_cities or city not in self.allowed_cities[city[0]]:
            raise CitiesGameException(random.choice(self.UNKNOWN_CITY))
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
        city = random.choice(self.allowed_cities[letter])
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
