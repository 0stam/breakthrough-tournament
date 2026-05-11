import sys

import pytest

from tests.swiss_score_tracking.dummy_tournament import DummyTournament as DummyTournament

@pytest.mark.parametrize(
    "num_of_rounds",
    [1, 2, 3, 6, 12, 24]
)
def test_matching_points(num_of_rounds):
    tournament = DummyTournament(num_of_rounds=num_of_rounds)
    tournament.load_players()

    tournament.run_tournament()

    for swiss_player in tournament.match_log.ranking:
        assert tournament.match_log.player_score(swiss_player) == tournament.score_tracker.get_player(swiss_player).score
    
    for tracker_player in tournament.score_tracker.players:
        assert tournament.match_log.player_score(tracker_player.name) == tracker_player.score


