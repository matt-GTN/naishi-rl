#!/usr/bin/env python3
"""Test for Task 18: Fix ACTION_SWAP and ACTION_DISCARD to handle turn context"""

from naishi_core.game_logic import GameState, ACTION_DEVELOP, ACTION_SWAP, ACTION_DISCARD

def test_emissary_first_requires_develop():
    """Test that using emissary first (Option B) requires develop afterward."""
    print("Test 1: Emissary-first requires develop (Option B)")
    
    # Create initial state
    gs = GameState.create_initial_state(seed=42)
    
    # Complete draft phase
    draft_action_p0 = [0, 0, 0, 0, 0, 0, 0, 0]
    draft_action_p1 = [0, 1, 0, 0, 0, 0, 0, 0]
    gs.apply_action_array(draft_action_p0)
    gs.apply_action_array(draft_action_p1)
    
    # Verify initial state
    assert not gs.in_draft_phase, "Should be in main game phase"
    assert not gs.must_develop, "must_develop should be False initially"
    assert not gs.optional_emissary_available, "optional_emissary_available should be False initially"
    
    player = gs.players[gs.current_player_idx]
    print(f"  Player has {player.emissaries} emissaries")
    print(f"  Initial must_develop: {gs.must_develop}")
    
    # Use emissary first (swap in hand)
    swap_action = [ACTION_SWAP, 0, 0, 0, 0, 1, 0, 0]  # Swap hand positions 0 and 1
    obs, reward, done, trunc, info = gs.apply_action_array(swap_action)
    
    # Check that must_develop is set and turn hasn't ended
    print(f"  After emissary-first (SWAP):")
    print(f"    must_develop: {gs.must_develop}")
    print(f"    optional_emissary_available: {gs.optional_emissary_available}")
    print(f"    Current player: {gs.current_player_idx}")
    
    assert gs.must_develop, "must_develop should be True after emissary-first"
    assert not gs.optional_emissary_available, "optional_emissary_available should be False"
    assert gs.current_player_idx == 0, "Turn should not have ended yet"
    print("  ✓ Emissary-first correctly sets must_develop=True")
    
    # Verify only DEVELOP is legal
    legal_actions = gs.get_legal_action_types()
    print(f"  Legal actions: {legal_actions}")
    assert legal_actions == [ACTION_DEVELOP], "Only DEVELOP should be legal after emissary-first"
    print("  ✓ Only DEVELOP is legal after emissary-first")
    
    # Now perform required develop
    develop_action = [ACTION_DEVELOP, 1, 0, 0, 0, 0, 0, 0]
    obs, reward, done, trunc, info = gs.apply_action_array(develop_action)
    
    # Check that turn ended
    print(f"  After required develop:")
    print(f"    must_develop: {gs.must_develop}")
    print(f"    Current player: {gs.current_player_idx}")
    
    assert not gs.must_develop, "must_develop should be cleared after develop"
    assert gs.current_player_idx == 1, "Turn should have ended and switched to player 1"
    print("  ✓ Turn ended after required develop")
    
    print()

def test_discard_first_requires_develop():
    """Test that using discard first (Option B) requires develop afterward."""
    print("Test 2: Discard-first requires develop (Option B)")
    
    # Create initial state
    gs = GameState.create_initial_state(seed=43)
    
    # Complete draft phase
    draft_action_p0 = [0, 0, 0, 0, 0, 0, 0, 0]
    draft_action_p1 = [0, 1, 0, 0, 0, 0, 0, 0]
    gs.apply_action_array(draft_action_p0)
    gs.apply_action_array(draft_action_p1)
    
    player = gs.players[gs.current_player_idx]
    print(f"  Player has {player.emissaries} emissaries")
    print(f"  Initial must_develop: {gs.must_develop}")
    
    # Use emissary first (discard)
    discard_action = [ACTION_DISCARD, 0, 0, 0, 0, 0, 0, 1]  # Discard from decks 0 and 1
    obs, reward, done, trunc, info = gs.apply_action_array(discard_action)
    
    # Check that must_develop is set and turn hasn't ended
    print(f"  After emissary-first (DISCARD):")
    print(f"    must_develop: {gs.must_develop}")
    print(f"    optional_emissary_available: {gs.optional_emissary_available}")
    print(f"    Current player: {gs.current_player_idx}")
    
    assert gs.must_develop, "must_develop should be True after emissary-first"
    assert not gs.optional_emissary_available, "optional_emissary_available should be False"
    assert gs.current_player_idx == 0, "Turn should not have ended yet"
    print("  ✓ Discard-first correctly sets must_develop=True")
    
    # Now perform required develop
    develop_action = [ACTION_DEVELOP, 2, 0, 0, 0, 0, 0, 0]
    obs, reward, done, trunc, info = gs.apply_action_array(develop_action)
    
    # Check that turn ended
    print(f"  After required develop:")
    print(f"    must_develop: {gs.must_develop}")
    print(f"    Current player: {gs.current_player_idx}")
    
    assert not gs.must_develop, "must_develop should be cleared after develop"
    assert gs.current_player_idx == 1, "Turn should have ended and switched to player 1"
    print("  ✓ Turn ended after required develop")
    
    print()

def test_optional_swap_ends_turn():
    """Test that using optional swap after develop (Option A) ends the turn."""
    print("Test 3: Optional swap after develop ends turn (Option A)")
    
    # Create initial state
    gs = GameState.create_initial_state(seed=44)
    
    # Complete draft phase
    draft_action_p0 = [0, 0, 0, 0, 0, 0, 0, 0]
    draft_action_p1 = [0, 1, 0, 0, 0, 0, 0, 0]
    gs.apply_action_array(draft_action_p0)
    gs.apply_action_array(draft_action_p1)
    
    player = gs.players[gs.current_player_idx]
    print(f"  Player has {player.emissaries} emissaries")
    
    # Develop first
    develop_action = [ACTION_DEVELOP, 0, 0, 0, 0, 0, 0, 0]
    obs, reward, done, trunc, info = gs.apply_action_array(develop_action)
    
    print(f"  After develop:")
    print(f"    optional_emissary_available: {gs.optional_emissary_available}")
    print(f"    must_develop: {gs.must_develop}")
    
    if gs.optional_emissary_available:
        print("  Optional emissary is available")
        
        # Use optional swap
        swap_action = [ACTION_SWAP, 0, 0, 0, 0, 1, 0, 0]
        obs, reward, done, trunc, info = gs.apply_action_array(swap_action)
        
        # Check that turn ended
        print(f"  After optional swap:")
        print(f"    optional_emissary_available: {gs.optional_emissary_available}")
        print(f"    must_develop: {gs.must_develop}")
        print(f"    Current player: {gs.current_player_idx}")
        
        assert not gs.optional_emissary_available, "optional_emissary_available should be cleared"
        assert not gs.must_develop, "must_develop should remain False"
        assert gs.current_player_idx == 1, "Turn should have ended and switched to player 1"
        print("  ✓ Turn ended after optional swap")
    else:
        print("  Optional emissary not available (skipping test)")
    
    print()

def test_optional_discard_ends_turn():
    """Test that using optional discard after develop (Option A) ends the turn."""
    print("Test 4: Optional discard after develop ends turn (Option A)")
    
    # Create initial state
    gs = GameState.create_initial_state(seed=45)
    
    # Complete draft phase
    draft_action_p0 = [0, 0, 0, 0, 0, 0, 0, 0]
    draft_action_p1 = [0, 1, 0, 0, 0, 0, 0, 0]
    gs.apply_action_array(draft_action_p0)
    gs.apply_action_array(draft_action_p1)
    
    player = gs.players[gs.current_player_idx]
    print(f"  Player has {player.emissaries} emissaries")
    
    # Develop first
    develop_action = [ACTION_DEVELOP, 1, 0, 0, 0, 0, 0, 0]
    obs, reward, done, trunc, info = gs.apply_action_array(develop_action)
    
    print(f"  After develop:")
    print(f"    optional_emissary_available: {gs.optional_emissary_available}")
    print(f"    must_develop: {gs.must_develop}")
    
    if gs.optional_emissary_available:
        print("  Optional emissary is available")
        
        # Use optional discard
        discard_action = [ACTION_DISCARD, 0, 0, 0, 0, 0, 0, 1]
        obs, reward, done, trunc, info = gs.apply_action_array(discard_action)
        
        # Check that turn ended
        print(f"  After optional discard:")
        print(f"    optional_emissary_available: {gs.optional_emissary_available}")
        print(f"    must_develop: {gs.must_develop}")
        print(f"    Current player: {gs.current_player_idx}")
        
        assert not gs.optional_emissary_available, "optional_emissary_available should be cleared"
        assert not gs.must_develop, "must_develop should remain False"
        assert gs.current_player_idx == 1, "Turn should have ended and switched to player 1"
        print("  ✓ Turn ended after optional discard")
    else:
        print("  Optional emissary not available (skipping test)")
    
    print()

def test_turn_context_detection():
    """Test that the system correctly detects optional vs emissary-first context."""
    print("Test 5: Turn context detection")
    
    # Create initial state
    gs = GameState.create_initial_state(seed=46)
    
    # Complete draft phase
    draft_action_p0 = [0, 0, 0, 0, 0, 0, 0, 0]
    draft_action_p1 = [0, 1, 0, 0, 0, 0, 0, 0]
    gs.apply_action_array(draft_action_p0)
    gs.apply_action_array(draft_action_p1)
    
    # Test 1: Emissary-first context
    print("  Scenario 1: Emissary-first (no optional_emissary_available flag)")
    assert not gs.optional_emissary_available, "Flag should be False initially"
    
    swap_action = [ACTION_SWAP, 0, 0, 0, 0, 1, 0, 0]
    gs.apply_action_array(swap_action)
    
    assert gs.must_develop, "Should set must_develop=True in emissary-first context"
    assert not gs.optional_emissary_available, "Flag should remain False"
    print("    ✓ Correctly detected emissary-first context")
    
    # Complete the required develop to reset state
    develop_action = [ACTION_DEVELOP, 0, 0, 0, 0, 0, 0, 0]
    gs.apply_action_array(develop_action)
    
    # Now we're on player 1's turn
    print("  Scenario 2: Optional emissary context (optional_emissary_available flag set)")
    
    # Develop first to set optional_emissary_available
    develop_action = [ACTION_DEVELOP, 0, 0, 0, 0, 0, 0, 0]
    gs.apply_action_array(develop_action)
    
    if gs.optional_emissary_available:
        print(f"    optional_emissary_available: {gs.optional_emissary_available}")
        
        # Use optional swap
        swap_action = [ACTION_SWAP, 0, 0, 0, 0, 1, 0, 0]
        gs.apply_action_array(swap_action)
        
        assert not gs.optional_emissary_available, "Should clear flag in optional context"
        assert not gs.must_develop, "Should not set must_develop in optional context"
        print("    ✓ Correctly detected optional emissary context")
    else:
        print("    Optional emissary not available (player may have no emissaries/spots)")
    
    print()

def test_multiple_turns_with_different_options():
    """Test multiple turns using different turn options."""
    print("Test 6: Multiple turns with different options")
    
    # Create initial state
    gs = GameState.create_initial_state(seed=47)
    
    # Complete draft phase
    draft_action_p0 = [0, 0, 0, 0, 0, 0, 0, 0]
    draft_action_p1 = [0, 1, 0, 0, 0, 0, 0, 0]
    gs.apply_action_array(draft_action_p0)
    gs.apply_action_array(draft_action_p1)
    
    # Turn 1: Player 0 uses Option A (develop → optional emissary)
    print("  Turn 1 (P0): Option A - Develop → Optional Emissary")
    develop_action = [ACTION_DEVELOP, 0, 0, 0, 0, 0, 0, 0]
    gs.apply_action_array(develop_action)
    
    if gs.optional_emissary_available:
        swap_action = [ACTION_SWAP, 0, 0, 0, 0, 1, 0, 0]
        gs.apply_action_array(swap_action)
        assert gs.current_player_idx == 1, "Should be player 1's turn"
        print("    ✓ Option A completed successfully")
    else:
        # Skip if not available
        gs.skip_optional_emissary()
        print("    ✓ Develop completed (no optional emissary available)")
    
    # Turn 2: Player 1 uses Option B (emissary → required develop)
    print("  Turn 2 (P1): Option B - Emissary → Required Develop")
    swap_action = [ACTION_SWAP, 0, 0, 0, 1, 2, 0, 0]
    gs.apply_action_array(swap_action)
    assert gs.must_develop, "must_develop should be True"
    
    develop_action = [ACTION_DEVELOP, 1, 0, 0, 0, 0, 0, 0]
    gs.apply_action_array(develop_action)
    assert gs.current_player_idx == 0, "Should be player 0's turn"
    print("    ✓ Option B completed successfully")
    
    # Turn 3: Player 0 uses Option A again but skips optional emissary
    print("  Turn 3 (P0): Option A - Develop → Skip Optional Emissary")
    develop_action = [ACTION_DEVELOP, 2, 0, 0, 0, 0, 0, 0]
    gs.apply_action_array(develop_action)
    
    if gs.optional_emissary_available:
        gs.skip_optional_emissary()
        assert gs.current_player_idx == 1, "Should be player 1's turn"
        print("    ✓ Skipped optional emissary successfully")
    else:
        assert gs.current_player_idx == 1, "Should be player 1's turn"
        print("    ✓ Develop completed (no optional emissary available)")
    
    print()

if __name__ == "__main__":
    print("=" * 70)
    print("Testing Task 18: Fix ACTION_SWAP and ACTION_DISCARD turn context")
    print("=" * 70)
    print()
    
    test_emissary_first_requires_develop()
    test_discard_first_requires_develop()
    test_optional_swap_ends_turn()
    test_optional_discard_ends_turn()
    test_turn_context_detection()
    test_multiple_turns_with_different_options()
    
    print("=" * 70)
    print("All tests passed! ✓")
    print("=" * 70)
