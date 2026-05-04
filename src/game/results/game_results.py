from dataclasses import dataclass


@dataclass
class GameResults:
    first_lost: bool
    second_lost: bool
    first_error_message: str|None
    second_error_message: str|None
