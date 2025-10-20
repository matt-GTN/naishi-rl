"""Test task 19: Enforce must_develop rule

This test verifies that:
1. When must_develop = True, only ACTION_DEVELOP is allowed
2. get_legal_action_types() returns only [ACTION_DEVELOP] when must_develop is True
3. The flag is cleared after develop completes
"""

import sys
import numpy as np
from naishi_core.game_logic import GameState, ACTION_DEVELOP, ACTION_SWAP, ACTION_DISCARD, ACTION_RECALL, ACTION_DECREE, ACTION_END_GAME


def test_must_develop_restricts_legal_actions():
    """Test that when must_develop=True, only ACTION_DEVELOP is legal."""
    print("\n=== Test: must_develop restricts legal actions ===")
    
    # Create a game state
    gs = GameState.create_initial_state(seed=42)
    
    # Complete draft phase
    gs.apply_action_array([0, 0, 0, 0, 0, 0, 0, 0])  # P0 draft
    gs.apply_action_array([0, 0, 0, 0, 0, 0, 0, 0])  # P1 draft
    
    # Verify we're in main game
    assert not gs.in_draft_phase, "Should be in main game"
    
    # Use emissary first (swap in hand) - this should set must_develop=True
    print("\n1. Using emissary first (swap in hand)...")
    legal_before = gs.get_legal_action_types()
    print(f"   Legal actions before emissary: {legal_before}")
    assert ACTION_SWAP in legal_before, "SWAP should be legal initially"
    
    # Perform swap action (swap_type=0 for hand swap, pos1=0, pos2=1)
    action = [ACTION_SWAP, 0, 0, 0, 0, 1, 0, 0]
    obs, reward, done, trunc, info = gs.apply_action_array(action)
    
    print(f"   must_develop after emissary: {gs.must_develop}")
    assert gs.must_develop == True, "must_develop should be True after emissary-first action"
    
    # Check legal actions - should only be DEVELOP
    legal_after = gs.get_legal_action_types()
    print(f"   Legal actions after emissary: {legal_after}")
    assert legal_after == [ACTION_DEVELOP], f"Only DEVELOP should be legal, got {legal_after}"
    
    # Verify other actions are not legal
    assert ACTION_SWAP not in legal_after, "SWAP should not be legal when must_develop=True"
    assert ACTION_DISCARD not in legal_after, "DISCARD should not be legal when must_develop=True"
    assert ACTION_RECALL not in legal_after, "RECALL should not be legal when must_develop=True"
    assert ACTION_DECREE not in legal_after, "DECREE should not be legal when must_develop=True"
    
    print("   ✓ Only ACTION_DEVELOP is legal when must_develop=True")
    
    # Now perform develop - this should clear must_develop
    print("\n2. Performing required develop...")
    develop_action = [ACTION_DEVELOP, 0, 0, 0, 0, 0, 0, 0]
    obs, reward, done, trunc, info = gs.apply_action_array(develop_action)
    
    print(f"   must_develop after develop: {gs.must_develop}")
    assert gs.must_develop == False, "must_develop should be False after develop completes"
    
    print("   ✓ must_develop flag cleared after develop")
    
    print("\n✓ Test passed: must_develop rule is properly enforced")


def test_is_legal_action_respects_must_develop():
    """Test that is_legal_action() respects must_develop flag."""
    print("\n=== Test: is_legal_action respects must_develop ===")
    
    # Create a game state
    gs = GameState.create_initial_state(seed=42)
    
    # Complete draft phase
    gs.apply_action_array([0, 0, 0, 0, 0, 0, 0, 0])  # P0 draft
    gs.apply_action_array([0, 0, 0, 0, 0, 0, 0, 0])  # P1 draft
    
    # Use emissary first to set must_develop=True
    action = [ACTION_SWAP, 0, 0, 0, 0, 1, 0, 0]
    gs.apply_action_array(action)
    
    assert gs.must_develop == True, "must_develop should be True"
    
    # Test that non-DEVELOP actions are illegal
    print("\n1. Testing illegal actions when must_develop=True...")
    
    swap_action = [ACTION_SWAP, 0, 0, 0, 0, 1, 0, 0]
    assert not gs.is_legal_action_array(swap_action), "SWAP should be illegal when must_develop=True"
    print("   ✓ SWAP is illegal")
    
    discard_action = [ACTION_DISCARD, 0, 0, 0, 0, 0, 0, 1]
    assert not gs.is_legal_action_array(discard_action), "DISCARD should be illegal when must_develop=True"
    print("   ✓ DISCARD is illegal")
    
    recall_action = [ACTION_RECALL, 0, 0, 0, 0, 0, 0, 0]
    assert not gs.is_legal_action_array(recall_action), "RECALL should be illegal when must_develop=True"
    print("   ✓ RECALL is illegal")
    
    decree_action = [ACTION_DECREE, 0, 0, 0, 0, 0, 0, 0]
    assert not gs.is_legal_action_array(decree_action), "DECREE should be illegal when must_develop=True"
    print("   ✓ DECREE is illegal")
    
    # Test that DEVELOP is legal
    print("\n2. Testing that DEVELOP is legal when must_develop=True...")
    develop_action = [ACTION_DEVELOP, 0, 0, 0, 0, 0, 0, 0]
    assert gs.is_legal_action_array(develop_action), "DEVELOP should be legal when must_develop=True"
    print("   ✓ DEVELOP is legal")
    
    print("\n✓ Test passed: is_legal_action respects must_develop flag")


def test_must_develop_cleared_after_develop():
    """Test that must_develop is cleared after develop completes."""
    print("\n=== Test: must_develop cleared after develop ===")
    
    # Create a game state
    gs = GameState.create_initial_state(seed=42)
    
    # Complete draft phase
    gs.apply_action_array([0, 0, 0, 0, 0, 0, 0, 0])  # P0 draft
    gs.apply_action_array([0, 0, 0, 0, 0, 0, 0, 0])  # P1 draft
    
    # Use emissary first to set must_develop=True
    print("\n1. Setting must_develop=True via emissary-first...")
    action = [ACTION_SWAP, 0, 0, 0, 0, 1, 0, 0]
    gs.apply_action_array(action)
    
    assert gs.must_develop == True, "must_develop should be True"
    print(f"   must_develop: {gs.must_develop}")
    
    # Perform develop
    print("\n2. Performing develop to clear flag...")
    develop_action = [ACTION_DEVELOP, 0, 0, 0, 0, 0, 0, 0]
    obs, reward, done, trunc, info = gs.apply_action_array(develop_action)
    
    print(f"   must_develop after develop: {gs.must_develop}")
    assert gs.must_develop == False, "must_develop should be False after develop"
    
    # Verify turn ended (player switched)
    print(f"   Turn ended: {gs.current_player_idx == 1}")
    assert gs.current_player_idx == 1, "Turn should have ended and switched to player 1"
    
    print("\n✓ Test passed: must_develop cleared after develop completes")


def test_illegal_action_penalty_when_must_develop():
    """Test that attempting illegal actions when must_develop=True results in penalty."""
    print("\n=== Test: Illegal action penalty when must_develop=True ===")
    
    # Create a game state
    gs = GameState.create_initial_state(seed=42)
    
    # Complete draft phase
    gs.apply_action_array([0, 0, 0, 0, 0, 0, 0, 0])  # P0 draft
    gs.apply_action_array([0, 0, 0, 0, 0, 0, 0, 0])  # P1 draft
    
    # Use emissary first to set must_develop=True
    action = [ACTION_SWAP, 0, 0, 0, 0, 1, 0, 0]
    gs.apply_action_array(action)
    
    assert gs.must_develop == True, "must_develop should be True"
    
    # Try to perform an illegal action (RECALL instead of DEVELOP)
    print("\n1. Attempting illegal RECALL action when must_develop=True...")
    recall_action = [ACTION_RECALL, 0, 0, 0, 0, 0, 0, 0]
    obs, reward, done, trunc, info = gs.apply_action_array(recall_action)
    
    print(f"   Reward: {reward}")
    assert reward == -0.1, f"Should receive penalty reward of -0.1, got {reward}"
    
    print("   ✓ Penalty applied for illegal action")
    
    print("\n✓ Test passed: Illegal actions penalized when must_develop=True")


def test_must_develop_with_discard():
    """Test must_develop rule with DISCARD action (not just SWAP)."""
    print("\n=== Test: must_develop with DISCARD action ===")
    
    # Create a game state
    gs = GameState.create_initial_state(seed=42)
    
    # Complete draft phase
    gs.apply_action_array([0, 0, 0, 0, 0, 0, 0, 0])  # P0 draft
    gs.apply_action_array([0, 0, 0, 0, 0, 0, 0, 0])  # P1 draft
    
    # Use emissary first with DISCARD - this should also set must_develop=True
    print("\n1. Using emissary first (discard)...")
    discard_action = [ACTION_DISCARD, 0, 0, 0, 0, 0, 0, 1]
    obs, reward, done, trunc, info = gs.apply_action_array(discard_action)
    
    print(f"   must_develop after discard: {gs.must_develop}")
    assert gs.must_develop == True, "must_develop should be True after discard-first action"
    
    # Check legal actions - should only be DEVELOP
    legal_after = gs.get_legal_action_types()
    print(f"   Legal actions after discard: {legal_after}")
    assert legal_after == [ACTION_DEVELOP], f"Only DEVELOP should be legal, got {legal_after}"
    
    print("   ✓ must_develop enforced after DISCARD action")
    
    # Perform develop to clear flag
    print("\n2. Performing required develop...")
    develop_action = [ACTION_DEVELOP, 0, 0, 0, 0, 0, 0, 0]
    gs.apply_action_array(develop_action)
    
    assert gs.must_develop == False, "must_develop should be False after develop"
    print("   ✓ must_develop cleared after develop")
    
    print("\n✓ Test passed: must_develop works with DISCARD action")


if __name__ == "__main__":
    print("=" * 60)
    print("Testing Task 19: Enforce must_develop rule")
    print("=" * 60)
    
    try:
        test_must_develop_restricts_legal_actions()
        test_is_legal_action_respects_must_develop()
        test_must_develop_cleared_after_develop()
        test_illegal_action_penalty_when_must_develop()
        test_must_develop_with_discard()
        
        print("\n" + "=" * 60)
        print("ALL TESTS PASSED ✓")
        print("=" * 60)
        print("\nTask 19 implementation verified:")
        print("  ✓ When must_develop=True, only ACTION_DEVELOP is allowed")
        print("  ✓ get_legal_action_types() returns only [ACTION_DEVELOP]")
        print("  ✓ is_legal_action() rejects non-DEVELOP actions")
        print("  ✓ Flag is cleared after develop completes")
        print("  ✓ Works with both SWAP and DISCARD emissary actions")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
