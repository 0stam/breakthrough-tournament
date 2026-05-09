import sys

import pytest

from src.player_process.player_process import PlayerProcess
from src.game.game import Game


def test_simple_run():
    first_process = PlayerProcess([sys.executable, "-m", "tests.game.dummy_process"])
    second_process = PlayerProcess([sys.executable, "-m", "tests.game.dummy_process"])

    game = Game(
        board_size_x=8,
        board_size_y=8,
        first_process=first_process,
        second_process=second_process,
        t_process_preparation=1.0,
        t_init=1.0,
        t_info_parsing=1.0,
        t_move=0.05
    )

    results = game.run()

    first_process.cleanup()
    second_process.cleanup()

    assert results.first_lost ^ results.second_lost  # Only one has won
    assert not results.first_error_message
    assert not results.second_error_message


def test_bad_init_output():
    first_process = PlayerProcess([sys.executable, "-m", "tests.game.dummy_process", "--override-init", "invalid\n"])
    second_process = PlayerProcess([sys.executable, "-m", "tests.game.dummy_process"])

    game = Game(
        board_size_x=5,
        board_size_y=5,
        first_process=first_process,
        second_process=second_process,
        t_process_preparation=1.0,
        t_init=1.0,
        t_info_parsing=1.0,
        t_move=0.01
    )

    results = game.run()

    first_process.cleanup()
    second_process.cleanup()

    assert results.first_lost
    assert not results.second_lost
    assert results.first_error_message
    assert not results.second_error_message


def test_bad_move_output():
    first_process = PlayerProcess([sys.executable, "-m", "tests.game.dummy_process"])
    second_process = PlayerProcess([sys.executable, "-m", "tests.game.dummy_process", "--override-move", "invalid\n"])

    game = Game(
        board_size_x=5,
        board_size_y=5,
        first_process=first_process,
        second_process=second_process,
        t_process_preparation=1.0,
        t_init=1.0,
        t_info_parsing=1.0,
        t_move=0.01
    )

    results = game.run()

    first_process.cleanup()
    second_process.cleanup()

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
    first_process = PlayerProcess([sys.executable, "-m", "tests.game.dummy_process", "--init-wait", str(first_wait)])
    second_process = PlayerProcess([sys.executable, "-m", "tests.game.dummy_process", "--init-wait", str(second_wait)])

    game = Game(
        board_size_x=5,
        board_size_y=5,
        first_process=first_process,
        second_process=second_process,
        t_process_preparation=1.0,
        t_init=allowed_wait,
        t_info_parsing=1.0,
        t_move=0.01
    )

    results = game.run()
    
    first_process.cleanup()
    second_process.cleanup()

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
    first_process = PlayerProcess([sys.executable, "-m", "tests.game.dummy_process", "--n-lines-per-move", "3", "--override-non-final-lines", "Gibberish\n"])
    second_process = PlayerProcess([sys.executable, "-m", "tests.game.dummy_process"])

    game = Game(
        board_size_x=5,
        board_size_y=9,
        first_process=first_process,
        second_process=second_process,
        t_process_preparation=1.0,
        t_init=1.0,
        t_info_parsing=1.0,
        t_move=0.01
    )

    results = game.run()

    first_process.cleanup()
    second_process.cleanup()

    assert results.first_lost ^ results.second_lost
    assert not results.first_error_message
    assert not results.second_error_message


def test_multiple_lines_per_move_last_incomplete():
    first_process = PlayerProcess([sys.executable, "-m", "tests.game.dummy_process"])
    second_process = PlayerProcess([sys.executable, "-m", "tests.game.dummy_process", "--n-lines-per-move", "3", "--override-move", "WWW"])

    game = Game(
        board_size_x=5,
        board_size_y=9,
        first_process=first_process,
        second_process=second_process,
        t_process_preparation=1.0,
        t_init=1.0,
        t_info_parsing=1.0,
        t_move=0.01
    )

    results = game.run()

    first_process.cleanup()
    second_process.cleanup()

    assert results.first_lost ^ results.second_lost
    assert not results.first_error_message
    assert not results.second_error_message


def test_mixed_input_formats():
    first_process = PlayerProcess([sys.executable, "-m", "tests.game.dummy_process", "--input-format", "1"])
    second_process = PlayerProcess([sys.executable, "-m", "tests.game.dummy_process", "--input-format", "0"])

    game = Game(
        board_size_x=5,
        board_size_y=9,
        first_process=first_process,
        second_process=second_process,
        t_process_preparation=1.0,
        t_init=1.0,
        t_info_parsing=1.0,
        t_move=0.01
    )

    results = game.run()

    first_process.cleanup()
    second_process.cleanup()

    assert results.first_lost ^ results.second_lost
    assert not results.first_error_message
    assert not results.second_error_message


def test_mixed_output_formats():
    first_process = PlayerProcess([sys.executable, "-m", "tests.game.dummy_process", "--output-format", "1"])
    second_process = PlayerProcess([sys.executable, "-m", "tests.game.dummy_process", "--output-format", "0"])

    game = Game(
        board_size_x=5,
        board_size_y=9,
        first_process=first_process,
        second_process=second_process,
        t_process_preparation=1.0,
        t_init=1.0,
        t_info_parsing=1.0,
        t_move=0.01
    )

    results = game.run()

    first_process.cleanup()
    second_process.cleanup()

    assert results.first_lost ^ results.second_lost
    assert not results.first_error_message
    assert not results.second_error_message


def test_all_mixed_formats():
    first_process = PlayerProcess([sys.executable, "-m", "tests.game.dummy_process", "--input-format", "1", "--output-format", "0"])
    second_process = PlayerProcess([sys.executable, "-m", "tests.game.dummy_process", "--input-format", "0", "--output-format", "1"])

    game = Game(
        board_size_x=5,
        board_size_y=9,
        first_process=first_process,
        second_process=second_process,
        t_process_preparation=1.0,
        t_init=1.0,
        t_info_parsing=1.0,
        t_move=0.01
    )

    results = game.run()

    first_process.cleanup()
    second_process.cleanup()

    assert results.first_lost ^ results.second_lost
    assert not results.first_error_message
    assert not results.second_error_message

