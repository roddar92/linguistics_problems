# -*- coding: utf-8 -*-
from random import randint


class GuessCity(object):
    def __init__(self):
        self.allowed_cities = set()
        self.guessed_cities = set()
        self.asked_cities = set()
        self.city_name = "Unknown"

        with open("ru_cities.txt", "r", encoding='utf-8') as f:
            for line in f:
                self.allowed_cities.add(line.strip())

    @staticmethod
    def get_city_name(city_name):
        if '-' in city_name:
            return "-".join([w[0].upper() + w[1:] for w in city_name.split("-")])
        elif ' ' in city_name:
            return " ".join([w[0].upper() + w[1:] for w in city_name.split()])
        else:
            return city_name[0].upper() + city_name[1:]

    @staticmethod
    def print_final_text(moves_count):
        if moves_count <= 5:
            print("WOW! You are lucky!")
        elif 5 < moves_count <= 8:
            print("You have a great intuition!")
        elif 8 < moves_count <= 12:
            print("Very nice work!")
        elif 12 < moves_count <= 18:
            print("Not bad...")
        else:
            print("How long you have to solve puzzles... But not upset! :) Get ready for the next time!")

    def choose_city(self):
        self.move()
        return input("Your answer: ").lower()

    def get_hint(self):
        global attempts, city, ind
        ind += 1
        attempts = 0
        if ind == len(self.city_name):
            ind = 1
            gc.choose_city()
        else:
            print("Well, I shall prompt you another letter!")
            gc.shift_letter(ind)
            city = input("And your answer: ").lower()

    def get_guessed_city(self):
        return self.city_name

    def make_city_used(self):
        self.guessed_cities.add(self.city_name)
        self.city_name = ""

    def make_city_asked(self, city_name):
        self.asked_cities.add(city_name)
    
    def clear_asked_cities(self):
        self.asked_cities.clear()

    def was_city_asked(self, city_name):
        return city_name in self.asked_cities

    def was_city_guessed(self, city_name):
        return city_name in self.guessed_cities

    def is_city_exists(self, city_name):
        return city_name in self.allowed_cities

    def check_city(self, city_name):
        if self.was_city_asked(city_name):
            raise Exception("You have already asked this city!")
        elif self.was_city_guessed(city_name):
            raise Exception("This city has already guessed!")
        elif not self.is_city_exists(city_name):
            raise Exception("This city was not exists!")

    def move(self):
        city_names = [word for word in self.allowed_cities if word not in self.guessed_cities]
        self.city_name = city_names[randint(0, len(city_names) - 1)]
        print("My guessed city is {}...".format(self.get_city_name(self.city_name)[0]))

    def shift_letter(self, index):
        if index == len(self.city_name):
            print("The guessed city was {}. This game was over :(".format(self.get_city_name(self.city_name)))
        else:
            print(self.get_city_name(self.city_name)[:index] + "...")


if __name__ == "__main__":
    gc = GuessCity()
    print("By welcome! Let's guess cities!")
    whole_moves_count = 0
    attempts = 0
    ind = 1

    city = gc.choose_city()

    while True:
        if city == "the end":
            print("Bye-bye! I hope to see you soon :)")
            break
        try:
            gc.check_city(city)
            if city == gc.get_guessed_city():
                print("Yes! The guessed city was {}!".format(gc.get_city_name(gc.get_guessed_city())))
                gc.print_final_text(whole_moves_count)
                gc.make_city_used()
                gc.clear_asked_cities()
                whole_moves_count = 0
                attempts = 0
                ind = 1
                city = gc.choose_city()
            else:
                if attempts == 2:
                    gc.get_hint()
                else:
                    whole_moves_count += 1
                    attempts += 1
                    gc.make_city_asked(city)
                    city = input("No... It isn't {} :( Try to guess my city again: "
                                 .format(gc.get_city_name(city))).lower()
        except Exception as msg:
            print(msg)
            if attempts == 2:
                gc.get_hint()
            else:
                whole_moves_count += 1
                attempts += 1
                city = input("Try to guess my city again: ").lower()
