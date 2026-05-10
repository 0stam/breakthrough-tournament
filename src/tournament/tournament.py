import sys
import src.swiss.pairing_strategies.min_cost
from src.swiss.match_log import MatchLog
from src.player_process.player_process import PlayerProcess
# from src.player_process.docker_process import DockerProcess
from src.tournament.score_tracking import Player, MatchResult, ScoreTracker
from src.game.game import Game

CPU_LIMIT = "3"
MEMORY_LIMIT = "8g"

class Tournament:
    def __init__(self,num_of_rounds, match_log = MatchLog()):
        self.num_of_rounds = num_of_rounds
        self.match_log = match_log
        self.score_tracker = ScoreTracker()
    
    def load_players(self):
        with open("players.txt", "r") as f:
            for line in f:
                self.match_log.add_player(line.strip())
                self.score_tracker.players.append(Player(name=line.strip()))

    def run_match(self, pairing):

        player_a = self.score_tracker.get_player(pairing.player_a)
        player_b = self.score_tracker.get_player(pairing.player_b)

        first_player, second_player = ScoreTracker.determine_first_player(player_a, player_b)

        # first_process = DockerProcess(
        #     image_name=pairing.player_a,
        #     memory_limit=MEMORY_LIMIT,
        #     cpu_limit=CPU_LIMIT,
        #     container_name="player1"
        # )
        # second_process = DockerProcess(
        #     image_name=pairing.player_b,
        #     memory_limit=MEMORY_LIMIT,
        #     cpu_limit=CPU_LIMIT,
        #     container_name="player2"
        # )

        first_process = PlayerProcess([sys.executable, "-m", "tests.game.dummy_process"])
        second_process = PlayerProcess([sys.executable, "-m", "tests.game.dummy_process"])

        try:
            game = Game(
                board_size_x=8,
                board_size_y=8,
                first_process=first_process,
                second_process=second_process,
                t_process_preparation=10.0,
                t_init=1.0,
                t_info_parsing=0.5,
                t_move=0.1
            )

            results = game.run()
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
            
            self.score_tracker.register_match_result(first_player, second_player, results)
                
            self.match_log.add_result(first_player.name, second_player.name, first_player_points, second_player_points)

        except Exception as e:
            print(f"Error during game execution: {e}")
            sys.exit(1)
        finally:
            first_process.cleanup()
            second_process.cleanup()

    def run_round(self, pairings):
        for pairing in pairings.pairs:
            self.run_match(pairing)
        self.score_tracker.end_round()

    def run_tournament(self):
        for round in range(self.num_of_rounds):
            pairings = src.swiss.pairing_strategies.min_cost.pairings(self.match_log)
            self.run_round(pairings)
    
    def print_standings(self):
        self.score_tracker.print_history()
        print("Wynik od zioma:")
        for player in self.match_log.ranking():
            print(f"{player}: {self.match_log.player_score(player)}")