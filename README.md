# naishi-rl
Reinforcement Learning approach to the Naishi board game

## Features

- **Self-Play Training** - Models train against themselves to continuously improve
- **Automatic Versioning** - Every training run creates a unique timestamped model
- **Comprehensive Analytics** - 12 interactive chart categories analyzing every aspect of model behavior
- **Model Comparison** - Compare multiple models side-by-side to track improvement

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Train a Model

```bash
python train_main_agent.py
```

This will:
- Load the best existing model (or start fresh)
- Train against itself using self-play
- Save checkpoints every 50k timesteps
- Create a unique timestamped model when complete

### 3. Analyze Your Model

```bash
python analyze_model.py
```

This generates a comprehensive interactive report with:
- Win rate analysis
- Score distributions
- Action patterns
- Card preferences
- Character synergies
- Strategic insights
- And much more!

### 4. Compare Models

```bash
python compare_models.py
```

Auto-detects all models and creates side-by-side comparisons.

## Training System

### Self-Play Training
- Models train against themselves
- Opponent updates every 20,480 timesteps
- Progressively stronger opponents = better learning

### Automatic Versioning
- Every run creates: `models/naishi_model_YYYYMMDD_HHMMSS.zip`
- Checkpoints saved to: `models/checkpoints/YYYYMMDD_HHMMSS/`
- Default model updated: `models/naishi_model.zip`

### Continuous Improvement
- Each new training run starts from the best existing model
- Builds on previous generations
- Never loses progress

## Analytics System

### 12 Interactive Chart Categories

1. **Win Rate Analysis** - Performance metrics
2. **Score Analysis** - Score distributions and comparisons
3. **Action Distribution** - What actions the model uses
4. **Draft Phase Analysis** - Draft strategy insights
5. **Card Preferences** - What cards the model values
6. **Deck Preferences** - River deck selection patterns
7. **Swap Analysis** - Swap behavior and patterns
8. **Emissary Usage** - Resource management efficiency
9. **Timing Analysis** - Game flow and timing
10. **Position Heatmap** - Positional preferences
11. **Character Synergies** - Discovered combinations
12. **Strategic Overview** - High-level metrics dashboard

### Usage

```bash
# Analyze default model
python analyze_model.py

# Analyze specific model
python analyze_model.py models/naishi_model_20251020_004131

# More games = better statistics
python analyze_model.py models/naishi_model 500

# Compare all models
python compare_models.py
```

See [ANALYTICS_README.md](ANALYTICS_README.md) for complete documentation.

## RULES.md Compliance

This codebase is fully compliant with [RULES.md](RULES.md), the authoritative specification for Naishi game rules.

### Architecture: Single Source of Truth

All game logic is centralized in `naishi_core/game_logic.py` (GameState class). Every component delegates to this single source:

- **naishi_env.py** - RL environment delegates all game operations to GameState
- **naishi_pvp.py** - Human vs Human gameplay delegates to GameState
- **play_vs_ai.py** - Human vs AI gameplay delegates to GameState
- **train_main_agent.py** - Training uses NaishiEnv which delegates to GameState

No game logic exists outside of naishi_core. This ensures:
- Consistent rule enforcement across all modes
- Single point of maintenance for rule changes
- Guaranteed compliance with RULES.md

### UI Layer Purity

The UI layer (`naishi_ui.py` and UI code in gameplay files) contains zero game logic:

- **Display only** - UI functions only format and display game state
- **Input conversion** - UI only converts user input to action arrays
- **No validation** - All action validation happens in GameState
- **No state management** - GameState manages all game state
- **Query-based** - UI queries GameState for all game information

This separation ensures:
- UI changes never affect game rules
- Easy to add new UI modes (CLI, GUI, web)
- Clear separation of concerns

### Complete RULES.md Implementation

Every section of RULES.md is implemented in naishi_core:

- **Section 2 (Setup)** - Draft phase, Mountain distribution, initial state
- **Section 4 (Turn Structure)** - Both turn options (Develop→Emissary, Emissary→Develop)
- **Section 5.1 (Develop)** - Position mapping, card replacement
- **Section 5.2 (Emissary)** - All 4 swap types, discard, spot tracking
- **Section 5.3 (Recall)** - Emissary restoration, marker clearing
- **Section 5.4 (Decree)** - Card swapping, permanent lock, once-per-game
- **Section 7 (Game End)** - Declare end, auto-end, turn fairness
- **Section 8 (Scoring)** - All 12 card types, adjacency, Ninja copying, tiebreaker

### Validation

Compliance is validated through:
- **Unit tests** - Test each RULES.md section independently
- **Integration tests** - Test complete game flows
- **Manual testing** - Human gameplay verification
- **Compliance matrix** - Systematic tracking of all requirements

See `.kiro/specs/full-compliance-audit/` for detailed audit reports and compliance documentation.

## Project Structure

```
naishi-rl/
├── train_main_agent.py      # Main training script
├── analyze_model.py          # Analytics CLI
├── compare_models.py         # Model comparison tool
├── model_analytics.py        # Analytics engine
├── naishi_env.py            # Gymnasium environment (delegates to naishi_core)
├── naishi_pvp.py            # Human vs Human (delegates to naishi_core)
├── play_vs_ai.py            # Human vs AI (delegates to naishi_core)
├── naishi_ui.py             # Pure UI layer (display only)
├── naishi_core/             # Single source of truth for game logic
│   ├── game_logic.py        # GameState - all game rules
│   ├── player.py            # Player state
│   ├── river.py             # River deck management
│   ├── scorer.py            # Scoring logic
│   ├── constants.py         # Game constants
│   └── utils.py             # Utility functions
├── policies.py              # Policy implementations
├── models/                  # Trained models
│   ├── naishi_model.zip    # Latest model
│   ├── naishi_model_*.zip  # Timestamped versions
│   └── checkpoints/        # Training checkpoints
├── analytics_reports/       # Generated reports
└── .kiro/specs/             # Compliance documentation
    └── full-compliance-audit/

```

## Documentation

- [ANALYTICS_README.md](ANALYTICS_README.md) - Complete analytics documentation
- [SETUP_ANALYTICS.md](SETUP_ANALYTICS.md) - Quick setup guide
- [ANALYTICS_SUMMARY.md](ANALYTICS_SUMMARY.md) - Analytics overview
- [RULES.md](RULES.md) - Naishi game rules

## Play Against Your Model

```bash
python play_vs_ai.py
```

Play interactively against your trained model!

## Requirements

- Python 3.8+
- gymnasium
- stable-baselines3
- numpy
- plotly (for analytics)

See [requirements.txt](requirements.txt) for complete list.
