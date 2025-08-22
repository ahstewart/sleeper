# Contents of /sleeper-draft-tool/sleeper-draft-tool/tests/test_value.py

import unittest
from src.sleeper_draft_tool.value import calculate_raw_value, calculate_adjusted_value

class TestValueCalculations(unittest.TestCase):

    def test_calculate_raw_value(self):
        # Example test case for raw value calculation
        player_projection = 200
        expected_value = player_projection  # Assuming raw value is equal to projection for this example
        self.assertEqual(calculate_raw_value(player_projection), expected_value)

    def test_calculate_adjusted_value(self):
        # Example test case for adjusted value calculation
        player_projection = 200
        available_money = 100
        roster_spots = 3
        expected_adjusted_value = player_projection * (available_money / roster_spots)  # Simplified example
        self.assertEqual(calculate_adjusted_value(player_projection, available_money, roster_spots), expected_adjusted_value)

if __name__ == '__main__':
    unittest.main()