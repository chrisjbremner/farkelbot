class DieException(Exception):
    pass


class DiceSetException(Exception):
    pass


class FarkelException(Exception):
    pass


class PlayerException (Exception):
    pass


def remove_duplicates(items):
    seen = []
    for value in items:
        if value not in seen:
            seen.append(value)
    return tuple(seen)
