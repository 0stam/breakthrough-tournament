import sys

import pytest

from tests.swiss_score_tracking.dummy_tournament import DummyTournament as DummyTournament

@pytest.mark.parametrize(
    "num_of_rounds",
    [1, 2, 3, 6, 12, 24]
)
def test_mathing_num_of_matches(num_of_rounds):
    tournament = DummyTournament(num_of_rounds=num_of_rounds)
    tournament.load_players()

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
    tournament = DummyTournament(num_of_rounds=num_of_rounds)
    tournament.load_players()

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


