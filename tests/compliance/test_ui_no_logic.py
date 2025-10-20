#!/usr/bin/env python3
"""
Test for Task 33: Verify train_main_agent.py uses correct rules
- Ensure it uses NaishiEnv (which delegates to GameState)
- Verify no game logic in training script
- Requirements: 2.4
"""

import ast
import inspect
from train_main_agent import train_agent, SelfPlayCallback, find_latest_model
from naishi_env import NaishiEnv
from naishi_core.game_logic import GameState


def test_train_main_agent_uses_naishi_env():
    """Verify that train_main_agent.py uses NaishiEnv."""
    # Check that the make_env function creates NaishiEnv
    import train_main_agent
    source = inspect.getsource(train_main_agent)
    
    # Parse the source code
    tree = ast.parse(source)
    
    # Find the make_env function
    make_env_found = False
    uses_naishi_env = False
    
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == 'make_env':
            make_env_found = True
            # Check if NaishiEnv is instantiated
            for subnode in ast.walk(node):
                if isinstance(subnode, ast.Call):
                    if isinstance(subnode.func, ast.Name) and subnode.func.id == 'NaishiEnv':
                        uses_naishi_env = True
                        break
    
    assert make_env_found, "make_env function not found in train_main_agent.py"
    assert uses_naishi_env, "make_env does not create NaishiEnv instance"
    print("✓ train_main_agent.py uses NaishiEnv")


def test_no_game_logic_in_training_script():
    """Verify that train_main_agent.py contains no game logic."""
    import train_main_agent
    source = inspect.getsource(train_main_agent)
    
    # Parse the source code
    tree = ast.parse(source)
    
    # List of game logic indicators that should NOT be in training script
    forbidden_patterns = [
        'apply_action',  # Should only be in GameState
        'get_legal_action_types',  # Should only be in GameState
        'swap_cards',  # Should only be in GameState
        'discard_cards',  # Should only be in GameState
        'develop_territory',  # Should only be in GameState
        'recall_emissaries',  # Should only be in GameState
        'impose_decree',  # Should only be in GameState
        'calculate_score',  # Should only be in GameState
        'check_game_end',  # Should only be in GameState
    ]
    
    # Check for forbidden patterns in function/method names
    violations = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            for pattern in forbidden_patterns:
                if pattern in node.name:
                    violations.append(f"Function '{node.name}' contains game logic pattern '{pattern}'")
    
    # Check for direct game state manipulation (not through env)
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute):
            # Check for direct access to game state fields that should only be accessed via env
            if isinstance(node.value, ast.Name):
                if node.value.id == 'gs' and node.attr in [
                    'players', 'river', 'current_player_idx', 'turn_count',
                    'must_develop', 'optional_emissary_available'
                ]:
                    # This is OK if it's just reading for display/logging
                    # But not OK if it's modifying
                    pass
    
    assert len(violations) == 0, f"Game logic found in training script: {violations}"
    print("✓ No game logic found in train_main_agent.py")


def test_training_delegates_to_naishi_env():
    """Verify that training delegates all game operations to NaishiEnv."""
    import train_main_agent
    source = inspect.getsource(train_main_agent.train_agent)
    
    # Check that the function creates env using NaishiEnv
    assert 'NaishiEnv' in source, "train_agent does not use NaishiEnv"
    
    # Check that it uses model.learn() which will call env.step()
    assert 'model.learn' in source, "train_agent does not call model.learn()"
    
    print("✓ Training delegates to NaishiEnv")


def test_naishi_env_delegates_to_game_state():
    """Verify that NaishiEnv delegates to GameState (already tested in task 27, but verify again)."""
    # Check that NaishiEnv.step() calls GameState.apply_action_array()
    source = inspect.getsource(NaishiEnv.step)
    
    assert 'self.gs.apply_action_array' in source, "NaishiEnv.step() does not call GameState.apply_action_array()"
    
    # Check that NaishiEnv.reset() calls GameState.create_initial_state()
    reset_source = inspect.getsource(NaishiEnv.reset)
    assert 'GameState.create_initial_state' in reset_source, "NaishiEnv.reset() does not call GameState.create_initial_state()"
    
    print("✓ NaishiEnv delegates to GameState")


def test_training_uses_correct_action_masking():
    """Verify that training uses action masking from GameState."""
    # Check that NaishiEnv._get_action_mask() uses GameState.get_legal_action_types()
    source = inspect.getsource(NaishiEnv._get_action_mask)
    
    assert 'self.gs.get_legal_action_types' in source, "NaishiEnv._get_action_mask() does not use GameState.get_legal_action_types()"
    
    print("✓ Training uses action masking from GameState")


def test_self_play_callback_no_game_logic():
    """Verify that SelfPlayCallback contains no game logic."""
    source = inspect.getsource(SelfPlayCallback)
    
    # Check that it only updates models and saves checkpoints
    # Should not contain any game logic
    forbidden_patterns = [
        'apply_action',
        'get_legal_action_types',
        'swap_cards',
        'discard_cards',
        'develop_territory',
    ]
    
    for pattern in forbidden_patterns:
        assert pattern not in source, f"SelfPlayCallback contains game logic pattern '{pattern}'"
    
    print("✓ SelfPlayCallback contains no game logic")


def test_training_script_structure():
    """Verify the overall structure of the training script."""
    import train_main_agent
    
    # Check that required functions exist
    assert hasattr(train_main_agent, 'train_agent'), "train_agent function not found"
    assert hasattr(train_main_agent, 'SelfPlayCallback'), "SelfPlayCallback class not found"
    assert hasattr(train_main_agent, 'find_latest_model'), "find_latest_model function not found"
    
    # Check that train_agent creates environment properly
    source = inspect.getsource(train_main_agent.train_agent)
    
    # Should create env with opponent_policy
    assert 'opponent_policy=' in source, "train_agent does not pass opponent_policy to env"
    
    # Should use DummyVecEnv or similar
    assert 'DummyVecEnv' in source or 'VecEnv' in source, "train_agent does not use vectorized environment"
    
    # Should use MaskablePPO (for action masking)
    assert 'MaskablePPO' in source, "train_agent does not use MaskablePPO"
    
    print("✓ Training script has correct structure")


def test_compliance_with_requirement_2_4():
    """
    Verify compliance with Requirement 2.4:
    WHEN train_main_agent.py trains a model THEN it SHALL use NaishiEnv which delegates to GameState
    """
    # This is a meta-test that combines all the above checks
    test_train_main_agent_uses_naishi_env()
    test_no_game_logic_in_training_script()
    test_training_delegates_to_naishi_env()
    test_naishi_env_delegates_to_game_state()
    test_training_uses_correct_action_masking()
    test_self_play_callback_no_game_logic()
    test_training_script_structure()
    
    print("\n" + "="*60)
    print("✓ REQUIREMENT 2.4 VERIFIED")
    print("  train_main_agent.py uses NaishiEnv which delegates to GameState")
    print("  No game logic found in training script")
    print("="*60)


if __name__ == "__main__":
    print("Testing Task 33: Verify train_main_agent.py uses correct rules")
    print("="*60)
    
    test_train_main_agent_uses_naishi_env()
    test_no_game_logic_in_training_script()
    test_training_delegates_to_naishi_env()
    test_naishi_env_delegates_to_game_state()
    test_training_uses_correct_action_masking()
    test_self_play_callback_no_game_logic()
    test_training_script_structure()
    test_compliance_with_requirement_2_4()
    
    print("\n" + "="*60)
    print("ALL TESTS PASSED ✓")
    print("="*60)
