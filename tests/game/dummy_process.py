import argparse
import time
import numpy as np

from src.state.state import numpy_to_str, str_to_numpy, create_board
from src.state.constants import FieldType


def dummy_process(
        override_init: str|None = None,
        override_move: str|None = None,
        override_non_final_lines: str|None = None,
        init_wait: float = 0.0,
        move_wait: float = 0.0,
        n_lines_per_move: int = 1,
        input_format: int = 0,
        output_format: int = 1,
    ):
    if init_wait > 0:
        time.sleep(init_wait)

    if override_init is not None:
        print(override_init, flush=True, end="")
    else:
        print(f"{input_format} {output_format}", flush=True)
    
    params = input().strip().split()

    board_x = int(params[0])
    board_y = int(params[1])
    player_id = int(params[2])

    direction = 1 if player_id == 0 else -1
    board_size = board_x * board_y

    ally_pawn = FieldType.FIRST_PLAYER if player_id == 0 else FieldType.SECOND_PLAYER
    enemy_pawn = FieldType.SECOND_PLAYER if player_id == 0 else FieldType.FIRST_PLAYER
    
    first_turn = True

    board = create_board(board_x, board_y)

    while True:
        if move_wait > 0:
            time.sleep(move_wait)

        input_str = input().strip()

        if input_format == 0:
            board = np.copy(str_to_numpy(input_str, board_y, board_size))
        elif input_format == 1 and not (first_turn and player_id == 0):
            move_from_x, move_from_y, move_to_x, move_to_y = map(int, input_str.split())
            board[move_to_x, move_to_y] = board[move_from_x, move_from_y]
            board[move_from_x, move_from_y] = FieldType.EMPTY

        first_turn = False

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

                        if output_format == 0:
                            move_str = numpy_to_str(board)
                        else:
                            move_str = f"{x} {y} {new_x} {new_y}"
    
                        break
                    else:
                        continue
                    break
            else:
                continue
            break
        else:
            raise RuntimeError("No move found, but there should always be one")

        for _ in range(n_lines_per_move - 1):
            if override_non_final_lines is not None:
                print(override_non_final_lines, end="")
            else:
                print(move_str, flush=True)

        if override_move is not None:
            print(override_move, flush=True, end="")
        else:
            print(move_str, flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Dummy process for testing Breakthrough game.")
    parser.add_argument("--override-init", type=str, default=None, help="String to override the init output")
    parser.add_argument("--override-move", type=str, default=None, help="String to override the move output")
    parser.add_argument("--override-non-final-lines", type=str, default=None, help="When printing multiple lines, string to override the non-final ones")
    parser.add_argument("--init-wait", type=float, default=0.0, help="Time to wait before sending init output")
    parser.add_argument("--move-wait", type=float, default=0.0, help="Time to wait before sending move output")
    parser.add_argument("--n-lines-per-move", type=int, default=1, help="Number of lines to output per move")
    parser.add_argument("--input-format", type=int, default=1, help="Input format to use (0 for full board, 1 for move only)")
    parser.add_argument("--output-format", type=int, default=1, help="Output format to use (0 for full board, 1 for move only)")
    args = parser.parse_args()

    dummy_process(
        override_init=args.override_init,
        override_move=args.override_move,
        init_wait=args.init_wait,
        move_wait=args.move_wait,
        n_lines_per_move=args.n_lines_per_move,
        input_format=args.input_format,
        output_format=args.output_format,
    )