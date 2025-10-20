# Naishi Test Suite

Comprehensive test suite for the Naishi card game implementation, organized by test type and purpose.

## Directory Structure

```
tests/
├── unit/              # Unit tests for core GameState components
├── integration/       # Integration tests for multi-component workflows
├── compliance/        # RULES.md compliance verification tests
└── manual/           # Manual testing utilities and guides
```

---

## Unit Tests (`tests/unit/`)

Tests for individual GameState components and game mechanics.

### Turn Structure & Actions
- **test_turn_structure.py** - Turn state tracking (optional_emissary_available, must_develop, clear_turn_state)
- **test_optional_emissary.py** - Option A: Develop → Optional Emissary flow
- **test_emissary_turn_context.py** - Emissary actions handling turn context (Option A vs Option B)
- **test_must_develop.py** - Option B: Emissary → Required Develop enforcement
- **test_actions.py** - All game actions (develop, swap, discard, recall, decree, end)

### Game Mechanics
- **test_setup_draft.py** - Game setup and draft phase (RULES.md Section 2)
- **test_recall.py** - Recall emissaries functionality (RULES.md Section 5.3)
- **test_decree.py** - Imperial Decree functionality (RULES.md Section 5.4)
- **test_game_ending.py** - Game ending conditions and P2 final turn fairness (RULES.md Section 7)
- **test_scoring.py** - All 12 card types scoring rules (RULES.md Section 8)

### Running Unit Tests
```bash
# Run all unit tests
pytest tests/unit/

# Run specific test file
pytest tests/unit/test_turn_structure.py

# Run with verbose output
pytest tests/unit/ -v
```

---

## Integration Tests (`tests/integration/`)

Tests for multi-component workflows and end-to-end scenarios.

### Environment Tests
- **test_env_multi_action.py** - Multi-action turn support in NaishiEnv
- **test_env_flag_lifecycle.py** - Turn state flag lifecycle in environment
- **test_env_integration.py** - Full environment integration
- **test_env_complete.py** - Complete environment workflows

### UI & Gameplay Tests
- **test_ui_integration.py** - UI component integration
- **test_optional_emissary_flow.py** - Optional emissary flow in complete game
- **test_complete_games.py** - Full game simulations from start to finish

### Running Integration Tests
```bash
# Run all integration tests
pytest tests/integration/

# Run specific test
pytest tests/integration/test_complete_games.py -v
```

---

## Compliance Tests (`tests/compliance/`)

Tests verifying RULES.md compliance and single source of truth architecture.

### Architecture Compliance
- **test_env_delegation.py** - Verify naishi_env.py delegates all logic to GameState
- **test_pvp_delegation.py** - Verify naishi_pvp.py queries GameState for turn state
- **test_pvp_no_logic.py** - Verify naishi_pvp.py contains zero game logic
- **test_ai_delegation.py** - Verify play_vs_ai.py queries GameState for turn state
- **test_ai_no_logic.py** - Verify play_vs_ai.py contains zero game logic
- **test_ui_purity.py** - Verify naishi_ui.py is pure display (no calculation)
- **test_ui_no_logic.py** - Verify UI files contain zero game logic

### Documentation Compliance
- **test_documentation.py** - Verify code documentation references RULES.md
- **test_readme.py** - Verify README.md compliance information
- **test_compliance_matrix.py** - Verify compliance matrix is up-to-date
- **test_final_report.py** - Verify final compliance report
- **test_validation_guide.py** - Verify compliance validation guide
- **test_deviations.py** - Verify documented deviations from RULES.md

### Running Compliance Tests
```bash
# Run all compliance tests
pytest tests/compliance/

# Run architecture compliance only
pytest tests/compliance/test_*_delegation.py tests/compliance/test_*_no_logic.py
```

---

## Manual Tests (`tests/manual/`)

Manual testing utilities and verification scripts.

- **test_guide.py** - Interactive manual testing guide
- **verify_complete_games.py** - Manual verification of complete game scenarios
- **manual_test_output.txt** - Sample output from manual testing

### Running Manual Tests
```bash
# Run interactive test guide
python tests/manual/test_guide.py

# Run verification script
python tests/manual/verify_complete_games.py
```

---

## Running All Tests

```bash
# Run entire test suite
pytest tests/

# Run with coverage
pytest tests/ --cov=naishi_core --cov=naishi_env --cov-report=html

# Run specific category
pytest tests/unit/
pytest tests/integration/
pytest tests/compliance/

# Run with markers (if configured)
pytest -m "unit"
pytest -m "integration"
pytest -m "compliance"
```

---

## Test Organization Principles

### Unit Tests
- Test individual components in isolation
- Fast execution (< 1 second per test)
- No external dependencies
- Focus on GameState methods

### Integration Tests
- Test multiple components working together
- May take longer to execute
- Test complete workflows
- Verify component interactions

### Compliance Tests
- Verify RULES.md compliance
- Verify single source of truth architecture
- Check for game logic in UI layer
- Validate documentation

### Manual Tests
- Interactive testing
- Human verification
- Edge case exploration
- Usability testing

---

## Test Naming Conventions

- **test_[component]_[feature].py** - Unit tests for specific component features
- **test_[workflow]_[scenario].py** - Integration tests for workflows
- **test_[aspect]_[check].py** - Compliance tests for specific checks

---

## Adding New Tests

### For New Features
1. Add unit tests in `tests/unit/` for core logic
2. Add integration tests in `tests/integration/` for workflows
3. Add compliance tests in `tests/compliance/` if architecture changes
4. Update this README with test descriptions

### For Bug Fixes
1. Add regression test reproducing the bug
2. Fix the bug
3. Verify test passes
4. Keep test to prevent regression

---

## Test Coverage Goals

- **Unit Tests:** 90%+ coverage of naishi_core
- **Integration Tests:** All major workflows covered
- **Compliance Tests:** 100% architecture compliance
- **Manual Tests:** All user-facing features tested

---

## Continuous Integration

Tests are run automatically on:
- Every commit (unit tests)
- Every pull request (all tests)
- Nightly builds (full suite + manual verification)

---

## Related Documentation

- **RULES.md** - Authoritative game rules specification
- **reports/COMPLIANCE_VALIDATION_GUIDE.md** - How to verify compliance
- **reports/MANUAL_TESTING_QUICK_START.md** - Manual testing procedures
- **.kiro/specs/full-compliance-audit/** - Detailed audit reports

---

## Test Statistics

- **Total Tests:** 35+ test files
- **Unit Tests:** 10 files
- **Integration Tests:** 7 files
- **Compliance Tests:** 13 files
- **Manual Tests:** 2 files + utilities

---

## Troubleshooting

### Import Errors
If you get import errors, ensure you're running from the project root:
```bash
cd /path/to/naishi-rl
pytest tests/
```

### Slow Tests
Integration tests may be slower. Run unit tests for quick feedback:
```bash
pytest tests/unit/  # Fast
```

### Failed Compliance Tests
If compliance tests fail, check:
1. Did you add game logic outside GameState?
2. Did you modify RULES.md without updating code?
3. Did you update documentation?

---

**Last Updated:** October 20, 2025
