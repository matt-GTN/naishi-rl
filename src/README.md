# Naishi Source Code

This directory contains the organized source code for the Naishi card game implementation.

## Directory Structure

```
src/
├── ui/              # User interface components
├── gameplay/        # Gameplay interfaces (PvP, vs AI)
├── training/        # RL training utilities
└── analysis/        # Model analysis and evaluation
```

---

## UI Components (`src/ui/`)

Terminal-based user interface for displaying game state.

### Files
- **banner.py** - ASCII art banner for game title
- **naishi_ui.py** - Rich terminal UI for displaying game state
  - Pure display functions (no game logic)
  - Delegates all state queries to GameState
  - Formats and displays: river, player cards, scores, etc.

### Usage
```python
from src.ui.naishi_ui import NaishiUI
from naishi_core.game_logic import GameState

gs = GameState.create_initial_state()
NaishiUI.show_full_state(gs)
```

---

## Gameplay Interfaces (`src/gameplay/`)

Human-playable game interfaces.

### Files
- **naishi_pvp.py** - Human vs Human gameplay
  - Console-based 2-player interface
  - Pure UI wrapper around GameState
  - Zero game logic (all delegated to GameState)

- **play_vs_ai.py** - Human vs AI gameplay
  - Play against trained RL agents or random policy
  - Supports both human and AI players
  - Pure UI wrapper around GameState

### Usage
```python
# Human vs Human
from src.gameplay.naishi_pvp import NaishiPvP
game = NaishiPvP()
game.play()

# Human vs AI
from src.gameplay.play_vs_ai import PlayVsAI, random_policy
game = PlayVsAI(ai_policy=random_policy)
game.play()
```

### Convenience Scripts
Use the root-level convenience scripts:
```bash
python play_pvp.py              # Human vs Human
python play_ai.py               # Human vs AI (random)
python play_ai.py models/agent  # Human vs trained AI
```

---

## Training Utilities (`src/training/`)

RL training infrastructure using Stable-Baselines3.

### Files
- **naishi_env.py** - Gymnasium environment
  - Wraps GameState for RL training
  - Provides action masking for MaskablePPO
  - Supports opponent policies for self-play
  - Pure delegation to GameState (zero game logic)

- **train_main_agent.py** - Main training script
  - Trains MaskablePPO agents
  - Supports self-play training
  - Configurable hyperparameters
  - Saves models and training logs

- **policies.py** - Custom policy classes
  - MaskedRandomPolicy - Random baseline
  - SelfPlayPolicy - Self-play opponent
  - Custom policy implementations

- **naishi_callbacks.py** - Training callbacks
  - ObservabilityCallback - Monitor training progress
  - Custom metrics and logging
  - Visualization utilities

- **run_sequential_trainings.py** - Batch training
  - Run multiple training sessions
  - Automated hyperparameter sweeps
  - Sequential execution

### Usage
```python
# Train an agent
from src.training.train_main_agent import main
main()

# Use the environment
from src.training.naishi_env import NaishiEnv
env = NaishiEnv()
obs, info = env.reset()
```

### Convenience Scripts
```bash
python train.py                 # Train with default settings
```

---

## Analysis Tools (`src/analysis/`)

Model evaluation and performance analysis.

### Files
- **model_analytics.py** - Comprehensive analytics
  - ModelAnalytics class for model evaluation
  - Interactive Plotly visualizations
  - Performance metrics and statistics
  - Card usage analysis
  - Win rate tracking

- **analyze_model.py** - Quick analysis script
  - Analyze a single model
  - Generate comprehensive reports
  - Save visualizations

- **compare_models.py** - Model comparison
  - Compare multiple models side-by-side
  - Comparative visualizations
  - Performance benchmarking

### Usage
```python
# Analyze a model
from src.analysis.model_analytics import analyze_model
analyze_model("models/naishi_model", num_games=100)

# Compare models
from src.analysis.compare_models import compare_models
compare_models(["models/v1", "models/v2"], num_games=100)
```

### Convenience Scripts
```bash
python analyze.py models/agent 100    # Analyze model with 100 games
```

---

## Architecture Principles

### Single Source of Truth
All game logic resides in `naishi_core/`. The `src/` directory contains:
- **UI**: Pure display and input conversion
- **Gameplay**: UI wrappers that delegate to GameState
- **Training**: RL infrastructure that delegates to GameState
- **Analysis**: Evaluation tools that query GameState

### Zero Game Logic Outside Core
- ✅ All files in `src/` delegate to `naishi_core.GameState`
- ✅ No game rules implemented in UI/gameplay/training
- ✅ Pure separation of concerns
- ✅ Maintainable and testable architecture

### Import Structure
```python
# Core game logic (single source of truth)
from naishi_core.game_logic import GameState
from naishi_core.constants import *
from naishi_core.scorer import Scorer

# UI components
from src.ui.naishi_ui import NaishiUI
from src.ui.banner import print_banner

# Gameplay interfaces
from src.gameplay.naishi_pvp import NaishiPvP
from src.gameplay.play_vs_ai import PlayVsAI

# Training utilities
from src.training.naishi_env import NaishiEnv
from src.training.policies import MaskedRandomPolicy

# Analysis tools
from src.analysis.model_analytics import analyze_model
```

---

## Development Guidelines

### Adding New Features

1. **Game Logic**: Add to `naishi_core/` (single source of truth)
2. **UI**: Add display functions to `src/ui/naishi_ui.py`
3. **Gameplay**: Update `src/gameplay/` to use new GameState features
4. **Training**: Update `src/training/naishi_env.py` if needed
5. **Analysis**: Add new metrics to `src/analysis/model_analytics.py`

### Testing

All tests are in the `tests/` directory:
```bash
pytest tests/unit/              # Unit tests for core logic
pytest tests/integration/       # Integration tests
pytest tests/compliance/        # Architecture compliance tests
```

### Code Quality

- ✅ All game logic in `naishi_core/`
- ✅ Pure UI functions (no state modification)
- ✅ Proper delegation patterns
- ✅ Type hints where appropriate
- ✅ Docstrings for public APIs

---

## File Organization Summary

| Directory | Purpose | Game Logic? | Delegates To |
|-----------|---------|-------------|--------------|
| `src/ui/` | Display | ❌ No | GameState (read-only) |
| `src/gameplay/` | User interfaces | ❌ No | GameState |
| `src/training/` | RL infrastructure | ❌ No | GameState |
| `src/analysis/` | Model evaluation | ❌ No | GameState |
| `naishi_core/` | Game rules | ✅ Yes | N/A (source of truth) |

---

## Related Documentation

- **RULES.md** - Authoritative game rules
- **tests/README.md** - Test suite documentation
- **reports/** - Compliance and audit reports
- **.kiro/specs/full-compliance-audit/** - Detailed compliance audit

---

**Last Updated:** October 20, 2025
