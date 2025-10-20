#!/usr/bin/env python3
"""
Test Task 31: Verify play_vs_ai.py has no game logic
Tests that play_vs_ai.py purely delegates to GameState
"""

import ast
import inspect


def test_no_action_validation():
    """Verify play_vs_ai.py doesn't validate actions itself"""
    from play_vs_ai import PlayVsAI
    
    # Check that PlayVsAI doesn't have methods that validate actions
    methods = [m for m in dir(PlayVsAI) if not m.startswith('_') and callable(getattr(PlayVsAI, m))]
    
    # Should not have validation methods
    forbidden_methods = ['validate_action', 'is_legal', 'check_action', 'verify_action']
    for method in forbidden_methods:
        assert method not in methods, f"Found forbidden validation method: {method}"
    
    print("✓ No action validation methods found")


def test_no_emissary_spot_management():
    """Verify play_vs_ai.py doesn't manage emissary spots"""
    import play_vs_ai
    
    # Read source code
    source = inspect.getsource(play_vs_ai)
    
    # Should not have emissary spot management logic
    forbidden_patterns = [
        'emissary_spots',
        'spots_used',
        'available_spots',
        'mark_spot',
        'clear_spots'
    ]
    
    for pattern in forbidden_patterns:
        assert pattern not in source, f"Found forbidden emissary management: {pattern}"
    
    # Should query GameState instead
    assert 'gs.optional_emissary_available' in source, "Should query GameState for optional emissary"
    assert 'gs.must_develop' in source, "Should query GameState for must_develop"
    
    print("✓ No emissary spot management found")
    print("✓ Queries GameState for turn state")


def test_no_player_switching():
    """Verify play_vs_ai.py doesn't switch players"""
    import play_vs_ai
    
    source = inspect.getsource(play_vs_ai)
    
    # Should not have player switching logic
    forbidden_patterns = [
        'current_player = ',
        'switch_player',
        'next_player',
        'toggle_player'
    ]
    
    for pattern in forbidden_patterns:
        assert pattern not in source, f"Found forbidden player switching: {pattern}"
    
    # Should use GameState's current_player_idx
    assert 'gs.current_player_idx' in source, "Should use GameState's current_player_idx"
    
    print("✓ No player switching found")
    print("✓ Uses GameState's current_player_idx")


def test_no_ending_checks():
    """Verify play_vs_ai.py doesn't check game ending"""
    import play_vs_ai
    
    source = inspect.getsource(play_vs_ai)
    
    # Should not have game ending logic
    forbidden_patterns = [
        'check_game_over',
        'is_game_over',
        'game_ended',
        'count.*empty.*deck'
    ]
    
    for pattern in forbidden_patterns:
        # Use simple string matching for most patterns
        if '*' not in pattern:
            assert pattern not in source, f"Found forbidden ending check: {pattern}"
    
    # Should use terminated/truncated from GameState
    assert 'terminated' in source, "Should use terminated from GameState"
    assert 'truncated' in source, "Should use truncated from GameState"
    
    print("✓ No game ending checks found")
    print("✓ Uses terminated/truncated from GameState")


def test_pure_delegation():
    """Verify play_vs_ai.py delegates all logic to GameState"""
    import play_vs_ai
    
    source = inspect.getsource(play_vs_ai)
    
    # Should delegate to GameState
    required_delegations = [
        'gs.apply_action_array',
        'gs.get_legal_action_types',
        'gs.optional_emissary_available',
        'gs.must_develop',
        'gs.skip_optional_emissary'
    ]
    
    for delegation in required_delegations:
        assert delegation in source, f"Missing required delegation: {delegation}"
    
    print("✓ All required delegations to GameState found")


def test_offer_optional_emissary_no_logic():
    """Verify _offer_optional_emissary has no game logic checks"""
    from play_vs_ai import PlayVsAI
    
    # Get source of the method
    source = inspect.getsource(PlayVsAI._offer_optional_emissary)
    
    # Should not check player.emissaries
    assert 'player.emissaries' not in source, "Should not check player.emissaries"
    
    # Should not check legal_types
    assert 'get_legal_action_types' not in source, "Should not call get_legal_action_types"
    
    # Should not check has_emissary_actions
    assert 'has_emissary_actions' not in source, "Should not check has_emissary_actions"
    
    # Should only present UI and get choice
    assert 'get_choice' in source, "Should use get_choice for UI"
    
    print("✓ _offer_optional_emissary has no game logic")
    print("✓ Pure UI presentation only")


def test_integration_pure_delegation():
    """Integration test: Verify play_vs_ai works with pure delegation"""
    from play_vs_ai import PlayVsAI
    from naishi_core.game_logic import GameState
    
    # Create game
    game = PlayVsAI(seed=42)
    
    # Verify it uses GameState
    assert isinstance(game.gs, GameState), "Should use GameState"
    
    # Verify no duplicate state
    assert not hasattr(game, 'current_player'), "Should not have current_player"
    assert not hasattr(game, 'emissary_spots'), "Should not have emissary_spots"
    assert not hasattr(game, 'game_over'), "Should not have game_over"
    
    print("✓ PlayVsAI uses pure delegation")
    print("✓ No duplicate state management")


if __name__ == '__main__':
    print("Testing Task 31: Remove game logic from play_vs_ai.py\n")
    
    test_no_action_validation()
    test_no_emissary_spot_management()
    test_no_player_switching()
    test_no_ending_checks()
    test_pure_delegation()
    test_offer_optional_emissary_no_logic()
    test_integration_pure_delegation()
    
    print("\n" + "="*60)
    print("✅ All Task 31 tests passed!")
    print("="*60)
    print("\nSummary:")
    print("- No action validation in play_vs_ai.py")
    print("- No emissary spot management")
    print("- No player switching")
    print("- No ending checks")
    print("- Pure delegation to GameState")
    print("- _offer_optional_emissary has no game logic")
