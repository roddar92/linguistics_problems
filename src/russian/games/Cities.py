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
        self.__allowed_cities = defaultdict(list)
        self.__guessed_cities = set()
        self.__previous_city = None
        self.status = "init"

        with open("../resources/ru_cities.txt", "r", encoding='utf-8') as f:
            for city in f:
                city = city.strip()
                if city:
                    self.__allowed_cities[city[0]].append(city)

    @staticmethod
    def get_city_name(city):
        if '-' in city:
            return "-".join([w.title() for w in city.split("-")])
        elif ' ' in city:
            return " ".join([w.title() for w in city.split()])
        else:
            return city.title()

    @staticmethod
    def __has_except_endings(word):
        return word in 'ъыь'

    def __is_cities_exausted(self, letter):
        return self.__allowed_cities[letter] == []

    def __is_all_cities_exausted(self):
        return not self.__allowed_cities

    def __find_index_of_right_letter(self, previous_city):
        ind = -1
        last_letter = previous_city[ind]
        while self.__has_except_endings(last_letter) or self.__is_cities_exausted(last_letter):
            ind -= 1
            last_letter = previous_city[ind]
        return ind

    def __get_last_city(self):
        return self.__previous_city
    
    def __get_right_letter_by_rules(self, city):
        return city[self.__find_index_of_right_letter(city)]

    def __check_rules(self, word):
        if self.__previous_city:
            return self.__get_right_letter_by_rules(self.__previous_city) == word[0]
        return True

    def __make_city_used(self, city):
        self.__previous_city = city
        self.__guessed_cities.add(city)
        self.__allowed_cities[city[0]].remove(city)
        if len(self.__allowed_cities[city[0]]) == 0:
            del self.__allowed_cities[city[0]]

    def __check_city(self, city):
        if city in self.__guessed_cities:
            raise CitiesGameException(random.choice(self.USED_CITY))
        elif city[0] not in self.__allowed_cities or city not in self.__allowed_cities[city[0]]:
            raise CitiesGameException(random.choice(self.UNKNOWN_CITY))
        elif not self.__check_rules(city):
            l = self.__get_right_letter_by_rules(self.__get_last_city()).upper()
            raise CitiesGameException(f"Этот город не начинается с буквы \'{l}\'!")
        else:
            self.__make_city_used(city)

    def move(self):
        last_letter = self.__get_right_letter_by_rules(self.__get_last_city())
        city = random.choice(self.__allowed_cities[last_letter])
        self.__make_city_used(city)
        print(self.get_city_name(city))

    def check_and_move(self, city):
        if city.lower() in self.BYE_PHRASES:
            self.status = "over"
        else:
            self.__check_city(s)
            self.status = "over" if self.__is_all_cities_exausted() else "proceed"
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
