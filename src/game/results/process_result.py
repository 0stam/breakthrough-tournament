from dataclasses import dataclass
from typing import NamedTuple


@dataclass
class ProcessResult:
    lost: list[bool]
    output: list[str]
