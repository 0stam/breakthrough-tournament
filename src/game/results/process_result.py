from dataclasses import dataclass
from typing import NamedTuple


@dataclass
class ProcessResult:
    lost: list[bool]
    output: list[str]
    err_msg: list[str|None]

    def __str__(self) -> str:
        output = []

        for i in range(len(self.lost)):
            player_output = []

            if self.lost[i]:
                player_output.append(f"Player {i} lost")
            
            if self.err_msg[i] is not None:
                player_output.append(f"Error message: {self.err_msg[i]}")
            
            if self.output[i] is not None:
                if self.output[i] != "":
                    player_output.append(f"Output: {self.output[i]}")
                elif self.lost[i]:
                    player_output.append("Output: <empty>")
            
            if player_output:
                output.append(f"Player {i} move capture:")
                output.extend(player_output)
                output.append("")  # Empty line between players
        
        return "\n".join(output)
