import collections
import itertools
import operator

from . import constants
from . import utils

# Dice combinations which are unique
SIMPLE_COMINATIONS = (
    (collections.Counter((1,)), constants.SINGLE_ONE_POINTS),
    (collections.Counter((5,)), constants.SINGLE_FIVE_POINTS),
    (collections.Counter((1, 1, 1)), constants.TRIPLE_ONE_POINTS),
    (collections.Counter((2, 2, 2)), constants.TRIPLE_TWO_POINTS),
    (collections.Counter((3, 3, 3)), constants.TRIPLE_THREE_POINTS),
    (collections.Counter((4, 4, 4)), constants.TRIPLE_FOUR_POINTS),
    (collections.Counter((5, 5, 5)), constants.TRIPLE_FIVE_POINTS),
    (collections.Counter((6, 6, 6)), constants.TRIPLE_SIX_POINTS),
    (collections.Counter((1, 2, 3, 4, 5, 6)), constants.STRAIGHT_POINTS),
)

# Four of a kind
QUADRUPLETS = tuple([(collections.Counter((i + 1,) * 4),
                      constants.QUADS_POINTS)
                     for i in range(constants.DICE_HIGH_VAL)])

# Five of a kind
QUINTUPLETS = tuple([(collections.Counter((i + 1,) * 5),
                      constants.QUINTS_POINTS)
                     for i in range(constants.DICE_HIGH_VAL)])

# Six of a kind
SEXTUPLETS = tuple([(collections.Counter((i + 1,) * 6),
                     constants.SEXTUPS_POINTS)
                    for i in range(constants.DICE_HIGH_VAL)])

# Helper list of pairs, triplets, and quadruplets
PAIRS_LIST = [(i + 1,) * 2 for i in range(constants.DICE_HIGH_VAL)]
TRIPLETS_LIST = [(i + 1,) * 3 for i in range(constants.DICE_HIGH_VAL)]
QUADRUPLETS_LIST = [(i + 1,) * 4 for i in range(constants.DICE_HIGH_VAL)]

# Three pairs
THREE_PAIRS = ((collections.Counter((i + j + k)), constants.THREE_PAIRS_POINTS)
               for i, j, k in
               itertools.product(PAIRS_LIST, PAIRS_LIST, PAIRS_LIST)
               if (i != j and i != k and j != k))
THREE_PAIRS = utils.remove_duplicates(THREE_PAIRS)


# Two triplets
TWO_TRIPLETS = ((collections.Counter((i + j)), constants.TWO_TRIPLETS_POINTS)
                for i, j in itertools.product(TRIPLETS_LIST, TRIPLETS_LIST)
                if i != j)
TWO_TRIPLETS = utils.remove_duplicates(TWO_TRIPLETS)


# Quadruplets and a pair
QUAD_PLUS_PAIR = ((collections.Counter((i + j)), constants.QUADS_PAIRS_POINTS)
                  for i, j in itertools.product(QUADRUPLETS_LIST, PAIRS_LIST)
                  if all(x not in j for x in i))
QUAD_PLUS_PAIR = utils.remove_duplicates(QUAD_PLUS_PAIR)

# An unsorted list of all dice rolls and their values
ALL_POINTS = SIMPLE_COMINATIONS + QUADRUPLETS + QUINTUPLETS + SEXTUPLETS + \
    THREE_PAIRS + TWO_TRIPLETS + QUAD_PLUS_PAIR

# A list of of all dice rolls and their values, sorted by value
ALL_POINTS_SORTED = sorted(
    ALL_POINTS, key=operator.itemgetter(1), reverse=True)


def score_dice(dice_value_counter, score=0):
    remaining_dice = dice_value_counter
    for scoring_values, points in ALL_POINTS_SORTED:
        if not scoring_values - dice_value_counter:
            score += points
            remaining_dice = dice_value_counter - scoring_values
            break
    else:
        return score, remaining_dice
    if not remaining_dice:
        return score, None
    else:
        return score_dice(remaining_dice, score)
