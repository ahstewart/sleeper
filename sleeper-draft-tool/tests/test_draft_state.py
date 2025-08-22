import unittest
from src.sleeper_draft_tool.draft_state import DraftState

class TestDraftState(unittest.TestCase):

    def setUp(self):
        self.draft_state = DraftState()

    def test_initial_state(self):
        self.assertEqual(self.draft_state.available_players, [])
        self.assertEqual(self.draft_state.team_budgets, {})
        self.assertEqual(self.draft_state.drafted_players, [])

    def test_add_player(self):
        self.draft_state.add_player('Player A', 10)
        self.assertIn('Player A', self.draft_state.drafted_players)

    def test_update_budget(self):
        self.draft_state.update_budget('Team 1', 100)
        self.assertEqual(self.draft_state.team_budgets['Team 1'], 100)

    def test_remove_player(self):
        self.draft_state.add_player('Player B', 15)
        self.draft_state.remove_player('Player B')
        self.assertNotIn('Player B', self.draft_state.drafted_players)

if __name__ == '__main__':
    unittest.main()