from dataclasses import dataclass
from typing import NamedTuple


@dataclass
class ProcessResult:
    first_lost: bool
    second_lost: bool
    first_output: str
    second_output: str
