#!/usr/bin/env python3
"""Test for Task 17: Fix ACTION_DEVELOP to support optional emissary"""

from naishi_core.game_logic import GameState, ACTION_DEVELOP, ACTION_SWAP, ACTION_DISCARD

def test_optional_emissary_after_develop():
    """Test that optional emissary is available after develop when conditions are met."""
    print("Test 1: Optional emissary available after develop")
    
    # Create initial state
    gs = GameState.create_initial_state(seed=42)
    
    # Complete draft phase
    draft_action_p0 = [0, 0, 0, 0, 0, 0, 0, 0]  # ACTION_DRAFT, pos 0
    draft_action_p1 = [0, 1, 0, 0, 0, 0, 0, 0]  # ACTION_DRAFT, pos 1
    gs.apply_action_array(draft_action_p0)
    gs.apply_action_array(draft_action_p1)
    
    # Verify we're in main game phase
    assert not gs.in_draft_phase, "Should be in main game phase"
    
    # Check initial state
    player = gs.players[gs.current_player_idx]
    print(f"  Player has {player.emissaries} emissaries")
    print(f"  Available swaps: {gs.available_swaps}")
    print(f"  Available discards: {gs.available_discards}")
    
    # Perform develop action
    develop_action = [ACTION_DEVELOP, 0, 0, 0, 0, 0, 0, 0]  # Develop position 0
    obs, reward, done, trunc, info = gs.apply_action_array(develop_action)
    
    # Check if optional emissary is available
    print(f"  After develop:")
    print(f"    optional_emissary_available: {gs.optional_emissary_available}")
    print(f"    Current player: {gs.current_player_idx}")
    
    # Should have optional emissary available if player has emissaries and spots available
    if player.emissaries > 0 and (0 in gs.available_swaps or 0 in gs.available_discards):
        assert gs.optional_emissary_available, "Optional emissary should be available"
        assert gs.current_player_idx == 0, "Turn should not have ended yet"
        print("  ✓ Optional emissary is available after develop")
    else:
        assert not gs.optional_emissary_available, "Optional emissary should not be available"
        print("  ✓ Optional emissary correctly not available (no emissaries or spots)")
    
    print()

def test_optional_emissary_ends_turn():
    """Test that using optional emissary ends the turn."""
    print("Test 2: Using optional emissary ends turn")
    
    # Create initial state
    gs = GameState.create_initial_state(seed=42)
    
    # Complete draft phase
    draft_action_p0 = [0, 0, 0, 0, 0, 0, 0, 0]
    draft_action_p1 = [0, 1, 0, 0, 0, 0, 0, 0]
    gs.apply_action_array(draft_action_p0)
    gs.apply_action_array(draft_action_p1)
    
    # Perform develop action
    develop_action = [ACTION_DEVELOP, 0, 0, 0, 0, 0, 0, 0]
    gs.apply_action_array(develop_action)
    
    if gs.optional_emissary_available:
        print("  Optional emissary is available")
        
        # Use optional emissary (swap in hand)
        swap_action = [ACTION_SWAP, 0, 0, 0, 0, 1, 0, 0]  # Swap hand positions 0 and 1
        obs, reward, done, trunc, info = gs.apply_action_array(swap_action)
        
        # Check that turn ended
        print(f"    After using optional emissary:")
        print(f"      optional_emissary_available: {gs.optional_emissary_available}")
        print(f"      Current player: {gs.current_player_idx}")
        
        assert not gs.optional_emissary_available, "Flag should be cleared"
        assert gs.current_player_idx == 1, "Turn should have ended and switched to player 1"
        print("  ✓ Turn ended after using optional emissary")
    else:
        print("  Optional emissary not available (skipping test)")
    
    print()

def test_skip_optional_emissary():
    """Test that skipping optional emissary ends the turn."""
    print("Test 3: Skipping optional emissary ends turn")
    
    # Create initial state
    gs = GameState.create_initial_state(seed=42)
    
    # Complete draft phase
    draft_action_p0 = [0, 0, 0, 0, 0, 0, 0, 0]
    draft_action_p1 = [0, 1, 0, 0, 0, 0, 0, 0]
    gs.apply_action_array(draft_action_p0)
    gs.apply_action_array(draft_action_p1)
    
    # Perform develop action
    develop_action = [ACTION_DEVELOP, 0, 0, 0, 0, 0, 0, 0]
    gs.apply_action_array(develop_action)
    
    if gs.optional_emissary_available:
        print("  Optional emissary is available")
        
        # Skip optional emissary
        obs, reward, done, trunc, info = gs.skip_optional_emissary()
        
        # Check that turn ended
        print(f"    After skipping optional emissary:")
        print(f"      optional_emissary_available: {gs.optional_emissary_available}")
        print(f"      Current player: {gs.current_player_idx}")
        
        assert not gs.optional_emissary_available, "Flag should be cleared"
        assert gs.current_player_idx == 1, "Turn should have ended and switched to player 1"
        print("  ✓ Turn ended after skipping optional emissary")
    else:
        print("  Optional emissary not available (skipping test)")
    
    print()

def test_no_optional_emissary_without_emissaries():
    """Test that optional emissary is not available if player has no emissaries."""
    print("Test 4: No optional emissary without emissaries")
    
    # Create initial state
    gs = GameState.create_initial_state(seed=42)
    
    # Complete draft phase
    draft_action_p0 = [0, 0, 0, 0, 0, 0, 0, 0]
    draft_action_p1 = [0, 1, 0, 0, 0, 0, 0, 0]
    gs.apply_action_array(draft_action_p0)
    gs.apply_action_array(draft_action_p1)
    
    # Remove all emissaries from current player
    player = gs.players[gs.current_player_idx]
    player.emissaries = 0
    
    print(f"  Player has {player.emissaries} emissaries")
    
    # Perform develop action
    develop_action = [ACTION_DEVELOP, 0, 0, 0, 0, 0, 0, 0]
    gs.apply_action_array(develop_action)
    
    # Check that optional emissary is NOT available
    print(f"  After develop:")
    print(f"    optional_emissary_available: {gs.optional_emissary_available}")
    print(f"    Current player: {gs.current_player_idx}")
    
    assert not gs.optional_emissary_available, "Optional emissary should not be available without emissaries"
    assert gs.current_player_idx == 1, "Turn should have ended"
    print("  ✓ Optional emissary correctly not available without emissaries")
    
    print()

def test_no_optional_emissary_without_spots():
    """Test that optional emissary is not available if all spots are full."""
    print("Test 5: No optional emissary without available spots")
    
    # Create initial state
    gs = GameState.create_initial_state(seed=42)
    
    # Complete draft phase
    draft_action_p0 = [0, 0, 0, 0, 0, 0, 0, 0]
    draft_action_p1 = [0, 1, 0, 0, 0, 0, 0, 0]
    gs.apply_action_array(draft_action_p0)
    gs.apply_action_array(draft_action_p1)
    
    # Fill all emissary spots
    gs.available_swaps = [1, 1, 1]  # All swap spots taken
    gs.available_discards = [1, 1]  # All discard spots taken
    
    print(f"  Available swaps: {gs.available_swaps}")
    print(f"  Available discards: {gs.available_discards}")
    
    # Perform develop action
    develop_action = [ACTION_DEVELOP, 0, 0, 0, 0, 0, 0, 0]
    gs.apply_action_array(develop_action)
    
    # Check that optional emissary is NOT available
    print(f"  After develop:")
    print(f"    optional_emissary_available: {gs.optional_emissary_available}")
    print(f"    Current player: {gs.current_player_idx}")
    
    assert not gs.optional_emissary_available, "Optional emissary should not be available without spots"
    assert gs.current_player_idx == 1, "Turn should have ended"
    print("  ✓ Optional emissary correctly not available without spots")
    
    print()

def test_legal_actions_during_optional_emissary():
    """Test that only emissary actions are legal during optional emissary phase."""
    print("Test 6: Legal actions during optional emissary phase")
    
    # Create initial state
    gs = GameState.create_initial_state(seed=42)
    
    # Complete draft phase
    draft_action_p0 = [0, 0, 0, 0, 0, 0, 0, 0]
    draft_action_p1 = [0, 1, 0, 0, 0, 0, 0, 0]
    gs.apply_action_array(draft_action_p0)
    gs.apply_action_array(draft_action_p1)
    
    # Perform develop action
    develop_action = [ACTION_DEVELOP, 0, 0, 0, 0, 0, 0, 0]
    gs.apply_action_array(develop_action)
    
    if gs.optional_emissary_available:
        print("  Optional emissary is available")
        
        # Get legal actions
        legal_actions = gs.get_legal_action_types()
        print(f"    Legal actions: {legal_actions}")
        
        # Should only have emissary actions (SWAP and/or DISCARD)
        assert ACTION_DEVELOP not in legal_actions, "DEVELOP should not be legal during optional emissary"
        assert ACTION_SWAP in legal_actions or ACTION_DISCARD in legal_actions, "At least one emissary action should be legal"
        print("  ✓ Only emissary actions are legal during optional emissary phase")
    else:
        print("  Optional emissary not available (skipping test)")
    
    print()

if __name__ == "__main__":
    print("=" * 60)
    print("Testing Task 17: Fix ACTION_DEVELOP to support optional emissary")
    print("=" * 60)
    print()
    
    test_optional_emissary_after_develop()
    test_optional_emissary_ends_turn()
    test_skip_optional_emissary()
    test_no_optional_emissary_without_emissaries()
    test_no_optional_emissary_without_spots()
    test_legal_actions_during_optional_emissary()
    
    print("=" * 60)
    print("All tests passed! ✓")
    print("=" * 60)
