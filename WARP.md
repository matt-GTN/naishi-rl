# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

This is a Reinforcement Learning approach to the Naismith board game. The codebase implements a digital version of the board game with an interactive command-line interface, featuring card drafting, deck management, and a colorful ASCII banner.

## Development Commands

### Running the Game
```bash
python3 game.py
```

### Running Individual Modules
```bash
# Test the banner display
python3 -c "from banner import print_banner; print_banner()"

# Create and display game state
python3 -c "from naishi import GameState; game = GameState.create_initial_state(); game.show()"
```

### Code Quality
```bash
# Type checking (if mypy is installed)
python3 -m mypy naishi.py game.py banner.py

# Code formatting (if black is installed)
python3 -m black naishi.py game.py banner.py

# Linting (if flake8 is installed)
python3 -m flake8 naishi.py game.py banner.py
```

## Architecture Overview

The project follows a clean modular architecture:

### Core Game Logic (`naishi.py`)
- **GameState dataclass**: Centralized game state management with immutable initialization
- **Factory pattern**: `GameState.create_initial_state()` handles all game setup including card shuffling, deck creation, and player drafting
- **Interactive drafting system**: Players choose cards to exchange during setup
- **Display system**: ASCII-formatted game board visualization

### Game Flow
1. **Initialization**: Cards are defined with quantities, shuffled into 5 decks of 6 cards each
2. **Player Setup**: Each player gets 2 initial cards plus 3 Mountains
3. **Card Drafting**: Interactive exchange phase where players swap cards
4. **Game Display**: Formatted display showing decks, player lines, and hands

### Key Game Components
- **11 unique card types**: Naishi, Councellor, Sentinel, Fort, Monk, Torii, Knight, Banner, Rice fields, Ronin, Ninja
- **Mountain cards**: Base terrain cards (3 per player)
- **5 decks**: Central card pools (6 cards each)
- **Player lines**: 5-card battle lines (initially all Mountains)
- **Player hands**: 5-card hands for each player

### Presentation Layer (`banner.py`)
- **ASCII art system**: Converts text to block letters with gradient coloring
- **Terminal color support**: Uses ANSI escape codes for pink-to-deep-pink gradients
- **Modular design**: Reusable banner generation for any text

### Entry Point (`game.py`)
- Simple orchestration layer that initializes and displays the game

## Technical Details

### Dependencies
- Pure Python 3.13+ (no external dependencies)
- Uses standard library modules: `typing`, `dataclasses`, `random`

### Game State Management
- Immutable initialization pattern prevents state corruption
- All randomization handled during setup with optional seeding for reproducible games
- Clear separation between game logic and presentation

### Interactive Elements
- Input validation with retry loops
- Clear prompts for user decisions during card drafting
- Error handling for invalid inputs

## Development Notes

- The codebase is designed for future RL integration (hence the project name)
- Card exchange logic uses index-based swapping for deterministic results
- Display formatting uses fixed-width layouts for consistent presentation
- Color gradients are calculated mathematically for smooth visual effects