import ast
import collections
import itertools
import random

from . import constants
from . import points
from . import utils


class Die(object):
    def __init__(self, seed=None):
        self.reset()
        if seed:
            random.seed(seed)

    def reset(self):
        self.value = None
        self.frozen = False

    def roll(self):
        if self.frozen:
            raise utils.DieException("Die is frozen")
        self.value = random.randint(constants.DICE_LOW_VAL,
                                    constants.DICE_HIGH_VAL)

    def freeze(self):
        if not self.value:
            raise utils.DieException("Cannot freeze an unrolled die")
        if self.frozen:
            raise utils.DieException("Cannot freeze a frozen die")
        self.frozen = True


class DiceSet(object):
    def __init__(self, seed=None):
        self.dice = [Die(seed) for _ in xrange(constants.NUM_DICE)]
        self.points = 0
        self.reset()

    def reset(self, reset_score=True):
        for die in self.dice:
            die.reset()
        self.roll_ok = True
        if reset_score:
            self.points = 0

    def roll(self):
        if not self.roll_ok:
            raise utils.DiceSetException("Must freeze at least one die first")
        for die in self.dice:
            if not die.frozen:
                die.roll()
                self.roll_ok = False
        if self.check_farkel():
            self.reset()
            raise utils.FarkelException("Farkel!")

    def freeze_selection(self, selection_list):
        if self.roll_ok or not selection_list:
            raise utils.DiceSetException("Must freeze at least one die")
        if any([die.frozen for die in selection_list]):
            raise utils.DiceSetException("A die is already frozen")
        die_values = [die.value for die in selection_list]
        roll_total_points, remaining_dice = points.score_dice(
            collections.Counter(die_values))
        if remaining_dice:
            raise utils.DiceSetException("Some dice didn't score!")
        self.points += roll_total_points
        for selection in selection_list:
            selection.freeze()
        self.roll_ok = True

    def inherit_diceset(self, diceset):
        for index, die in enumerate(diceset.dice):
            self.dice[index].value = die.value
            self.dice[index].frozen = die.frozen
        self.points = diceset.points
        self.roll_ok = True

    def check_farkel(self):
        die_values = [die.value for die in self.dice if not die.frozen]
        score, remaining_dice = \
            points.score_dice(collections.Counter(die_values))
        if score:
            return False
        else:
            return True


class Player(object):
    def __init__(self, seed=None, name=None):
        self.qualified = False
        self.score = 0
        self.farkel_count = 0
        self.diceset = DiceSet(seed)
        self.active = False
        self.name = name

    def bank_points(self):
        if self.qualified:
            self.score += self.diceset.points
            self.farkel_count = 0
        else:
            if self.diceset.points >= constants.QUALIFICATION_POINTS:
                self.qualified = True
            else:
                raise utils.PlayerException(
                    "Need {} points to qualify, player has {}".format(
                        constants.QUALIFICATION_POINTS, self.diceset.points))
        self.active = False

    def roll(self):
        if all([die.frozen for die in self.diceset.dice]):
            self.diceset.reset(reset_score=False)
        try:
            self.diceset.roll()
        except utils.FarkelException:
            self.active = False
            if self.qualified:
                self.farkel_count += 1
                if self.farkel_count >= constants.FARKEL_LIMIT:
                    self.score -= constants.FARKEL_POINTS
            print("You rolled a Farkel!\n")
            return
        dice = [die.value if not die.frozen else 0
                for die in self.diceset.dice]
        print("You rolled the following dice: {}".format(dice))
        return dice

    def freeze_selection(self, selection_list):
        return self.diceset.freeze_selection(
            [die for index, die in enumerate(self.diceset.dice)
             if index in selection_list])

    def make_active(self):
        self.active = True

    def make_inactive(self):
        self.active = True

    def is_active(self):
        return self.active

    def is_win_condition_met(self):
        return self.score >= constants.WIN_CONDITION


class Game(object):
    def __init__(self, num_players):
        self.num_players = num_players
        self.players = [Player(name=i + 1)
                        for i in xrange(self.num_players)]
        self.player_cycle = None
        self.persist = itertools.cycle([True])
        self.last_turn = False
        self.last_player = None
        self.score_to_beat = 0

    def start(self):
        # Determine who starts
        starting_player = random.randint(0, self.num_players)

        # Set up the player cycle
        self.player_cycle = itertools.cycle(self.players)

        # Start on randomly chosen player
        self.player_cycle = itertools.islice(
            self.player_cycle, starting_player, None)

        while next(self.persist):
            self.loop_through_players()

        best_score = 0
        winning_player = ''
        for p in self.players:
            if p.score > best_score:
                best_score = p.score
                winning_player = p.name
        print("\n*********************************************\n"
              "Player {} wins with a score of {}"
              "\n*********************************************\n"
              .format(winning_player, best_score))

    def loop_through_players(self):
        for player_turn in xrange(self.num_players):
            player = self.player_cycle.next()
            player.make_active()

            if self.last_turn and self.score_to_beat == player.score:
                return

            print("---------------------------------------------")
            print("Player {}'s turn, you are {}qualified and have {} "
                  "banked points."
                  .format(player.name, '' if player.qualified else 'not ',
                          player.score))

            if (self.last_player and self.last_player.diceset.points and
                    player.qualified and self.last_player.qualified and
                    self.last_player.score != 0):
                inherit_choice = ''
                while inherit_choice not in ['n', 'y']:
                    inherit_choice = raw_input(
                        "The last player scored {} and left {} dice. "
                        "Would you like to inherit their score "
                        "and dice? Type 'y' or 'n'\n".format(
                            self.last_player.diceset.points,
                            sum([1 for die in
                                 self.last_player.diceset.dice
                                 if not die.frozen]))
                    )
                if inherit_choice == 'y':
                    player.diceset.inherit_diceset(
                        self.last_player.diceset)
                    print("\nRoll inherited, you have {} points"
                          .format(player.diceset.points))
            if self.last_player:
                self.last_player.diceset.reset()

            self.last_player = player

            print("\nInitial roll!")
            player.roll()

            while player.is_active():
                freeze_choice = ''
                while not freeze_choice:
                    freeze_choice = raw_input("\nWrite dice index (as a "
                                              "list) to freeze\n")
                    try:
                        freeze_choice = ast.literal_eval(freeze_choice)
                        player.freeze_selection(freeze_choice)
                        print("\nYou now have {} points".format(
                            player.diceset.points))
                    except (ValueError, SyntaxError):
                        freeze_choice = ''
                    except (utils.DiceSetException, utils.DieException):
                        print("Invalid dice selection")
                        freeze_choice = ''

                if all([die.frozen for die in player.diceset.dice]):
                    print("All dice frozen, re-rolling")
                    player.roll()
                    continue

                if not player.qualified:
                    if (player.diceset.points <
                            constants.QUALIFICATION_POINTS):
                        print("\nNot qualified, must roll again")
                        player.roll()
                    else:
                        print("You qualified!")
                        player.bank_points()
                    continue

                if (self.last_turn and
                    (player.score + player.diceset.points) <
                        self.score_to_beat):
                    print("Must beat {} points, re-rolling"
                          .format(self.score_to_beat))
                    player.roll()
                    continue

                bank_choice = ''
                while bank_choice not in ['b', 'r']:
                    bank_choice = raw_input("\nType 'b' to bank points or "
                                            "'r' to roll\n")
                if bank_choice == 'b':
                    player.bank_points()
                    if self.last_turn:
                        self.score_to_beat = player.score
                    continue
                else:
                    player.roll()
                    continue

            if player.is_win_condition_met():
                if not self.last_turn:
                    self.persist = iter([True, False])
                    self.last_turn = True
                    self.score_to_beat = player.score
                    print(
                        "\n*********************************************\n"
                        "Player {} has over {} points, last turn!"
                        "\n*********************************************\n"
                        .format(player.name, constants.WIN_CONDITION))

                    # Set up player cycle to do one more loop
                    self.player_cycle = itertools.dropwhile(
                        lambda x: x != player, self.player_cycle)
                    self.player_cycle = itertools.islice(
                        self.player_cycle, 1, None)
                    return
