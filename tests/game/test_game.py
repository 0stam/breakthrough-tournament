import sys

import pytest

from src.game.game import Game


def test_simple_run():
    game = Game(
        board_size_x=8,
        board_size_y=8,
        first_args=[sys.executable, "tests/game/dummy_process.py"],
        second_args=[sys.executable, "tests/game/dummy_process.py"],
        t_init=1.0,
        t_info_parsing=1.0,
        t_move=1.0
    )

    results = game.run()

    assert not results.first_lost
    assert not results.second_lost