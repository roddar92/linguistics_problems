# -*- coding: utf-8 -*-
from random import randint


class Game(object):
    def __init__(self):
        self.allowed_cities = list()
        self.current_cities = list()
        self.allowed_letters = dict()
        self.used_letters = dict()

        with open("ru_cities.txt", "r", encoding='utf-8') as f:
            for line in f:
                name = line.strip()
                self.allowed_cities.append(name)
                self.register_first_letter(name)

    @staticmethod
    def get_city_name(city):
        if '-' in city:
            return "-".join([w[0].upper() + w[1:] for w in city.split("-")])
        elif ' ' in city:
            return " ".join([w[0].upper() + w[1:] for w in city.split()])
        else:
            return city[0].upper() + city[1:]

    @staticmethod
    def has_except_endings(word):
        return word in 'ъыь'

    def register_first_letter(self, name):
        if name[0] in self.allowed_letters:
            self.allowed_letters[name[0]] += 1
        else:
            self.allowed_letters[name[0]] = 1

    def register_first_letter_in_use_dict(self, name):
        if name[0] in self.used_letters:
            self.used_letters[name[0]] += 1
        else:
            self.used_letters[name[0]] = 1

    def find_index_of_right_letter(self, previous_city):
        ind = -1
        if self.has_except_endings(previous_city[ind]):
            ind = -2
        if previous_city[ind] in self.allowed_letters and previous_city[ind] in self.used_letters:
            while self.has_except_endings(previous_city[ind]) \
                    or self.used_letters[previous_city[ind]] == self.allowed_letters[previous_city[ind]]:
                ind -= 1
                if not self.has_except_endings(previous_city[ind]) and previous_city[ind] not in self.used_letters:
                    break
        return ind

    def check_rules(self, word):
        if len(self.current_cities) != 0:
            previous_city = self.current_cities[-1]
            ind = self.find_index_of_right_letter(previous_city)
            return previous_city[ind] == word[0]
        else:
            return True

    def check_city(self, city):
        if city not in self.allowed_cities:
            raise Exception("Такого города не существует!")
        elif not self.check_rules(city):
            raise Exception("Этот город не начинается с буквы \'{}\'!"
                            .format(self.current_cities[-1][self.find_index_of_right_letter(self.current_cities[-1])]
                                    .upper()))
        elif city in self.current_cities:
            raise Exception("Этот город уже был!")

    def make_city_used(self, city):
        self.current_cities.append(city)
        self.register_first_letter_in_use_dict(city)

    def move(self):
        ind = self.find_index_of_right_letter(self.current_cities[-1])
        letter = self.current_cities[-1][ind]
        cities_starts_with_letter = [word for word in self.allowed_cities
                                     if word.startswith(letter) and word not in self.current_cities]
        city = cities_starts_with_letter[randint(0, len(cities_starts_with_letter) - 1)]
        self.make_city_used(city)
        print(self.get_city_name(city))


if __name__ == "__main__":
    game = Game()
    s = input("Приветствуем!\nВведите город:\n").lower()
    while True:
        if len(game.allowed_cities) == len(game.current_cities) or s == "Конец".lower():
            print("Спасибо за игру!\nДо новых встреч!")
            break

        try:
            game.check_city(s)
            game.make_city_used(s)
            game.move()
            s = input().lower()
        except Exception as msg:
            print(msg)
            s = input("Предложите другой город:\n").lower()
