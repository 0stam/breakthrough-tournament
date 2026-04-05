import numpy as np

from src.state.state import numpy_to_str, str_to_numpy
from src.state.constants import FieldType


def dummy_process():
    print("0", flush=True)

    params = input().strip().split()

    board_x = int(params[0])
    board_y = int(params[1])
    player_id = int(params[2])

    direction = 1 if player_id == 0 else -1
    board_size = board_x * board_y

    ally_pawn = FieldType.FIRST_PLAYER if player_id == 0 else FieldType.SECOND_PLAYER
    enemy_pawn = FieldType.SECOND_PLAYER if player_id == 0 else FieldType.FIRST_PLAYER

    while True:
        board_str = input().strip()
        board = np.copy(str_to_numpy(board_str, board_x, board_size))

        # --- Dummy move: move the first pawn in the direction of the opponent ---
        board[board == FieldType.MOVE_INDICATOR] = FieldType.EMPTY  # Clear move indicators from previous turn

        for x in range(board_x):
            for y in range(board_y):
                if board[x, y] == ally_pawn:
                    for x_offset in range(-1, 2):
                        new_x = x + x_offset
                        new_y = y + direction

                        if not (0 <= new_x < board_x and 0 <= new_y < board_y):
                            continue

                        if board[new_x, new_y] == ally_pawn:
                            continue

                        if board[new_x, new_y] == enemy_pawn and x_offset == 0:
                            continue

                        board[new_x, new_y] = ally_pawn
                        board[x, y] = FieldType.MOVE_INDICATOR

                        break
                    else:
                        continue
                    break
            else:
                continue
            break

        print(numpy_to_str(board), flush=True)


if __name__ == "__main__":
    dummy_process()