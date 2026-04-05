import os
import subprocess
import multiprocessing
from typing import IO

from src.game.constants import InputType

class PlayerProcess:
    def __init__(self, process_args: list[str]) -> None:
        self.process_args: list[str] = process_args
        self.input_type: InputType = InputType.FULL_BOARD
    
    def start_process(self):
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
    
    def send_input(self, input_str: str):
        self.stdin.write(input_str)
        self.stdin.flush()
    
    def request_termination(self):
        self._process.terminate()
    
    def join(self, timeout: float):
        try:
            self._process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            self._process.kill()
            self._process.wait()
