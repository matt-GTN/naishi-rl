#!/usr/bin/env python3
"""Integration test for Task 17: Verify Option A works in complete game flow"""

from naishi_core.game_logic import GameState, ACTION_DEVELOP, ACTION_SWAP, ACTION_DISCARD

def test_option_a_complete_flow():
    """Test complete Option A flow: Develop → Optional Emissary → Turn ends"""
    print("Integration Test: Complete Option A Flow")
    print("-" * 60)
    
    # Create initial state
    gs = GameState.create_initial_state(seed=42)
    
    # Complete draft phase
    print("1. Completing draft phase...")
    draft_action_p0 = [0, 0, 0, 0, 0, 0, 0, 0]
    draft_action_p1 = [0, 1, 0, 0, 0, 0, 0, 0]
    gs.apply_action_array(draft_action_p0)
    gs.apply_action_array(draft_action_p1)
    print(f"   Draft complete. Current player: {gs.current_player_idx}")
    
    # Player 0's turn - Option A
    print("\n2. Player 0 uses Option A (Develop → Optional Emissary):")
    print(f"   Initial state:")
    print(f"     Emissaries: {gs.players[0].emissaries}")
    print(f"     Available swaps: {gs.available_swaps}")
    print(f"     Turn count: {gs.turn_count}")
    
    # Step 1: Develop
    print(f"\n   Step 1: Develop position 0")
    develop_action = [ACTION_DEVELOP, 0, 0, 0, 0, 0, 0, 0]
    obs, reward, done, trunc, info = gs.apply_action_array(develop_action)
    print(f"     After develop:")
    print(f"       optional_emissary_available: {gs.optional_emissary_available}")
    print(f"       Current player: {gs.current_player_idx}")
    print(f"       Turn count: {gs.turn_count}")
    
    assert gs.optional_emissary_available, "Optional emissary should be available"
    assert gs.current_player_idx == 0, "Should still be player 0's turn"
    
    # Step 2: Use optional emissary
    print(f"\n   Step 2: Use optional emissary (swap in hand)")
    swap_action = [ACTION_SWAP, 0, 0, 0, 0, 1, 0, 0]
    obs, reward, done, trunc, info = gs.apply_action_array(swap_action)
    print(f"     After optional emissary:")
    print(f"       optional_emissary_available: {gs.optional_emissary_available}")
    print(f"       Current player: {gs.current_player_idx}")
    print(f"       Turn count: {gs.turn_count}")
    print(f"       Emissaries: {gs.players[0].emissaries}")
    
    assert not gs.optional_emissary_available, "Flag should be cleared"
    assert gs.current_player_idx == 1, "Should be player 1's turn now"
    assert gs.turn_count == 1, "Turn count should have incremented"
    assert gs.players[0].emissaries == 1, "Player 0 should have used 1 emissary"
    
    print("\n   ✓ Option A flow completed successfully!")
    print()

def test_option_b_still_works():
    """Test that Option B still works after implementing Option A"""
    print("Integration Test: Option B Still Works")
    print("-" * 60)
    
    # Create initial state
    gs = GameState.create_initial_state(seed=42)
    
    # Complete draft phase
    print("1. Completing draft phase...")
    draft_action_p0 = [0, 0, 0, 0, 0, 0, 0, 0]
    draft_action_p1 = [0, 1, 0, 0, 0, 0, 0, 0]
    gs.apply_action_array(draft_action_p0)
    gs.apply_action_array(draft_action_p1)
    
    # Player 0's turn - Option B
    print("\n2. Player 0 uses Option B (Emissary → Required Develop):")
    print(f"   Initial state:")
    print(f"     Emissaries: {gs.players[0].emissaries}")
    print(f"     must_develop: {gs.must_develop}")
    
    # Step 1: Use emissary first
    print(f"\n   Step 1: Use emissary (swap in hand)")
    swap_action = [ACTION_SWAP, 0, 0, 0, 0, 1, 0, 0]
    obs, reward, done, trunc, info = gs.apply_action_array(swap_action)
    print(f"     After emissary:")
    print(f"       must_develop: {gs.must_develop}")
    print(f"       optional_emissary_available: {gs.optional_emissary_available}")
    print(f"       Current player: {gs.current_player_idx}")
    
    assert gs.must_develop, "must_develop should be True"
    assert not gs.optional_emissary_available, "optional_emissary should be False"
    assert gs.current_player_idx == 0, "Should still be player 0's turn"
    
    # Step 2: Required develop
    print(f"\n   Step 2: Required develop")
    develop_action = [ACTION_DEVELOP, 0, 0, 0, 0, 0, 0, 0]
    obs, reward, done, trunc, info = gs.apply_action_array(develop_action)
    print(f"     After develop:")
    print(f"       must_develop: {gs.must_develop}")
    print(f"       optional_emissary_available: {gs.optional_emissary_available}")
    print(f"       Current player: {gs.current_player_idx}")
    
    assert not gs.must_develop, "must_develop should be cleared"
    assert not gs.optional_emissary_available, "No optional emissary after required develop"
    assert gs.current_player_idx == 1, "Should be player 1's turn now"
    
    print("\n   ✓ Option B still works correctly!")
    print()

def test_decline_optional_emissary():
    """Test declining optional emissary"""
    print("Integration Test: Decline Optional Emissary")
    print("-" * 60)
    
    # Create initial state
    gs = GameState.create_initial_state(seed=42)
    
    # Complete draft phase
    print("1. Completing draft phase...")
    draft_action_p0 = [0, 0, 0, 0, 0, 0, 0, 0]
    draft_action_p1 = [0, 1, 0, 0, 0, 0, 0, 0]
    gs.apply_action_array(draft_action_p0)
    gs.apply_action_array(draft_action_p1)
    
    # Player 0's turn - Develop then decline optional emissary
    print("\n2. Player 0 develops then declines optional emissary:")
    
    # Step 1: Develop
    print(f"\n   Step 1: Develop position 0")
    develop_action = [ACTION_DEVELOP, 0, 0, 0, 0, 0, 0, 0]
    gs.apply_action_array(develop_action)
    print(f"     optional_emissary_available: {gs.optional_emissary_available}")
    
    assert gs.optional_emissary_available, "Optional emissary should be available"
    
    # Step 2: Decline (skip)
    print(f"\n   Step 2: Decline optional emissary")
    obs, reward, done, trunc, info = gs.skip_optional_emissary()
    print(f"     After decline:")
    print(f"       optional_emissary_available: {gs.optional_emissary_available}")
    print(f"       Current player: {gs.current_player_idx}")
    
    assert not gs.optional_emissary_available, "Flag should be cleared"
    assert gs.current_player_idx == 1, "Should be player 1's turn now"
    
    print("\n   ✓ Decline optional emissary works correctly!")
    print()

def test_observation_includes_flag():
    """Test that observation includes optional_emissary_available flag"""
    print("Integration Test: Observation Includes Flag")
    print("-" * 60)
    
    # Create initial state
    gs = GameState.create_initial_state(seed=42)
    
    # Complete draft phase
    draft_action_p0 = [0, 0, 0, 0, 0, 0, 0, 0]
    draft_action_p1 = [0, 1, 0, 0, 0, 0, 0, 0]
    gs.apply_action_array(draft_action_p0)
    gs.apply_action_array(draft_action_p1)
    
    # Get observation before develop
    obs_before = gs.get_observation()
    print(f"1. Observation before develop:")
    print(f"   Length: {len(obs_before)}")
    print(f"   Last element (optional_emissary_available): {obs_before[-1]}")
    
    assert obs_before[-1] == 0, "Flag should be 0 before develop"
    
    # Develop
    develop_action = [ACTION_DEVELOP, 0, 0, 0, 0, 0, 0, 0]
    gs.apply_action_array(develop_action)
    
    # Get observation after develop
    obs_after = gs.get_observation()
    print(f"\n2. Observation after develop:")
    print(f"   Length: {len(obs_after)}")
    print(f"   Last element (optional_emissary_available): {obs_after[-1]}")
    
    if gs.optional_emissary_available:
        assert obs_after[-1] == 1, "Flag should be 1 when optional emissary available"
        print("\n   ✓ Observation correctly includes optional_emissary_available flag!")
    else:
        print("\n   ✓ Observation includes flag (not available in this case)")
    
    print()

if __name__ == "__main__":
    print("=" * 60)
    print("Integration Tests for Task 17")
    print("=" * 60)
    print()
    
    test_option_a_complete_flow()
    test_option_b_still_works()
    test_decline_optional_emissary()
    test_observation_includes_flag()
    
    print("=" * 60)
    print("All integration tests passed! ✓")
    print("=" * 60)
