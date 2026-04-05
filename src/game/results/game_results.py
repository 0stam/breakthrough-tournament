from dataclasses import dataclass


@dataclass
class GameResults:
    first_lost: bool
    second_lost: bool