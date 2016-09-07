# -*- coding: utf-8 -*-
# Project : design-pattern
# Created by igor on 16/9/7

'''
“Basically, an Abstract Factory is a (logical) group of Factory Methods, where each Factory Method is responsible for generating a different kind of object”

摘录来自: “Mastering Python Design Patterns”。 iBooks.
'''


class Forg:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

    def interact_with(self, obstacle):
        print("{} the Frog encounters {} and {}!".format(
            self, obstacle, obstacle.action()
        ))


class Bug:
    def __str__(self):
        return "a bug"

    def action(self):
        return "eats it"


class ForgWorld:
    '''
    An Abstract Factory
    creating the main character and obstacle(s) of the game
    '''

    def __init__(self, name):
        print(self)
        self.player_name = name

    def __str__(self):
        return "\n\n\t------- Frog World -------"

    def make_character(self):
        return Forg(self.player_name)

    def make_obstacle(self):
        return Bug()


class Wizard:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

    def interact_with(self, obstacle):
        print('{} the Wizard battles against {} and {}!'.format(
            self, obstacle, obstacle.action()
        ))


class Ork:
    def __str__(self):
        return "an evil ork"

    def action(self):
        return "kills it"


class WizardWorld:
    def __init__(self, name):
        print(self)
        self.player_name = name

    def __str__(self):
        return "\n\n\t------- Wizard World -------"

    def make_character(self):
        return Wizard(self.player_name)

    def make_obstacle(self):
        return Ork()


class GameEnvironment:
    '''
    main entry point of game
    accepts factory as input and uses it to create the world of the game
    '''

    def __init__(self, factory):
        self.hero = factory.make_character()
        self.obstacle = factory.make_obstacle()

    def play(self):
        self.hero.interact_with(self.obstacle)


def validate_age(name):
    try:
        age = input("Welcome {}. How old are you?".format(name))
        age = int(age)
    except ValueError as err:
        print("Age {} is invalid, please try again... ".format(age))
        return False, age
    return True, age


def main():
    name = input("Hello. What's your name? ")
    valid_input = False
    while not valid_input:
        valid_input, age = validate_age(name)
        game = ForgWorld if age < 18 else WizardWorld
        environment = GameEnvironment(game(name))
        environment.play()


if __name__ == '__main__':
    main()
