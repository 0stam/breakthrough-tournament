from enum import IntEnum


class FieldType(IntEnum):
    EMPTY = ord("_")
    FIRST_PLAYER = ord("B")
    SECOND_PLAYER = ord("W")
    MOVE_INDICATOR = ord("o")