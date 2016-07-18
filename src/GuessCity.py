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

    def get_guessed_city(self):
        return self.city_name

    def make_city_used(self):
        self.guessed_cities.add(self.city_name)
        self.city_name = ""
    
    def was_city_guessed(self, city_name):
        return city_name in self.guessed_cities

    def is_city_exists(self, city_name):
        return city_name in self.allowed_cities

    def check_city(self, city_name):
        if self.was_city_guessed(city_name):
            raise Exception("This city has already guessed!")
        elif not self.is_city_exists(city_name):
            raise Exception("This city was not exists")

    def move(self):
        self.city_name = [word for word in self.allowed_cities if word not in self.guessed_cities]
        print("My guessed city is " + self.city_name[0] + "...")

    def shift_letter(self, index):
        if index == len(self.city_name):
            print("The guessed city was {}. Game is over :(".format(self.city_name))
        else:
            print(self.city_name[:index] + "...")


if __name__ == "__main__":
    gc = GuessCity()
    print("By welcome! Let's quess cities!")
    whole_moves_count = 0
    attempts = 0

    gc.move()
    city = input("Your answer: ").lower()

    while True:
            if city == "the end":
                print("Bye-bye! We hope to see you soon :)")
                break

            gc.check_city(city)
            if city == gc.get_guessed_city():
                print("Yes! The guessed city was {}!".format(gc.get_guessed_city()))
                gc.print_final_text(whole_moves_count)
                gc.make_city_used()
                whole_moves_count = 0
                attempts = 0
                ind = 1
                gc.move()
                city = input("Your answer: ").lower()
            else:
                whole_moves_count += 1
                ind += 1
                if attempts == 3:
                    gc.shift_letter(ind)
                    if ind == len(gc.get_guessed_city()):
                        gc.move()
                        city = input("Your answer: ").lower()
        except Exception as msg:
            print(msg)
            s = input("Try input city again: ")
