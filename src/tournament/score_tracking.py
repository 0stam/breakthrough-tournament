
import enum
from dataclasses import dataclass, field
from random import random
from typing import List, List, Optional, Optional, Set

from src.game.results.game_results import GameResults

class MatchResult(enum.IntEnum):
    UNDEFINED = 0
    FIRST_PLAYER_WINS = 1
    SECOND_PLAYER_WINS = 2
    DRAW = 3

    def __bool__(self):
        return self != MatchResult.UNDEFINED

@dataclass
class Player:
    name: str
    score: int = 0
    side_balance: int = 0

@dataclass
class Match:
    first_player: Player #first player goes first in the match
    second_player: Player
    result: MatchResult = MatchResult.UNDEFINED
    move_history: Optional[list] = None
    
    first_p_start_score: int = field(init=False)
    second_p_start_score: int = field(init=False)

    def __post_init__(self):
        self.first_p_start_score = self.first_player.score
        self.second_p_start_score = self.second_player.score

    def finish_match(self, results: GameResults, move_history: Optional[list] = None) -> None:

        match (results.first_lost, results.second_lost):
                case (False, True):
                    self.result = MatchResult.FIRST_PLAYER_WINS
                    self.first_player.score += 1
                case (True, False):
                    self.result = MatchResult.SECOND_PLAYER_WINS
                    self.second_player.score += 1
                case (True, True):
                    self.result = MatchResult.DRAW
                # case _:
                #     raise RuntimeError("Invalid game result")
        
        self.move_history = move_history


@dataclass
class ScoreTracker:
    players: List[Player] = field(default_factory=list)
    prev_rounds: List[List[Match]] = field(default_factory=list)
    curr_round_matches: List[Match] = field(default_factory=list)

    def register_match_result(self, first_player: Player, second_player: Player, first_player_points: int, second_player_points: int, move_history: Optional[list] = None) -> None:
        
        first_player.side_balance += 1
        second_player.side_balance -= 1
        first_player.score += first_player_points
        second_player.score += second_player_points
        game_match = Match(first_player=first_player, second_player=second_player)

        match (first_player_points, second_player_points):
                case (0, 1):
                    game_match.result = MatchResult.FIRST_PLAYER_WINS
                case (1, 0):
                    game_match.result = MatchResult.SECOND_PLAYER_WINS
                case (1, 1):
                    game_match.result = MatchResult.DRAW
                # case _:
                #     raise RuntimeError("Invalid game result")
        
        game_match.move_history = move_history
        self.curr_round_matches.append(game_match)
    
    def end_round(self) -> None:
        self.prev_rounds.append(self.curr_round_matches)
        self.curr_round_matches = []

    def get_player(self, name: str) -> Optional[Player]:
        for player in self.players:
            if player.name == name:
                return player
        raise ValueError(f"Player with name {name} not found in score tracker")

    def print_history(self) -> None:
        for i, round in enumerate(self.prev_rounds):
            print(f"Round {i+1}:")
            for match in round:
                print(f"{match.first_player.name} (Score: {match.first_p_start_score}) vs {match.second_player.name} (Score: {match.second_p_start_score}) - Result: {match.result.name}")
        
        print("Final Scores:")
        for player in sorted(self.players, key=lambda p: p.score, reverse=True):
            print(f"{player.name}: {player.score}")

    @staticmethod
    def determine_first_player(p1: Player, p2: Player) -> tuple[Player, Player]:
        if p1.side_balance > p2.side_balance:
            return p1, p2
        elif p1.side_balance < p2.side_balance:
            return p2, p1
        else:
            return (p1, p2) if random() < 0.5 else (p2, p1)
