import io
import selectors
import sys
import time

from src.game.constants import InputType
from src.game.exceptions import PlayerLostException
from src.game.results.game_results import GameResults
from src.game.results.process_result import ProcessResult
from src.game.player_process import PlayerProcess
from src.state.state import create_board


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
        self.first_args = first_args
        self.second_args = second_args
        self.t_init = t_init
        self.t_info_parsing = t_info_parsing
        self.t_move = t_move
        self.board_size_x = board_size_x
        self.board_size_y = board_size_y
        self.selector = selectors.DefaultSelector()
    
    def run(self) -> GameResults:
        board = create_board(self.board_size_x, self.board_size_y)
        
        self.first_process = PlayerProcess(self.first_args)
        self.second_process = PlayerProcess(self.second_args)

        try:
            self.first_process.start_process()
            self.second_process.start_process()

            self.selector.register(self.first_process.stdout, selectors.EVENT_READ, data=0)
            self.selector.register(self.second_process.stdout, selectors.EVENT_READ, data=1)

            self._read_preferred_format()

            print(f"First player prefers {self.first_process.input_type} format", file=sys.stderr)
            print(f"Second player prefers {self.second_process.input_type} format", file=sys.stderr)

            # board_size_x board_size_y player_id (0 - white, 1 - black)
            self.first_process.send_input(f"{self.board_size_x} {self.board_size_y} 0\n")
            self.second_process.send_input(f"{self.board_size_x} {self.board_size_y} 1\n")

            self.first_process.request_termination()
            self.second_process.request_termination()

            self.first_process.join(timeout=10.0)
            self.second_process.join(timeout=5.0)

            return GameResults(first_lost=False, second_lost=False)  # TODO: implement the actual game loop
        except PlayerLostException as e:
            return GameResults(e.first, e.second)
    
    def _read_preferred_format(self) -> None:
        result = self._collect_first_line_from_both(timeout=self.t_init)

        first_format = -1
        second_format = -1

        try:
            first_format = int(result.first_output)
        except ValueError:
            pass

        try:
            second_format = int(result.second_output)
        except ValueError:
            pass

        result.first_lost |= first_format not in InputType.__members__.values()
        result.second_lost |= second_format not in InputType.__members__.values()

        self._check_if_lost(result)

        self.first_process.input_type = InputType(first_format)
        self.second_process.input_type = InputType(second_format)
    
    def _check_if_lost(self, result: ProcessResult) -> None:
        if result.first_lost or result.second_lost:
            raise PlayerLostException(result.first_lost, result.second_lost)
    
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
            first_lost=last_lines[0] == "",
            second_lost=last_lines[1] == "",
            first_output=last_lines[0],
            second_output=last_lines[1]
        )

                
        
        
