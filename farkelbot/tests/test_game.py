import pytest

from .. import constants
from .. import game
from .. import utils


def test_die():
    die = game.Die(seed=42)

    # Check the default values
    assert(not die.frozen)
    assert(not die.value)

    # Try freezing an unrolled die
    with pytest.raises(utils.DieException):
        die.freeze()

    # Roll the die and check a value
    die.roll()
    assert(die.value)
    assert(not die.frozen)

    # Freeze the die and check it's frozen
    die.freeze()
    assert(die.frozen)

    # Try rolling a frozen dice
    with pytest.raises(utils.DieException):
        die.roll()

    # Reset a dice
    die.reset()
    assert(not die.frozen)
    assert(not die.value)


def test_diceset():
    diceset = game.DiceSet(seed=42)

    # Try freezing a die before rolling
    with pytest.raises(utils.DiceSetException):
        diceset.freeze_selection([diceset.dice[1]])

    # Roll the dice
    diceset.roll()

    # Try rolling without freezing
    with pytest.raises(utils.DiceSetException):
        diceset.roll()

    # Freeze a die
    diceset.freeze_selection([diceset.dice[1]])  # This is a 1
    assert(diceset.dice[1].frozen)
    original_value = diceset.dice[1].value

    # Roll the dice and check the frozen die didn't change
    diceset.roll()
    assert(diceset.dice[1].value == original_value)

    # Reset the dice
    diceset.reset()


def test_inheritance():
    diceset_1 = game.DiceSet(seed=42)
    diceset_2 = game.DiceSet()

    # Roll a diceset and then inherit it
    diceset_1.roll()
    diceset_2.inherit_diceset(diceset_1)

    # Check that the two dicesets are identical
    for index, die in enumerate(diceset_2.dice):
        assert(die.value == diceset_1.dice[index].value)
        assert(die.frozen == diceset_1.dice[index].frozen)
    assert(diceset_2.points == diceset_1.points)


def test_no_scoring():
    player = game.Player()
    player.diceset.dice[0].value = 2
    player.diceset.dice[1].value = 3
    player.diceset.dice[2].value = 4
    player.diceset.dice[3].value = 6
    player.diceset.dice[4].value = 2
    player.diceset.dice[5].value = 3
    player.diceset.roll_ok = False

    assert(player.diceset.check_farkel() is True)


def test_multiple_scoring():
    player = game.Player()
    player.diceset.dice[0].value = 1
    player.diceset.dice[1].value = 2
    player.diceset.dice[2].value = 3
    player.diceset.dice[3].value = 4
    player.diceset.dice[4].value = 6
    player.diceset.dice[5].value = 6
    player.diceset.roll_ok = False
    player.qualified = True

    player.diceset.freeze_selection([player.diceset.dice[0]])

    player.diceset.dice[1].value = 5
    player.diceset.dice[2].value = 2
    player.diceset.dice[3].value = 3
    player.diceset.dice[4].value = 6
    player.diceset.dice[5].value = 4
    player.diceset.roll_ok = False

    player.diceset.freeze_selection([player.diceset.dice[1]])

    player.bank_points()
    assert(player.score == (constants.SINGLE_ONE_POINTS +
                            constants.SINGLE_FIVE_POINTS))


def test_quads_scoring():
    player = game.Player()
    player.diceset.dice[0].value = 1
    player.diceset.dice[1].value = 1
    player.diceset.dice[2].value = 1
    player.diceset.dice[3].value = 1
    player.diceset.dice[4].value = 2
    player.diceset.dice[5].value = 3
    player.diceset.roll_ok = False
    player.qualified = True

    player.diceset.freeze_selection(player.diceset.dice[:4])
    assert(player.diceset.points == constants.QUADS_POINTS)

    player.bank_points()
    assert(player.score == constants.QUADS_POINTS)


def test_qualification():
    player = game.Player(seed=2)

    player.roll()  # 6, 6, 1, 1, 6, 5
    player.diceset.freeze_selection(player.diceset.dice)

    player.roll()  # 5, 2, 4, 4, 4, 1
    player.diceset.freeze_selection([player.diceset.dice[0],
                                     player.diceset.dice[5]])

    player.bank_points()

    assert(player.qualified)
    assert(player.score == 0)
    player.diceset.reset()

    player.roll()  # 3, 3, 5, 6, 6, 4
    player.diceset.freeze_selection([player.diceset.dice[2]])

    player.bank_points()

    assert(player.score == constants.SINGLE_FIVE_POINTS)


def test_triple_farkel_and_score():
    player = game.Player(seed=42)
    starting_points = 2000
    player.score = starting_points
    player.qualified = True
    player.active = True

    assert(player.farkel_count == 0)

    player.roll()  # 4, 1, 2, 2, 5, 5
    player.diceset.freeze_selection([player.diceset.dice[1]])

    player.roll()  # 6, 0, 1, 3, 1, 2
    player.diceset.freeze_selection([player.diceset.dice[2]])

    player.roll()  # 4, 0, 0, 1, 2, 4
    player.diceset.freeze_selection([player.diceset.dice[3]])

    player.roll()
    assert(player.farkel_count == 1)
    assert(player.active is False)
    player.active = True
    player.diceset.reset()

    player.roll()  # 5, 1, 5, 5, 3, 1
    player.diceset.freeze_selection([player.diceset.dice[0]])

    player.roll()  # 0, 6, 3, 1, 1, 6
    player.diceset.freeze_selection([player.diceset.dice[3]])

    player.roll()  # 0, 4, 5, 0, 5, 4
    player.diceset.freeze_selection([player.diceset.dice[4]])

    player.roll()
    assert(player.farkel_count == 2)
    assert(player.active is False)
    player.active = True
    player.diceset.reset()

    player.roll()  # 5, 4, 6, 4, 5, 1
    player.diceset.freeze_selection([player.diceset.dice[0]])

    player.roll()  # 0, 2, 2, 1, 2, 1
    player.diceset.freeze_selection([player.diceset.dice[5]])

    player.roll()
    assert(player.farkel_count == 3)
    assert(player.active is False)
    assert(player.score == starting_points - constants.FARKEL_POINTS)
    player.active = True
    player.diceset.reset()

    player.roll()  # 2, 2, 6, 4, 4, 2
    player.diceset.freeze_selection([player.diceset.dice[0],
                                     player.diceset.dice[1],
                                     player.diceset.dice[5]])

    player.roll()  # 0, 0, 5, 1, 3, 0
    player.diceset.freeze_selection([player.diceset.dice[2],
                                     player.diceset.dice[3]])

    player.roll()
    assert(player.farkel_count == 4)
    assert(player.active is False)
    assert(player.score == starting_points - constants.FARKEL_POINTS * 2)
    player.active = True
    player.diceset.reset()

    player.roll()  # 4, 4, 5, 6, 5, 2
    player.diceset.freeze_selection([player.diceset.dice[2]])

    assert(player.active is True)
    player.bank_points()
    assert(player.active is False)
    assert(player.farkel_count == 0)
    assert(player.score ==
           (starting_points - constants.FARKEL_POINTS * 2 +
            constants.SINGLE_FIVE_POINTS))
