import io
import selectors
import sys
import time

from src.game.constants import InputType
from src.game.exceptions import PlayerLostException
from src.game.results.game_results import GameResults
from src.game.results.process_result import ProcessResult
from src.game.player_process import PlayerProcess
from src.state.state import check_win, create_board, numpy_to_str, str_to_numpy, validate_new_state


class Game:
    def __init__(
        self,
        board_size_x: int,
        board_size_y: int,
        first_args: list[str],
        second_args: list[str],
        t_init: float,
        t_info_parsing: float,
        t_move: float
    ):
        self.first_args: list[str] = first_args
        self.second_args: list[str] = second_args
        self.t_init: float = t_init
        self.t_info_parsing: float = t_info_parsing
        self.t_move: float = t_move
        self.board_size_x: int = board_size_x
        self.board_size_y: int = board_size_y
        self.board_size_total: int = board_size_x * board_size_y

        self.selector: selectors.DefaultSelector = selectors.DefaultSelector()

        self.turn: int = 0
        self.board: np.ndarray = None  # type: ignore
    
    def run(self) -> GameResults:
        board = create_board(self.board_size_x, self.board_size_y)
        self.board = board

        self.processes: list[PlayerProcess] = []
        self.processes.append(PlayerProcess(self.first_args))
        self.processes.append(PlayerProcess(self.second_args))

        try:
            self.processes[0].start_process()
            self.processes[1].start_process()

            self.selector.register(self.processes[0].stdout, selectors.EVENT_READ, data=0)
            self.selector.register(self.processes[1].stdout, selectors.EVENT_READ, data=1)

            self._read_preferred_format()

            print(f"First player prefers {self.processes[0].input_type} format", file=sys.stderr)
            print(f"Second player prefers {self.processes[1].input_type} format", file=sys.stderr)

            # board_size_x board_size_y player_id (0 - white, 1 - black)
            self.processes[0].send_input(f"{self.board_size_x} {self.board_size_y} 0\n")
            self.processes[1].send_input(f"{self.board_size_x} {self.board_size_y} 1\n")

            time.sleep(self.t_info_parsing)

            while True:
                current_player_idx = self.turn % 2
                self._perform_move()

                if check_win(self.board, current_player_idx):
                    self.processes[0].request_termination()
                    self.processes[1].request_termination()

                    self.processes[0].join(timeout=10.0)
                    self.processes[1].join(timeout=5.0)

                    return GameResults(
                        first_lost=current_player_idx != 0,
                        second_lost=current_player_idx != 1
                    )
                
                self.turn += 1
        except PlayerLostException as e:
            return GameResults(e.first, e.second)
    
    def _read_preferred_format(self) -> None:
        result = self._collect_first_line_from_both(timeout=self.t_init)

        formats: list[int] = [0, 0]

        for i in range(2):
            format = -1
            try:
                formats[i] = int(result.output[i])
            except ValueError:
                pass

            result.lost[i] |= formats[i] not in InputType.__members__.values()

        self._check_if_lost(result)

        for i in range(2):
            self.processes[i].input_type = InputType(formats[i])

    def _perform_move(self) -> None:
        player_idx = self.turn % 2

        self.selector.unregister(self.processes[1 - player_idx].stdout)

        if self.processes[player_idx].stdout not in self.selector.get_map():
            self.selector.register(self.processes[player_idx].stdout, selectors.EVENT_READ, data=player_idx)
        
        self.processes[player_idx].send_input(f"{numpy_to_str(self.board)}\n")

        result = self._collect_last_line_from_single_player(player_idx=player_idx, timeout=self.t_move)

        try:
            new_state = str_to_numpy(result.output[player_idx], self.board_size_x, self.board_size_total)
        except ValueError:
            result.lost[player_idx] = True

        result.lost[player_idx] |= not validate_new_state(self.board, new_state, self.turn)

        self._check_if_lost(result)

        self.board = new_state

    
    def _check_if_lost(self, result: ProcessResult) -> None:
        if any(result.lost):
            raise PlayerLostException(result.lost[0], result.lost[1])

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
        
        return ProcessResult(
            lost=[last_lines[0] == "", last_lines[1] == ""],
            output=[last_lines[0], last_lines[1]]
        )
    
    def _collect_last_line_from_single_player(self, player_idx: int, timeout: float) -> ProcessResult:
        '''
        Collects the last complete line from the specified player's output within the given timeout.
        If the player does not produce a complete line within the timeout, it is considered lost.

        This function assumes that only a single stdout is currently registered in the selector
        '''
        assert len(self.selector.get_map()) == 1, "Only one player's output should be registered in the selector"

        deadline = time.time() + timeout

        last_line = ""
        unfinished_line = ""

        while True:
            time_left = deadline - time.time()

            if time_left <= 0:
                break

            events = self.selector.select(timeout=time_left)

            for key, _ in events:
                pipe = key.fileobj

                assert isinstance(pipe, io.TextIOWrapper)

                in_data = pipe.read(65536)  # Flush the entire pipe

                if in_data.endswith("\n"):  # The last line is complete (should happen most of the time)
                    last_line = unfinished_line + in_data[:-1]
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
                
        return ProcessResult(
            lost=[player_idx == 0 and last_line == "", player_idx == 1 and last_line == ""],
            output=[last_line if player_idx == 0 else "", last_line if player_idx == 1 else ""]
        )
