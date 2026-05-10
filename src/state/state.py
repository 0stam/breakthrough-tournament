import numpy as np

from src.state.exceptions import InvalidInputException
from src.state.constants import FieldType


def create_board(size_x: int, size_y: int) -> np.ndarray:
    '''
    Creates a board of given size with pawns in their initial positions.
    '''
    assert size_y >= 4, "Board size y must be at least 4"

    board = np.full((size_x, size_y), FieldType.EMPTY, dtype="int32")

    board[:, :2] = FieldType.FIRST_PLAYER
    board[:, -2:] = FieldType.SECOND_PLAYER

    return board


def str_to_numpy(s: str, size_y: int, size_total: int) -> np.ndarray:
    s_processed = s.strip()[::2].encode("utf-32-le")  # Makes sure each char contains four bytes of little-endian data
    
    if len(s_processed) != size_total * 4:
        raise InvalidInputException(f"Invalid input size: {len(s_processed) // 4} fields found, but expected {size_total}, input string: {s}")
    
    result = np.frombuffer(s_processed, dtype="int32").reshape((size_y, -1)).T[:, ::-1]

    return result


def numpy_to_beautiful_str(board: np.ndarray) -> str:
    '''
    Prints the board in a more human-readable format, with rows reversed and columns separated by spaces.
    '''
    return "\n".join(map(lambda sub_arr: " ".join(map(chr, sub_arr)), board[:, ::-1].T))


def str_to_move_coordinates(s: str) -> tuple[tuple[int, int], tuple[int, int]]:
    parts = s.strip().split()

    if len(parts) != 4:
        raise InvalidInputException(f"Expected four values separated by space, got: {s}")
    
    try:
        x1 = int(parts[0])
        y1 = int(parts[1])
        x2 = int(parts[2])
        y2 = int(parts[3])
    except ValueError:
        raise InvalidInputException(f"Can't parse values to integers: {s}")
    
    return (x1, y1), (x2, y2)


def numpy_to_str(arr: np.ndarray) -> str:
    assert arr.ndim == 2
    assert arr.shape[0] > 0
    assert arr.shape[1] > 0

    return " ".join(map(lambda sub_arr: " ".join(map(chr, sub_arr)), arr[:, ::-1].T))


def apply_move_coordinates(prev_state: np.ndarray, move_from: tuple[int, int], move_to: tuple[int, int]) -> None:
    '''
    Modifies the state in place by moving whatever is at move_from to move_to.
    
    Assumes that the prev_state is correct.

    Note: while this function does some basic validation, it is not tested and is only meant
    to provide more verbose errors when using the move coordinates format

    The only errors guaranteed to be caught are out of bound errors
    '''

    for i in range(2):
        if not (0 <= move_from[i] < prev_state.shape[i]):
            raise InvalidInputException(f"Move from coordinates out of bounds: {move_from}, board shape: {prev_state.shape}")
        
        if not (0 <= move_to[i] < prev_state.shape[i]):
            raise InvalidInputException(f"Move to coordinates out of bounds: {move_to}, board shape: {prev_state.shape}")
    
    if prev_state[move_from] in (FieldType.EMPTY, FieldType.MOVE_INDICATOR):
        raise InvalidInputException(f"Invalid move: Move from empty field: {move_from}")
    
    direction = move_to[1] - move_from[1]

    if direction not in (-1, 1):
        raise InvalidInputException(f"Invalid move: y direction is not 1 or -1: {direction}")

    if prev_state[move_from] == FieldType.FIRST_PLAYER and direction != 1:
        raise InvalidInputException(f"Invalid move: First player can only move in positive y direction, but tried to move from {move_from} to {move_to}")
    
    if prev_state[move_from] == FieldType.SECOND_PLAYER and direction != -1:
        raise InvalidInputException(f"Invalid move: Second player can only move in negative y direction, but tried to move from {move_from} to {move_to}")
    
    # Clear old move indicator
    prev_state[prev_state == FieldType.MOVE_INDICATOR] = FieldType.EMPTY

    # Move whatever is at the selected location
    moved_pawn = prev_state[move_from]
    prev_state[move_from] = FieldType.MOVE_INDICATOR
    prev_state[move_to] = moved_pawn


def state_to_move_coordinates(prev_state: np.ndarray, new_state: np.ndarray) -> tuple[tuple[int, int], tuple[int, int]]:
    '''
    Returns the move coordinates (move_from, move_to) of the last move.

    Assumes the state is correct and at least one move was performed.
    '''
    move_from = np.argwhere(new_state == FieldType.MOVE_INDICATOR)[0]
    move_to = np.argwhere((new_state != prev_state) & (new_state != FieldType.MOVE_INDICATOR) & (new_state != FieldType.EMPTY))[0]

    return tuple(move_from), tuple(move_to)


def validate_new_state(prev_state: np.ndarray, new_state: np.ndarray, turn: int) -> None|str:
    '''
    Assuming that prev_state contains a valid board state, checks if new_state is valid.

    Returns None if the state is valid, otherwise returns a string with an error message.
    '''
    assert prev_state.shape == new_state.shape

    diff = new_state - prev_state

    changed_xs, changed_ys = np.nonzero(diff)

    curr_player_pawn_code = FieldType.FIRST_PLAYER if turn % 2 == 0 else FieldType.SECOND_PLAYER

    prev_indicator_x: int = -1
    prev_indicator_y: int = -1
    new_indicator_x: int = -1
    new_indicator_y: int = -1
    new_pawn_x: int = -1
    new_pawn_y: int = -1

    for x, y in zip(changed_xs, changed_ys):
        x = int(x)
        y = int(y)

        if new_state[x, y] == FieldType.MOVE_INDICATOR:
            if new_indicator_x != -1:
                return "Multiple move indicators found in new state"

            new_indicator_x = x
            new_indicator_y = y

        if prev_state[x, y] == FieldType.MOVE_INDICATOR:
            if prev_indicator_x != -1:
                return "Multiple move indicators found in previous state"

            prev_indicator_x = x
            prev_indicator_y = y
        
        if new_state[x, y] == curr_player_pawn_code:
            if new_pawn_x != -1:
                return "Multiple pawns changed position in new state"

            new_pawn_x = x
            new_pawn_y = y

    # --- Checks for turn == 0 ---
    if turn == 0:
        if len(changed_xs) != 2:
            return "More than two fields changed on the first turn"

        return validate_single_pawn_movement(
            prev_state, new_indicator_x, new_indicator_y, new_pawn_x, new_pawn_y, curr_player_pawn_code
        )
    
    # --- Checks for turn > 0 ---

    # Check if previous move indicator disappeared
    if prev_indicator_x == -1:
        return "There was no change at prev indicator position"
    
    if len(changed_xs) == 2:
        # Make sure a pawn has moved on an old move indicator
        if prev_indicator_x != new_pawn_x or prev_indicator_y != new_pawn_y:
            return "Only two fields changed, which usually means that a pawn moved on an old move indicator, but it didn't"
    
    if len(changed_xs) > 3:
        return "More than 3 field changed (old indicator, old pawn position, new pawn position, and ???)"
    
    return validate_single_pawn_movement(
        prev_state, new_indicator_x, new_indicator_y, new_pawn_x, new_pawn_y, curr_player_pawn_code
    )


def validate_single_pawn_movement(
    prev_state: np.ndarray,
    new_indicator_x: int,
    new_indicator_y: int,
    new_pawn_x: int,
    new_pawn_y: int,
    curr_player_pawn_code: FieldType
) -> None|str:
    assert curr_player_pawn_code in {FieldType.FIRST_PLAYER, FieldType.SECOND_PLAYER}

    if curr_player_pawn_code == FieldType.FIRST_PLAYER:
        direction = 1
    else:
        direction = -1
    
    if curr_player_pawn_code == FieldType.FIRST_PLAYER:
        enemy_pawn_code = FieldType.SECOND_PLAYER
    else:
        enemy_pawn_code = FieldType.FIRST_PLAYER

    if new_indicator_x == -1:
        return "Move indicator not found in the new state"
    
    if new_pawn_x == -1:
        return "New pawn not found in the new state"
    
    # Check if move was performed by a correct player
    if prev_state[new_indicator_x, new_indicator_y] != curr_player_pawn_code:
        return "Wrong player moved (or move from empty field)"
    
    # Check if move is in range
    if abs(new_pawn_x - new_indicator_x) > 1:
        return "Move out of range"
    
    if abs(new_pawn_y - new_indicator_y) > 1:
        return "Move out of range"

    # Check if move in right direction
    if new_pawn_y - new_indicator_y != direction:
        return "Move in wrong direction"
    
    # Check for correct straight move
    if new_pawn_x == new_indicator_x:
        if prev_state[new_pawn_x, new_pawn_y] not in {FieldType.EMPTY, FieldType.MOVE_INDICATOR}:
            return "Moved on an occupied field"
        return None
    
    if prev_state[new_pawn_x, new_pawn_y] not in {FieldType.EMPTY, FieldType.MOVE_INDICATOR, enemy_pawn_code}:
        return "Moved on their own pawn"
    
    return None


def check_win(state: np.ndarray, player_idx: int) -> bool:
    '''
    For a given state and a player that performs the last move, check if that player won.

    The function only checks for the victory of this player and assumes that the game was not won before.
    '''
    if player_idx == 0:
        if np.any(state[:, -1] == FieldType.FIRST_PLAYER):
            return True
        
        return bool(np.all(state != FieldType.SECOND_PLAYER))
    
    if np.any(state[:, 0] == FieldType.SECOND_PLAYER):
        return True

    return bool(np.all(state != FieldType.FIRST_PLAYER))
