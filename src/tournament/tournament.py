import logging
import sys
import pickle
import random
from pathlib import Path
import src.swiss.pairing_strategies.min_cost
from src.swiss.match_log import MatchLog
from src.player_process.docker_process import DockerProcess
from src.tournament.score_tracking import Player, ScoreTracker
from src.game.game import Game

CPU_LIMIT = "3"
MEMORY_LIMIT = "8g"

logger = logging.getLogger(__name__)

def docker_game_runner(first_player_name, second_player_name):
    first_process = DockerProcess(
        image_name=first_player_name,
        memory_limit=MEMORY_LIMIT,
        cpu_limit=CPU_LIMIT,
        container_name="player1"
    )
    second_process = DockerProcess(
        image_name=second_player_name,
        memory_limit=MEMORY_LIMIT,
        cpu_limit=CPU_LIMIT,
        container_name="player2"
    )

    try:
        game = Game(
            board_size_x=8,
            board_size_y=8,
            first_process=first_process,
            second_process=second_process,
            t_process_preparation=10.0,
            t_init=1.0,
            t_info_parsing=0.5,
            t_move=0.1,
            t_move_soft_limit=3.0
        )

        results = game.run()
    except Exception as e:
        logger.error(f"Error during game execution: {e}")
        sys.exit(1)
    finally:
        first_process.cleanup()
        second_process.cleanup()
    
    match (results.first_lost, results.second_lost):
                case (False, True):
                    return 1, 0
                case (True, False):
                    return 0, 1
                case (True, True):
                    return 0, 0
                case _:
                    raise RuntimeError("Invalid game result")


class Tournament:
    def __init__(self, num_of_rounds, game_runner=docker_game_runner):
        self.game_runner = game_runner
        self.num_of_rounds = num_of_rounds
        self.match_log = MatchLog()
        self.score_tracker = ScoreTracker()
    
    def load_players(self, players_file=None):
        if players_file is None:
            players_file = Path(__file__).parent.parent.parent / "players.txt"

        player_names = []
        with open(players_file, "r") as f:
            for line in f:
                player_names.append(line.strip())

        random.shuffle(player_names)
        for player_name in player_names:
            self.match_log.add_player(player_name)
            self.score_tracker.players.append(Player(name=player_name))


    def run_match(self, pairing):

        assert len(self.score_tracker.players) >= 2 and len(self.score_tracker.players) % 2 == 0, f"Unsupported number of players: {len(self.score_tracker.players)}"
        assert len(self.score_tracker.players) > self.num_of_rounds and self.num_of_rounds > 0, f"Invalid number of rounds: {self.num_of_rounds} for {len(self.score_tracker.players)} players"

        player_a = self.score_tracker.get_player(pairing.player_a)
        player_b = self.score_tracker.get_player(pairing.player_b)

        first_player, second_player = ScoreTracker.determine_first_player(player_a, player_b)

        first_player_points, second_player_points = self.game_runner(first_player.name, second_player.name)

        game_match = self.score_tracker.register_match_result(first_player, second_player, first_player_points, second_player_points)
        self.match_log.add_result(first_player.name, second_player.name, first_player_points, second_player_points)

        with open(Path(__file__).parent.parent.parent / "latest_match_log.pkl", "wb") as file:
            pickle.dump(self.match_log, file)
        
        with open(Path(__file__).parent.parent.parent / "latest_score_tracker.pkl", "wb") as file:
            pickle.dump(self.score_tracker, file)

        logger.info(f"{game_match.first_player.name} (S: {game_match.first_p_start_score}) (SB: {game_match.first_player.side_balance - 1}) vs {game_match.second_player.name} (S: {game_match.second_p_start_score}) (SB: {game_match.second_player.side_balance + 1}) - Result: {game_match.result.name}")

    def run_round(self, pairings):
        for pairing in pairings.pairs:
            self.run_match(pairing)
        self.score_tracker.end_round()

        logger.info(f"End of round {len(self.score_tracker.prev_rounds)}. Current standings:")
        for player in sorted(self.score_tracker.players, key=lambda p: p.score, reverse=True):
            logger.info(f"{player.name}: {player.score} points, Side Balance: {player.side_balance}")

    def run_tournament(self):
        for _ in range(self.num_of_rounds):
            pairings = src.swiss.pairing_strategies.min_cost.pairings(self.match_log)
            self.run_round(pairings)
    
    def print_tournament_history(self):
        self.score_tracker.print_history()
    
    def print_standings(self):
        sorted_players = sorted(self.score_tracker.players, key=lambda p: p.score, reverse=True)
        print("Standings:")
        for player in sorted_players:
            print(f"{player.name}: {player.score} points, Side Balance: {player.side_balance}")