import unittest
from unittest.mock import patch, Mock
from src.sleeper_draft_tool import fetchers, models


class TestFetchers(unittest.TestCase):

    @patch("src.sleeper_draft_tool.fetchers.requests.get")
    def test_fetch_all_players_returns_dict(self, mock_get):
        mock_resp = Mock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"3086": {"first_name": "Tom", "last_name": "Brady"}}
        mock_get.return_value = mock_resp

        result = fetchers.fetch_all_players("http://api", "nfl")
        self.assertIsInstance(result, dict)
        self.assertIn("3086", result)
        self.assertEqual(result["3086"]["first_name"], "Tom")

    @patch("src.sleeper_draft_tool.fetchers.requests.get")
    def test_fetch_all_teams_returns_allteams(self, mock_get):
        mock_resp = Mock()
        mock_resp.status_code = 200
        # API may return a list of rosters
        mock_resp.json.return_value = [
            {
                "roster_id": 1,
                "owner_id": "owner1",
                "players": ["1046", "138"],
                "starters": ["1046"],
                "settings": {}
            }
        ]
        mock_get.return_value = mock_resp

        all_teams = fetchers.fetch_all_teams("http://api", "league1")
        self.assertIsInstance(all_teams, models.AllTeams)
        # roster_id 1 should exist as a string key
        self.assertIn("1", all_teams.teams)
        team = all_teams.get("1")
        self.assertEqual(team.roster_id, 1)
        self.assertIn("1046", team.players)

    @patch("src.sleeper_draft_tool.fetchers.requests.get")
    def test_fetch_all_users_returns_allusers(self, mock_get):
        mock_resp = Mock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = [
            {"user_id": "u1", "username": "sleeperuser", "display_name": "SleeperUser", "avatar": "abc"}
        ]
        mock_get.return_value = mock_resp

        all_users = fetchers.fetch_all_users("http://api", "league1")
        self.assertIsInstance(all_users, models.AllUsers)
        self.assertIn("u1", all_users.users)
        user = all_users.get("u1")
        self.assertEqual(user.username, "sleeperuser")

    @patch("src.sleeper_draft_tool.fetchers.requests.get")
    def test_fetch_all_player_projections(self, mock_get):
        mock_resp = Mock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"6462": {"pts_ppr": 150.0}}
        mock_get.return_value = mock_resp

        projections = fetchers.fetch_all_player_projections("http://api", "nfl", "2025", "regular")
        self.assertIsInstance(projections, dict)
        self.assertIn("6462", projections)
        self.assertEqual(projections["6462"]["pts_ppr"], 150.0)


if __name__ == "__main__":
    unittest.main()