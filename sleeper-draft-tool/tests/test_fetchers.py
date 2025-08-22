import unittest
from src.sleeper_draft_tool.fetchers import fetch_player_projections, fetch_scoring_settings, fetch_live_draft_info

class TestFetchers(unittest.TestCase):

    def test_fetch_player_projections(self):
        # Test fetching player projections
        projections = fetch_player_projections()
        self.assertIsInstance(projections, dict)
        self.assertIn('player_id', projections)

    def test_fetch_scoring_settings(self):
        # Test fetching scoring settings
        scoring_settings = fetch_scoring_settings()
        self.assertIsInstance(scoring_settings, dict)
        self.assertIn('scoring_type', scoring_settings)

    def test_fetch_live_draft_info(self):
        # Test fetching live draft information
        live_info = fetch_live_draft_info()
        self.assertIsInstance(live_info, dict)
        self.assertIn('teams', live_info)

if __name__ == '__main__':
    unittest.main()