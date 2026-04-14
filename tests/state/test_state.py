import pytest
import numpy as np

from src.state.state import check_win, create_board, numpy_to_str, str_to_numpy, validate_new_state
from src.state.exceptions import InvalidInputException


@pytest.mark.parametrize(
    "size_x,size_y,expected",
    [
        (
            2, 5,
            np.array([[66, 66, 95, 87, 87], [66, 66, 95, 87, 87]])
        ),
        (
            8, 8,
            np.array([[66, 66, 95, 95, 95, 95, 87, 87]] * 8)
        )
    ]
)
def test_create_board(size_x, size_y, expected):
    board = create_board(size_x, size_y)

    assert board.shape == expected.shape

    print(board)

    assert np.all(board == expected)


@pytest.mark.parametrize(
    "test_arr,expected",
    [
        (
            np.array([[87, 87, 95, 95, 66, 66], [87, 87, 95, 95, 66, 66], [87, 87, 95, 95, 66, 66], [87, 87, 95, 95, 66, 66]]),
            "B B B B B B B B _ _ _ _ _ _ _ _ W W W W W W W W",
        ),
        (
            np.array([[66, 95, 95, 95, 95, 95, 95, 87], [95, 66, 95, 95, 95, 95, 95, 95], [95, 95, 95, 95, 66, 95, 95, 95],
                      [95, 111, 95, 95, 95, 95, 95, 95], [95, 95, 66, 87, 87, 95, 95, 95], [95] * 8,
                      [95, 95, 95, 95, 95, 95, 87, 95], [95, 95, 66, 95, 95, 95, 95, 95]]),
            "W _ _ _ _ _ _ _ _ _ _ _ _ _ W _ _ _ _ _ _ _ _ _ _ _ B _ W _ _ _ _ _ _ _ W _ _ _ _ _ _ _ B _ _ B _ B _ o _ _ _ _ B _ _ _ _ _ _ _",
        )
    ]
)
def test_numpy_to_str(test_arr, expected):
    assert numpy_to_str(test_arr) == expected


@pytest.mark.parametrize(
    "test_text,size_x,size_y,expected",
    [
        (
            "B B B B B B B B _ _ _ _ _ _ _ _ W W W W W W W W",
            4,
            6,
            np.array([[87, 87, 95, 95, 66, 66], [87, 87, 95, 95, 66, 66], [87, 87, 95, 95, 66, 66], [87, 87, 95, 95, 66, 66]])
        ),
        (
            #- - - - - - - -#- - - - - - - -#- - - - - - - -#- - - - - - - -#- - - - - - - -#- - - - - - - -#- - - - - - - -#- - - - - - - -#
            "W _ _ _ _ _ _ _ _ _ _ _ _ _ W _ _ _ _ _ _ _ _ _ _ _ B _ W _ _ _ _ _ _ _ W _ _ _ _ _ _ _ B _ _ B _ B _ o _ _ _ _ B _ _ _ _ _ _ _",
            8,
            8,
            np.array([[66, 95, 95, 95, 95, 95, 95, 87], [95, 66, 95, 95, 95, 95, 95, 95], [95, 95, 95, 95, 66, 95, 95, 95],
                      [95, 111, 95, 95, 95, 95, 95, 95], [95, 95, 66, 87, 87, 95, 95, 95], [95] * 8,
                      [95, 95, 95, 95, 95, 95, 87, 95], [95, 95, 66, 95, 95, 95, 95, 95]])
        )
    ]
)
def test_str_to_numpy_correct(test_text, size_x, size_y, expected):
    result = str_to_numpy(test_text, size_y, size_x * size_y)

    print(result)
    print(expected)

    assert result.shape == expected.shape
    
    print(result - expected)

    assert np.all(result == expected)


@pytest.mark.parametrize(
    "test_text,size_x,size_y",
    [
        (  # Missing first
            " B B B B B B B _ _ _ _ _ _ _ _ W W W W W W W W",
            4,
            6,
        ),
        (  # Excess last
            "B B B B B B B B _ _ _ _ _ _ _ _ W W W W W W W W W",
            4,
            6,
        ),
        (  # Empty
            "",
            4,
            6,
        ),
        (  # Missing spaces
            "B BB B BB B B _ _ _ _ _ _ _ _ W W W W W W W W",
            4,
            6,
        ),
    ]
)
def test_str_to_numpy_invalid(test_text, size_x, size_y):
    with pytest.raises(InvalidInputException):
        str_to_numpy(test_text, size_y, size_x * size_y)



@pytest.mark.parametrize(
    "size_x,size_y,prev_str,new_str,turn,expected",
    [
        (  # Valid straight
            2, 6,
            "W W W W _ _ _ B B o B B",
            "W W o W W _ _ B B _ B B",
            1,
            True
        ),
        (  # Valid diagonal on empty
            3, 4,
            "_ o _ _ W _ _ B _ _ _ _",
            "_ _ _ B W _ _ o _ _ _ _",
            8,
            True
        ),
        (  # Valid diagonal capture
            3, 4,
            "_ o _ W W _ _ B _ _ _ _",
            "_ _ _ B W _ _ o _ _ _ _",
            8,
            True
        ),
        (  # Valid move on previous move indicator
            4, 4,
            "o _ _ _ B W _ _ _ _ _ _ _ _ _ _",
            "B _ _ _ o W _ _ _ _ _ _ _ _ _ _",
            14,
            True
        ),
        (  # Valid first turn move
            8, 8,
            "W " * 16 + "_ " * 32 + "B " * 16,
            "W " * 16 + "_ " * 24 + "_ _ _ B _ _ _ _ B B B o B B B B " + "B " * 8,
            0,
            True
        ),
        (  # Wrong player
            2, 6,
            "W W W W _ _ _ B B o B B",
            "W W o W W _ _ B B _ B B",
            2,
            False
        ),
        (  # Wrong player
            3, 4,
            "_ o _ W W _ _ B _ _ _ _",
            "_ _ _ B W _ _ o _ _ _ _",
            9,
            False
        ),
        (  # Invalid straight capture
            3, 4,
            "_ o _ _ W _ _ B _ _ _ _",
            "_ _ _ _ B _ _ o _ _ _ _",
            8,
            False
        ),
        (  # Invalid move indicator stayed
            3, 4,
            "_ o _ W W _ _ B _ _ _ _",
            "_ o _ B W _ _ o _ _ _ _",
            8,
            False
        ),
        (  # Invalid no new move indicator
            3, 4,
            "_ o _ W W _ _ B _ _ _ _",
            "_ _ _ B W _ _ _ _ _ _ _",
            8,
            False
        ),
        (  # Invalid move back
            3, 4,
            "_ o _ W W _ _ B _ _ _ _",
            "_ _ _ W W _ _ o _ _ B _",
            8,
            False
        ),
        (  # Invalid pawn multiplication
            3, 4,
            "_ o _ W W _ _ B _ _ _ _",
            "_ _ _ B W _ _ o _ _ B _",
            8,
            False
        ),
        (  # Invalid random char
            2, 6,
            "W W W W _ _ _ B B o B B",
            "W W o W X _ _ B B _ B B",
            1,
            False
        ),
        (  # Invalid all random chars
            2, 6,
            "W W W W _ _ _ B B o B B",
            "a;lksjdflaksdjfal;sdkjf",
            1,
            False
        ),
    ]
)
def test_validate_new_state_simple(size_x, size_y, prev_str, new_str, turn, expected):
    prev_state = str_to_numpy(prev_str, size_y, size_x * size_y)
    new_state = str_to_numpy(new_str, size_y, size_x * size_y)

    if expected:
        assert validate_new_state(prev_state, new_state, turn) is None
    else:
        assert validate_new_state(prev_state, new_state, turn) is not None


@pytest.mark.parametrize(
    "size_x,size_y,state_str,player_idx,expected",
    [
        (  # White win by reaching last row
            4, 4,
            "B _ _ _ o W _ _ _ _ _ _ _ _ _ _",
            0,
            True
        ),
        (  # Black win by reaching last row
            3, 4,
            "_ _ _ B _ _ _ _ o _ _ W",
            1,
            True
        ),
        (  # White win by capturing all black
            3, 4,
            "_ _ _ B _ _ o _ _ _ _ _",
            0,
            True
        ),
        (  # Black win by capturing all white
            3, 4,
            "o _ _ W _ _ _ _ _ _ _ _",
            1,
            True
        ),
        (  # White move, no win
            2, 6,
            "W W W o _ W _ B B _ B B",
            1,
            False
        ),
        (  # Black move, no win
            2, 6,
            "W W W W _ _ _ B B o B B",
            1,
            False
        )
    ]
)
def test_check_win(size_x, size_y, state_str, player_idx, expected):
    state = str_to_numpy(state_str, size_y, size_x * size_y)

    assert check_win(state, player_idx) == expected