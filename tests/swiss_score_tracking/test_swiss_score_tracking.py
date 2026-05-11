import pytest

from pathlib import Path
from src.tournament.tournament import Tournament
from src.game.results.game_results import GameResults


def run_dummy_game(first_player_name, second_player_name):
    if first_player_name < second_player_name:
        return 1, 0
    elif first_player_name > second_player_name:
        return 0, 1
    return 0, 0

@pytest.mark.parametrize(
    "num_of_rounds",
    [1, 2, 3, 6, 12, 24]
)
def test_mathing_num_of_matches(num_of_rounds):
    tournament = Tournament(num_of_rounds=num_of_rounds, game_runner=run_dummy_game)
    tournament.load_players(Path(__file__).parent / "test_players.txt")

    tournament.run_tournament()

    swiss_matches = len(tournament.match_log._entries)
    tracker_matches = 0
    for round in tournament.score_tracker.prev_rounds:
        tracker_matches += len(round)

    assert swiss_matches == tracker_matches, f"MatchLog logged {swiss_matches} matches, ScoreTracker {tracker_matches}"


@pytest.mark.parametrize(
    "num_of_rounds",
    [1, 2, 3, 6, 12, 24]
)
def test_matching_points(num_of_rounds):
    tournament = Tournament(num_of_rounds=num_of_rounds, game_runner=run_dummy_game)
    tournament.load_players(Path(__file__).parent / "test_players.txt")

    tournament.run_tournament()

    for swiss_player in tournament.match_log.players():
        swiss_score = tournament.match_log.player_score(swiss_player)
        tracker_score = tournament.score_tracker.get_player(swiss_player).score
        print(f"Score for player {swiss_player}: MatchLog score = {swiss_score}, ScoreTracker score = {tracker_score}")
    
    for tracker_player in tournament.score_tracker.players:
        tracker_score = tracker_player.score
        swiss_score = tournament.match_log.player_score(tracker_player.name)
        print(f"Score for player {tracker_player.name}: ScoreTracker score = {tracker_score}, MatchLog score = {swiss_score}")

    for swiss_player in tournament.match_log.players():
        swiss_score = tournament.match_log.player_score(swiss_player)
        tracker_score = tournament.score_tracker.get_player(swiss_player).score
        assert swiss_score == tracker_score, f"Score mismatch for player {swiss_player}: MatchLog score = {swiss_score}, ScoreTracker score = {tracker_score}"

    for tracker_player in tournament.score_tracker.players:
        tracker_score = tracker_player.score
        swiss_score = tournament.match_log.player_score(tracker_player.name)
        assert tracker_score == swiss_score, f"Score mismatch for player {tracker_player.name}: ScoreTracker score = {tracker_score}, MatchLog score = {swiss_score}"


def test_final_results():
    tournament = Tournament(num_of_rounds=-1, game_runner=run_dummy_game)
    tournament.load_players(Path(__file__).parent / "test_players.txt")
    tournament.num_of_rounds = len(tournament.score_tracker.players) - 1
    tournament.run_tournament()

    player_ranks = sorted(tournament.score_tracker.players, key=lambda p: p.score, reverse=True)
    expected_ranks = sorted(tournament.score_tracker.players, key=lambda p: p.name)

    for player, expected in zip(player_ranks, expected_ranks):
        print(f"Player: {player.name}, Score: {player.score} - Expected: {expected.name}, Expected Score: {expected.score}")

    assert player_ranks == expected_ranks