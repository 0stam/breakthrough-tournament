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
        raise InvalidInputException("Invalid input size")
    
    result = np.frombuffer(s_processed, dtype="int32").reshape((size_y, -1)).T[:, ::-1]

    return result


def numpy_to_str(arr: np.ndarray) -> str:
    assert arr.ndim == 2
    assert arr.shape[0] > 0
    assert arr.shape[1] > 0

    return " ".join(map(lambda sub_arr: " ".join(map(chr, sub_arr)), arr[:, ::-1].T))


def validate_new_state(prev_state: np.ndarray, new_state: np.ndarray, turn: int) -> bool:
    '''
    Assuming that prev_state contains a valid board state, checks if new_state is valid.
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
                return False

            new_indicator_x = x
            new_indicator_y = y

        if prev_state[x, y] == FieldType.MOVE_INDICATOR:
            if prev_indicator_x != -1:
                return False

            prev_indicator_x = x
            prev_indicator_y = y
        
        if new_state[x, y] == curr_player_pawn_code:
            if new_pawn_x != -1:
                return False

            new_pawn_x = x
            new_pawn_y = y

    # --- Checks for turn == 0 ---
    if turn == 0:
        if len(changed_xs) != 2:
            return False  # More than two fields changed on the first turn

        return validate_single_pawn_movement(
            prev_state, new_indicator_x, new_indicator_y, new_pawn_x, new_pawn_y, curr_player_pawn_code
        )
    
    # --- Checks for turn > 0 ---

    # Check if previous move indicator disappeared
    if prev_indicator_x == -1:
        return False  # There was no change at prev indicator position
    
    if len(changed_xs) == 2:
        # Make sure a pawn has moved on an old move indicator
        if prev_indicator_x != new_pawn_x or prev_indicator_y != new_pawn_y:
            return False
    
    if len(changed_xs) > 3:
        return False  # More than 3 field changed (old indicator, old pawn position, new pawn position, and ???)
    
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
) -> bool:
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
        return False  # Move indicator not found in the new state
    
    if new_pawn_x == -1:
        return False # New pawn not found in the new state
    
    # Check if move was performed by a correct player
    if prev_state[new_indicator_x, new_indicator_y] != curr_player_pawn_code:
        return False  # Wrong player moved (or move from empty field)
    
    # Check if move in right direction
    if new_pawn_y - new_indicator_y != direction:
        return False  
    
    # Check for correct straight move
    if new_pawn_x == new_indicator_x:
        if prev_state[new_pawn_x, new_pawn_y] not in {FieldType.EMPTY, FieldType.MOVE_INDICATOR}:
            return False  # Moved on an occupied field
        return True
    
    # Check for correct diagonal move
    if abs(new_pawn_x - new_indicator_x) > 1:
        return False  # Move out of range
    
    if prev_state[new_pawn_x, new_pawn_y] not in {FieldType.EMPTY, FieldType.MOVE_INDICATOR, enemy_pawn_code}:
        return False  # Moved on their own pawn
    
    return True


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
