# README.md

# Fantasy Football Draft Tool

## Overview

The Fantasy Football Draft Tool is designed to provide real-time data on available players and their projected values to assist users in making informed decisions during auction drafts. The tool calculates player values based on various parameters, ensuring that users can maximize their team's projected points.

## Features

- Assigns draft values to all available players in the Sleeper system.
- Live updates draft values based on draft actions.
- Calculates player values using projections, value over replacement, available draft dollars, and more.
- Provides a graphical user interface (GUI) for easy interaction.
- Includes a command-line interface (CLI) for terminal-based usage.

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   ```
2. Navigate to the project directory:
   ```
   cd sleeper-draft-tool
   ```
3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

To start the application, you can either use the GUI or the CLI:

### GUI

Run the following command to launch the graphical user interface:
```
python -m src.sleeper_draft_tool.gui
```

### CLI

For command-line usage, run:
```
python -m src.sleeper_draft_tool.cli
```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.