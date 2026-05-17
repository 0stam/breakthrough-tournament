import io
import selectors
import sys
import time

from src.game.constants import MoveFormat
from src.game.exceptions import PlayerLostException
from src.game.results.game_results import GameResults
from src.game.results.process_result import ProcessResult
from src.player_process.player_process import PlayerProcess
from src.state.state import apply_move_coordinates, check_win, create_board, numpy_to_beautiful_str, numpy_to_str, state_to_move_coordinates, str_to_move_coordinates, str_to_numpy, validate_new_state
from src.state.exceptions import InvalidInputException


class Game:
    def __init__(
        self,
        board_size_x: int,
        board_size_y: int,
        first_process: PlayerProcess,
        second_process: PlayerProcess,
        t_process_preparation: float,
        t_init: float,
        t_info_parsing: float,
        t_move: float,
        t_move_soft_limit: float
    ):
        self.processes: list[PlayerProcess] = [
            first_process,
            second_process
        ]

        self.t_process_preparation: float = t_process_preparation
        self.t_init: float = t_init
        self.t_info_parsing: float = t_info_parsing
        self.t_move: float = t_move
        self.t_move_soft_limit: float = t_move_soft_limit
        self.board_size_x: int = board_size_x
        self.board_size_y: int = board_size_y
        self.board_size_total: int = board_size_x * board_size_y

        self.selector: selectors.DefaultSelector = selectors.DefaultSelector()

        self.turn: int = 0
        self.board: np.ndarray = None  # type: ignore
        self.last_move_coordinates: tuple[tuple[int, int], tuple[int, int]] = None  # type: ignore
    
    def run(self) -> GameResults:
        board = create_board(self.board_size_x, self.board_size_y)
        self.board = board

        for process in self.processes:
            process.t_soft_limit_left = self.t_move_soft_limit

        try:
            for process in self.processes:
                process.start_preparing()
            
            for process in self.processes:
                process.join_preparation(timeout=self.t_process_preparation)

            for process in self.processes:
                process.start_process()

            self.selector.register(self.processes[0].stdout, selectors.EVENT_READ, data=0)
            self.selector.register(self.processes[1].stdout, selectors.EVENT_READ, data=1)

            self._read_preferred_format()

            print(f"First player prefers {self.processes[0].input_type} {self.processes[0].output_type} format", file=sys.stderr)
            print(f"Second player prefers {self.processes[1].input_type} {self.processes[1].output_type} format", file=sys.stderr)

            # board_size_x board_size_y player_id (0 - white, 1 - black)
            self.processes[0].send_input(f"{self.board_size_x} {self.board_size_y} 0\n")
            self.processes[1].send_input(f"{self.board_size_x} {self.board_size_y} 1\n")

            time.sleep(self.t_info_parsing)

            while True:
                current_player_idx = self.turn % 2
                self._perform_move()

                # Print board state

                print(numpy_to_beautiful_str(self.board), end="\n\n", file=sys.stderr)

                if check_win(self.board, current_player_idx):
                    self.processes[0].request_termination()
                    self.processes[1].request_termination()

                    self.processes[0].join(timeout=10.0)
                    self.processes[1].join(timeout=5.0)

                    return GameResults(
                        first_lost=current_player_idx != 0,
                        second_lost=current_player_idx != 1,
                        first_error_message=None,
                        second_error_message=None
                    )
                
                self.turn += 1
        except PlayerLostException as e:
            return GameResults(
                first_lost=e.first,
                second_lost=e.second,
                first_error_message=e.first_error_message,
                second_error_message=e.second_error_message
            )

    def _read_preferred_format(self) -> None:
        result = self._collect_first_line_from_both(timeout=self.t_init)

        print(f"Preferred formats: {result.output}", file=sys.stderr)

        input_formats: list[int] = [-1, -1]
        output_formats: list[int] = [-1, -1]

        for i in range(2):
            try:
                in_str, out_str = result.output[i].strip().split()
                input_formats[i] = int(in_str)
                output_formats[i] = int(out_str)
            except ValueError:
                pass

            result.lost[i] |= input_formats[i] not in MoveFormat.__members__.values()
            result.lost[i] |= output_formats[i] not in MoveFormat.__members__.values()

            result.err_msg[i] = f"Invalid input format: {result.output[i]}" if result.lost[i] else None

        self._check_if_lost(result)

        for i in range(2):
            self.processes[i].input_type = MoveFormat(input_formats[i])
            self.processes[i].output_type = MoveFormat(output_formats[i])

    def _perform_move(self) -> None:
        player_idx = self.turn % 2

        self.selector.unregister(self.processes[1 - player_idx].stdout)

        if self.processes[player_idx].stdout not in self.selector.get_map():
            self.selector.register(self.processes[player_idx].stdout, selectors.EVENT_READ, data=player_idx)
        
        if self.processes[player_idx].input_type == MoveFormat.FULL_BOARD or self.turn < 1:
            input_str = f"{numpy_to_str(self.board)}\n"
        elif self.processes[player_idx].input_type == MoveFormat.MOVE_ONLY:
            input_str = f"{self.get_formatted_last_move_coordinates()}\n"
        else:
            raise ValueError(f"Unknown input type: {self.processes[player_idx].input_type}")

        self.processes[player_idx].send_input(input_str)

        result = self._collect_last_line_from_single_player(
            player_idx=player_idx,
            timeout=self.t_move,
            final_timeout=self.processes[player_idx].t_soft_limit_left
        )

        print(result, file=sys.stderr)

        try:
            if self.processes[player_idx].output_type == MoveFormat.FULL_BOARD:
                new_state = str_to_numpy(result.output[player_idx], self.board_size_y, self.board_size_total)
            elif self.processes[player_idx].output_type == MoveFormat.MOVE_ONLY:
                new_state = self.board.copy()
                move_from, move_to = str_to_move_coordinates(result.output[player_idx])
                apply_move_coordinates(new_state, move_from, move_to)
            else:
                raise ValueError(f"Unknown output type: {self.processes[player_idx].output_type}")


            validation_result = validate_new_state(self.board, new_state, self.turn)

            if validation_result is not None:
                result.lost[player_idx] = True
                result.err_msg[player_idx] = validation_result
        except InvalidInputException as e:
            result.lost[player_idx] = True
            result.err_msg[player_idx] = str(e)
        

        self._check_if_lost(result)

        self.last_move_coordinates = state_to_move_coordinates(self.board, new_state)
        self.board = new_state
    
    def _check_if_lost(self, result: ProcessResult) -> None:
        if any(result.lost):
            raise PlayerLostException(result.lost[0], result.lost[1], result.err_msg[0], result.err_msg[1])

    def _collect_first_line_from_both(self, timeout: float) -> ProcessResult:
        deadline = time.time() + timeout

        last_lines = {0: "", 1: ""}
        unfinished_lines = {0: "", 1: ""}

        while True:
            time_left = deadline - time.time()

            if time_left <= 0:
                break

            events = self.selector.select(timeout=time_left)

            for key, _ in events:
                pipe = key.fileobj
                player_idx = key.data

                assert isinstance(pipe, io.TextIOWrapper)

                in_data = pipe.read(65536)  # Flush the entire pipe

                if last_lines[player_idx] != "":
                    continue  # We already have a line from this player

                endline_idx = in_data.find("\n")

                if endline_idx == -1:
                    unfinished_lines[player_idx] += in_data
                    continue

                last_lines[player_idx] = unfinished_lines[player_idx] + in_data[:endline_idx]

            if all(line != "" for line in last_lines.values()):
                break
        
        error_msg = "Timeout when waiting for players' line"

        error_msgs = [error_msg if last_lines[i] == "" else None for i in range(2)]

        return ProcessResult(
            lost=[last_lines[0] == "", last_lines[1] == ""],
            output=[last_lines[0], last_lines[1]],
            err_msg=error_msgs
        )
    
    def _collect_last_line_from_single_player(self, player_idx: int, timeout: float, final_timeout: float|None) -> ProcessResult:
        '''
        Collects the last complete line from the specified player's output within the given timeout.
        If the player does not produce a complete line within the timeout, it is considered lost.

        If the process doesn't output a complete line within the initial timeout, but does output
        a complete line within the final timeout, the time after initial timeout is subtracted from
        the player's soft time limit.

        This function assumes that only a single stdout is currently registered in the selector
        '''
        assert len(self.selector.get_map()) == 1, "Only one player's output should be registered in the selector"

        deadline = time.time() + timeout
        final_deadline = deadline + (final_timeout if final_timeout else 0)

        last_line = ""
        unfinished_line = ""

        exceeded_initial_timeout = False

        while True:
            curr_time = time.time()

            if deadline - curr_time > 0:
                time_left = deadline - curr_time
            elif final_deadline - curr_time > 0 and not last_line:
                time_left = final_deadline - curr_time
                exceeded_initial_timeout = True
            else:
                break

            events = self.selector.select(timeout=time_left)

            for key, _ in events:
                pipe = key.fileobj

                assert isinstance(pipe, io.TextIOWrapper)

                in_data = pipe.read(65536)  # Flush the entire pipe

                if in_data.endswith("\n"):  # The last line is complete (should happen most of the time)
                    prev_newline_idx = in_data[:-1].rfind("\n")

                    if prev_newline_idx == -1:  # There is only one line, we take it
                        last_line = unfinished_line + in_data[:-1]
                        unfinished_line = ""
                    else:  # There are multiple lines, we take the last one
                        last_line = in_data[prev_newline_idx + 1:-1]
                        unfinished_line = ""
                else:  # The last line is not complete
                    endline_idx = in_data.rfind("\n")

                    if endline_idx == -1:  # There are no previous complete lines
                        unfinished_line += in_data
                    else:  # There is at least one complete line
                        prev_newline_idx = in_data[:endline_idx].rfind("\n")
                        
                        if prev_newline_idx == -1:  # There is only one complete line, we take it
                            last_line = unfinished_line + in_data[:endline_idx]
                        else:  # There are multiple complete lines, we take the last one
                            last_line = in_data[prev_newline_idx + 1:endline_idx]

                        unfinished_line = in_data[endline_idx + 1:]
        
        if exceeded_initial_timeout:
            self.processes[player_idx].t_soft_limit_left -= curr_time - deadline

        lost = [False, False]
        last_lines = ["", ""]
        error_msgs: list[str|None] = [None, None]

        last_lines[player_idx] = last_line

        if last_line == "":
            lost[player_idx] = True
            error_msgs[player_idx] = "Timeout when waiting for player's line"

        return ProcessResult(
            lost=lost,
            output=last_lines,
            err_msg=error_msgs
        )
    
    def get_formatted_last_move_coordinates(self) -> str:
        move_from, move_to = self.last_move_coordinates

        return f"{move_from[0]} {move_from[1]} {move_to[0]} {move_to[1]}"
