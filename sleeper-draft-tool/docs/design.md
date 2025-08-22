# Design Document for Sleeper Draft Tool

## Overview
The Sleeper Draft Tool is designed to assist users in making informed decisions during fantasy football auction drafts. It provides real-time data on available players, their projected values, and other relevant metrics to optimize draft strategies.

## Purpose
The primary purpose of this tool is to enhance the drafting experience by providing accurate player valuations based on various factors, including player projections, team needs, and available budget.

## Features
- **Player Valuation**: Assign draft values to all players available in the Sleeper system.
- **Live Updates**: Adjust player values in real-time based on draft actions and team budgets.
- **Comprehensive Metrics**: Calculate values based on:
  - Player projections
  - Value over replacement
  - Available draft dollars
  - Total available draft dollars
  - Team value
  - Positional standard deviation

## Value Calculation
### Types of Value
1. **Raw Value**: The cost of a player based on their projected points.
2. **Adjusted Value**: The cost of players considering available roster spots and budget constraints.

### Draft Goal
The objective is to finish the draft with the maximum possible team projection.

## Requirements
### Data Fetching
- Fetch all player projections.
- Retrieve scoring settings and apply them to get accurate projections.
- Gather roster settings and live draft information, including each team's available budget and drafted players.

## Design Architecture
### File Structure
- **src/sleeper_draft_tool/**: Contains the core application logic.
  - `__init__.py`: Initializes the package.
  - `config.py`: Configuration settings.
  - `models.py`: Data models for players and teams.
  - `fetchers.py`: Functions to fetch external data.
  - `scoring.py`: Scoring logic.
  - `value.py`: Value calculation logic.
  - `draft_state.py`: Manages the draft state.
  - `gui.py`: Graphical user interface setup.
  - `cli.py`: Command-line interface functionality.
  - `utils.py`: Utility functions.

- **tests/**: Contains unit tests for the application.
  - `__init__.py`: Initializes the test package.
  - `test_fetchers.py`: Tests for data fetching functions.
  - `test_value.py`: Tests for value calculations.
  - `test_draft_state.py`: Tests for draft state management.

- **docs/**: Documentation for the project.
  - `design.md`: Design decisions and architecture.

### User Interface
- **Player View**: Displays all players with their projections and values, grouped by position.
- **Selected Player View**: Shows detailed draft data and real-time adjusted value for a selected player.
- **Draft Results View**: Displays all teams' drafted players and their projected team values.

## Conclusion
The Sleeper Draft Tool aims to provide a comprehensive solution for fantasy football drafting, leveraging real-time data and advanced calculations to enhance user decision-making. The design is modular, allowing for easy updates and maintenance as league rules and player data evolve.