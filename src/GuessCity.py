# -*- coding: utf-8 -*-
class GuessCity(object):
    def __init__(self):
        self.allowed_cities = set()
        self.guessed_cities = set()
        self.city_name = "Unknown"

        with open("ru_cities.txt", "r", encoding='utf-8') as f:
            for line in f:
                self.allowed_cities.add(line.strip())

    @staticmethod
    def get_city_name(city):
        if '-' in city:
            return "-".join([w[0].upper() + w[1:] for w in city.split("-")])
        elif ' ' in city:
            return " ".join([w[0].upper() + w[1:] for w in city.split()])
        else:
            return city[0].upper() + city[1:]

    def make_city_used(self, city):
        self.guessed_cities.add(city)
    
    def was_city_guessed(self, city):
        return city in self.guessed_cities

    def is_city_exists(self, city):
        return city in self.allowed_cities

    def move(self):
        self.city_name = [word for word in self.allowed_cities if word not in self.guessed_cities]
        print(self.city_name[0])

    def shift_letter(self, index):
        if (index + 1) == len(self.city_name):
            print("The guessed city was {}. Game is over :(".format(self.city_name))
            self.move()
        else:
            print(self.city_name[:index + 1])
