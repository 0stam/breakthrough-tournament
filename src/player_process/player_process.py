import os
import subprocess
from typing import IO

from src.game.constants import MoveFormat

class PlayerProcess:
    def __init__(self, process_args: list[str]) -> None:
        self.process_args: list[str] = process_args
        self.input_type: MoveFormat = MoveFormat.FULL_BOARD
        self.output_type: MoveFormat = MoveFormat.FULL_BOARD
        self.t_soft_limit_left: float = 0

    def start_preparing(self) -> None:
        '''
        Runs code that is not written by comeptitors, and shouldn't be counted in time limits.
        The code is started here, but is not guaranteed to finish until join_preparation is called.

        It could be used e.g. to setup Docker and performance limits.
        '''
        pass

    def join_preparation(self, timeout: float) -> None:
        '''
        Waits for preparation code to finish, and kills it if it exceeds the time limit.'''
        pass
    
    def start_process(self) -> None:
        '''
        Starts the process that will be used to play the game. Should be called after preparation is done.
        '''
        self._process: subprocess.Popen = subprocess.Popen(
            self.process_args,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True,
        )

        assert self._process.stdin is not None
        assert self._process.stdout is not None

        self.stdin: IO = self._process.stdin
        self.stdout: IO = self._process.stdout

        os.set_blocking(self.stdout.fileno(), False)
    
    def send_input(self, input_str: str) -> None:
        self.stdin.write(input_str)
        self.stdin.flush()
    
    def request_termination(self) -> None:
        self._process.terminate()
    
    def join(self, timeout: float) -> None:
        try:
            self._process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            self._process.kill()
            self._process.wait()

    def cleanup(self) -> None:
        '''
        Only call this if you don't want to reuse the process for another game.
        Must be called after join()
        '''
        self.stdin.close()
        self.stdout.close()
