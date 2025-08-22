# Contents of /sleeper-draft-tool/sleeper-draft-tool/src/sleeper_draft_tool/cli.py

import argparse
from sleeper_draft_tool import fetchers, scoring, value, draft_state

def main():
    parser = argparse.ArgumentParser(description='Fantasy Football Draft Tool CLI')
    parser.add_argument('--fetch', action='store_true', help='Fetch player data and projections')
    parser.add_argument('--score', action='store_true', help='Calculate scores based on current projections')
    parser.add_argument('--value', action='store_true', help='Calculate player values')
    parser.add_argument('--draft', action='store_true', help='Manage draft state')
    
    args = parser.parse_args()

    if args.fetch:
        fetchers.fetch_all_data()
        print("Fetched player data and projections.")
    
    if args.score:
        scoring.apply_scoring_settings()
        print("Applied scoring settings to projections.")
    
    if args.value:
        value.calculate_player_values()
        print("Calculated player values.")
    
    if args.draft:
        draft_state.manage_draft_state()
        print("Managed draft state.")

if __name__ == '__main__':
    main()