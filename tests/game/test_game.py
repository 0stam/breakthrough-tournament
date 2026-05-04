import sys

import pytest

from src.game.game import Game


def test_simple_run():
    game = Game(
        board_size_x=8,
        board_size_y=8,
        first_args=[sys.executable, "-m", "tests.game.dummy_process"],
        second_args=[sys.executable, "-m", "tests.game.dummy_process"],
        t_init=1.0,
        t_info_parsing=1.0,
        t_move=0.05
    )

    results = game.run()

    assert results.first_lost ^ results.second_lost  # Only one has won
    assert not results.first_error_message
    assert not results.second_error_message


def test_bad_init_output():
    game = Game(
        board_size_x=5,
        board_size_y=5,
        first_args=[sys.executable, "-m", "tests.game.dummy_process", "--override-init", "invalid\n"],
        second_args=[sys.executable, "-m", "tests.game.dummy_process"],
        t_init=1.0,
        t_info_parsing=1.0,
        t_move=0.01
    )

    results = game.run()

    assert results.first_lost
    assert not results.second_lost
    assert results.first_error_message
    assert not results.second_error_message


def test_bad_move_output():
    game = Game(
        board_size_x=5,
        board_size_y=5,
        first_args=[sys.executable, "-m", "tests.game.dummy_process"],
        second_args=[sys.executable, "-m", "tests.game.dummy_process", "--override-move", "invalid\n"],
        t_init=1.0,
        t_info_parsing=1.0,
        t_move=0.01
    )

    results = game.run()

    assert not results.first_lost
    assert results.second_lost
    assert not results.first_error_message
    assert results.second_error_message


@pytest.mark.parametrize(
    "allowed_wait,first_wait,second_wait,first_error,second_error",
    [
        (1.0, 0.5, 0.5, False, False),  # Both players within time limit
        (1.0, 1.5, 0.5, True, False),   # First player exceeds time limit
        (1.0, 0.5, 1.5, False, True),   # Second player exceeds time limit
        (1.0, 1.5, 1.5, True, True)     # Both players exceed time limit
    ]
)
def test_init_timeout(allowed_wait, first_wait, second_wait, first_error, second_error):
    game = Game(
        board_size_x=5,
        board_size_y=5,
        first_args=[sys.executable, "-m", "tests.game.dummy_process", "--init-wait", str(first_wait)],
        second_args=[sys.executable, "-m", "tests.game.dummy_process", "--init-wait", str(second_wait)],
        t_init=allowed_wait,
        t_info_parsing=1.0,
        t_move=0.01
    )

    results = game.run()

    if first_error:
        assert results.first_lost
        assert results.first_error_message
    else:
        if second_error:
            assert not results.first_lost
        assert not results.first_error_message

    if second_error:
        assert results.second_lost
        assert results.second_error_message
    else:
        if first_error:
            assert not results.second_lost
        assert not results.second_error_message

def test_multiple_lines_per_move_last_correct():
    game = Game(
        board_size_x=5,
        board_size_y=9,
        first_args=[sys.executable, "-m", "tests.game.dummy_process", "--n-lines-per-move", "3", "--override-non-final-lines", "Gibberish\n"],
        second_args=[sys.executable, "-m", "tests.game.dummy_process"],
        t_init=1.0,
        t_info_parsing=1.0,
        t_move=0.01
    )

    results = game.run()

    assert results.first_lost ^ results.second_lost
    assert not results.first_error_message
    assert not results.second_error_message


def test_multiple_lines_per_move_last_incomplete():
    game = Game(
        board_size_x=5,
        board_size_y=9,
        first_args=[sys.executable, "-m", "tests.game.dummy_process"],
        second_args=[sys.executable, "-m", "tests.game.dummy_process", "--n-lines-per-move", "3", "--override-move", "WWW"],
        t_init=1.0,
        t_info_parsing=1.0,
        t_move=0.01
    )

    results = game.run()

    assert results.first_lost ^ results.second_lost
    assert not results.first_error_message
    assert not results.second_error_message


def test_mixed_input_formats():
    game = Game(
        board_size_x=5,
        board_size_y=9,
        first_args=[sys.executable, "-m", "tests.game.dummy_process", "--input-format", "1"],
        second_args=[sys.executable, "-m", "tests.game.dummy_process", "--input-format", "0"],
        t_init=1.0,
        t_info_parsing=1.0,
        t_move=0.01
    )

    results = game.run()

    assert results.first_lost ^ results.second_lost
    assert not results.first_error_message
    assert not results.second_error_message


def test_mixed_output_formats():
    game = Game(
        board_size_x=5,
        board_size_y=9,
        first_args=[sys.executable, "-m", "tests.game.dummy_process", "--output-format", "1"],
        second_args=[sys.executable, "-m", "tests.game.dummy_process", "--output-format", "0"],
        t_init=1.0,
        t_info_parsing=1.0,
        t_move=0.01
    )

    results = game.run()

    assert results.first_lost ^ results.second_lost
    assert not results.first_error_message
    assert not results.second_error_message


def test_all_mixed_formats():
    game = Game(
        board_size_x=5,
        board_size_y=9,
        first_args=[sys.executable, "-m", "tests.game.dummy_process", "--input-format", "1", "--output-format", "0"],
        second_args=[sys.executable, "-m", "tests.game.dummy_process", "--input-format", "0", "--output-format", "1"],
        t_init=1.0,
        t_info_parsing=1.0,
        t_move=0.01
    )

    results = game.run()

    assert results.first_lost ^ results.second_lost
    assert not results.first_error_message
    assert not results.second_error_message
