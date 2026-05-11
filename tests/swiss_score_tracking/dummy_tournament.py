import sys
import src.swiss.pairing_strategies.min_cost
from pathlib import Path
from src.swiss.match_log import MatchLog
from src.tournament.score_tracking import Player, ScoreTracker
from src.game.results.game_results import GameResults

# CPU_LIMIT = "3"
# MEMORY_LIMIT = "8g"

def run_dummy_game(first_player_name, second_player_name):
    if first_player_name < second_player_name:
        return GameResults(first_lost=False, second_lost=True, first_error_message=None, second_error_message=None)
    elif first_player_name > second_player_name:
        return GameResults(first_lost=True, second_lost=False, first_error_message=None, second_error_message=None)
    return GameResults(first_lost=True, second_lost=True, first_error_message=None, second_error_message=None)


class DummyTournament:
    def __init__(self,num_of_rounds):
        self.num_of_rounds = num_of_rounds
        self.match_log = MatchLog()
        self.score_tracker = ScoreTracker()
    
    def load_players(self):
        players_file = Path(__file__).parent / "test_players.txt"
        with open(players_file, "r") as f:
            for line in f:
                self.match_log.add_player(line.strip())
                self.score_tracker.players.append(Player(name=line.strip()))

    def run_match(self, pairing):

        player_a = self.score_tracker.get_player(pairing.player_a)
        player_b = self.score_tracker.get_player(pairing.player_b)

        first_player, second_player = ScoreTracker.determine_first_player(player_a, player_b)

        results = run_dummy_game(first_player.name, second_player.name)

        match (results.first_lost, results.second_lost):
            case (False, True):
                first_player_points = 1
                second_player_points = 0
            case (True, False):
                first_player_points = 0
                second_player_points = 1
            case (True, True):
                first_player_points = 0
                second_player_points = 0
            case _:
                raise RuntimeError("Invalid game result")
        
        self.score_tracker.register_match_result(first_player, second_player, first_player_points, second_player_points)
            
        self.match_log.add_result(first_player.name, second_player.name, first_player_points, second_player_points)


    def run_round(self, pairings):
        for pairing in pairings.pairs:
            self.run_match(pairing)
        self.score_tracker.end_round()

    def run_tournament(self):
        for _ in range(self.num_of_rounds):
            pairings = src.swiss.pairing_strategies.min_cost.pairings(self.match_log)
            self.run_round(pairings)
    
    def print_tournament_history(self):
        self.score_tracker.print_history()
