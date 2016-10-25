import random

#FIXME from . import constants
import constants


class DieException(Exception):
    pass


class Die(object):
    def __init__(self):
        self.reset()

    def reset(self):
        self.value = None
        self.frozen = False

    def roll(self):
        if self.frozen:
            raise DieException("Die is frozen")
        self.value = random.randint(constants.DICE_LOW_VAL,
                                    constants.DICE_HIGH_VAL)
        return self.value

    def freeze(self):
        if not self.value:
            raise DieException("Cannot freeze an unrolled die")
        self.frozen = True


class DiceSet(object):
    def __init__(self):
        self.dice = [Die() for _ in range(constants.NUM_DICE)]
        self.reset()

    def reset(self):
        for die in self.dice:
            die.reset()

    def roll(self):
        values = []
        for die in self.dice:
            if not die.frozen:
                die.roll()
            values.append(die.value)
        return values

    def freeze_selection(self, selection_list):
        for selection in selection_list:
            selection.freeze()

    def inherit_diceset(self, diceset):
        for index, die in enumerate(diceset):
            self.dice[index].value = die.value
            self.dice[index].frozen = die.frozen

class Player(object):
    def __init__(self):
        self.qualified = False
        self.score = 0
        self.diceset = DiceSet()


