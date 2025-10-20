"""
Test Task 22: Verify Recall implementation compliance with RULES.md Section 5.3

This test verifies:
1. Emissary restoration logic (2 normal, 1 after decree)
2. Marker clearing (swap and discard spots)
3. Decree interaction
4. Legal action checks
"""

import sys
sys.path.insert(0, '.')

from naishi_core.game_logic import GameState, ACTION_RECALL, ACTION_SWAP, ACTION_DISCARD, ACTION_DECREE


def test_recall_restoration_normal():
    """Test that recall restores to 2 emissaries when no decree used"""
    print("\n=== Test 1: Recall Restoration (Normal) ===")
    
    gs = GameState.create_initial_state()
    gs.in_draft_phase = False
    
    # Set up player with 0 emissaries, no decree
    gs.players[0].emissaries = 0
    gs.players[0].decree_used = False
    
    print(f"Before recall - P0 emissaries: {gs.players[0].emissaries}, decree_used: {gs.players[0].decree_used}")
    
    action = {"type": ACTION_RECALL}
    gs.apply_action(action)
    
    print(f"After recall - P0 emissaries: {gs.players[0].emissaries}")
    
    assert gs.players[0].emissaries == 2, "Should restore to 2 emissaries without decree"
    print("✅ Recall restores to 2 emissaries (normal)")
    
    # Test from 1 emissary
    gs.players[1].emissaries = 1
    gs.players[1].decree_used = False
    gs.current_player_idx = 1
    
    print(f"\nBefore recall - P1 emissaries: {gs.players[1].emissaries}")
    action = {"type": ACTION_RECALL}
    gs.apply_action(action)
    print(f"After recall - P1 emissaries: {gs.players[1].emissaries}")
    
    assert gs.players[1].emissaries == 2, "Should restore from 1 to 2"
    print("✅ Recall restores from 1 to 2 emissaries")


def test_recall_restoration_after_decree():
    """Test that recall restores to 1 emissary when decree was used"""
    print("\n=== Test 2: Recall Restoration (After Decree) ===")
    
    gs = GameState.create_initial_state()
    gs.in_draft_phase = False
    
    # Set up player with 0 emissaries, decree used
    gs.players[0].emissaries = 0
    gs.players[0].decree_used = True
    
    print(f"Before recall - P0 emissaries: {gs.players[0].emissaries}, decree_used: {gs.players[0].decree_used}")
    
    action = {"type": ACTION_RECALL}
    gs.apply_action(action)
    
    print(f"After recall - P0 emissaries: {gs.players[0].emissaries}")
    
    assert gs.players[0].emissaries == 1, "Should restore to 1 emissary after decree"
    print("✅ Recall restores to 1 emissary (after decree)")


def test_recall_marker_clearing_swap():
    """Test that recall clears player's markers from swap spots"""
    print("\n=== Test 3: Marker Clearing (Swap Spots) ===")
    
    gs = GameState.create_initial_state()
    gs.in_draft_phase = False
    
    # Manually place markers on swap spots (player 0 = marker 1)
    gs.available_swaps[0] = 1  # P0 marker
    gs.available_swaps[1] = 1  # P0 marker
    gs.players[0].emissaries = 0  # Used emissaries
    
    print(f"Before recall - available_swaps: {gs.available_swaps}")
    print(f"P0 emissaries: {gs.players[0].emissaries}")
    
    # Verify markers are placed
    marker_count = sum(1 for spot in gs.available_swaps if spot == 1)
    assert marker_count == 2, "Should have 2 markers placed"
    print(f"✅ P0 has {marker_count} markers on swap spots")
    
    # Now recall
    gs.current_player_idx = 0
    action = {"type": ACTION_RECALL}
    gs.apply_action(action)
    
    print(f"After recall - available_swaps: {gs.available_swaps}")
    print(f"P0 emissaries: {gs.players[0].emissaries}")
    
    # Verify all P0 markers are cleared
    marker_count = sum(1 for spot in gs.available_swaps if spot == 1)
    assert marker_count == 0, "All P0 markers should be cleared"
    assert gs.players[0].emissaries == 2, "Emissaries should be restored"
    print("✅ All P0 swap markers cleared and emissaries restored")


def test_recall_marker_clearing_discard():
    """Test that recall clears player's markers from discard spots"""
    print("\n=== Test 4: Marker Clearing (Discard Spots) ===")
    
    gs = GameState.create_initial_state()
    gs.in_draft_phase = False
    
    # Manually place markers on discard spots (player 0 = marker 1)
    gs.available_discards[0] = 1  # P0 marker
    gs.available_discards[1] = 1  # P0 marker
    gs.players[0].emissaries = 0  # Used emissaries
    
    print(f"Before recall - available_discards: {gs.available_discards}")
    print(f"P0 emissaries: {gs.players[0].emissaries}")
    
    # Verify markers are placed
    marker_count = sum(1 for spot in gs.available_discards if spot == 1)
    assert marker_count == 2, "Should have 2 markers placed"
    print(f"✅ P0 has {marker_count} markers on discard spots")
    
    # Now recall
    gs.current_player_idx = 0
    action = {"type": ACTION_RECALL}
    gs.apply_action(action)
    
    print(f"After recall - available_discards: {gs.available_discards}")
    print(f"P0 emissaries: {gs.players[0].emissaries}")
    
    # Verify all P0 markers are cleared
    marker_count = sum(1 for spot in gs.available_discards if spot == 1)
    assert marker_count == 0, "All P0 markers should be cleared"
    assert gs.players[0].emissaries == 2, "Emissaries should be restored"
    print("✅ All P0 discard markers cleared and emissaries restored")


def test_recall_opponent_markers_unaffected():
    """Test that recall only clears current player's markers, not opponent's"""
    print("\n=== Test 5: Opponent Markers Unaffected ===")
    
    gs = GameState.create_initial_state()
    gs.in_draft_phase = False
    
    # Manually place markers for both players
    gs.available_swaps[0] = 1  # P0 marker
    gs.available_swaps[1] = 2  # P1 marker
    gs.players[0].emissaries = 0
    
    print(f"Before recall - available_swaps: {gs.available_swaps}")
    
    # Verify both markers are placed
    p0_markers = sum(1 for spot in gs.available_swaps if spot == 1)
    p1_markers = sum(1 for spot in gs.available_swaps if spot == 2)
    assert p0_markers == 1, "P0 should have 1 marker"
    assert p1_markers == 1, "P1 should have 1 marker"
    print(f"✅ P0 has {p0_markers} marker, P1 has {p1_markers} marker")
    
    # P0 recalls
    gs.current_player_idx = 0
    action = {"type": ACTION_RECALL}
    gs.apply_action(action)
    
    print(f"After P0 recall - available_swaps: {gs.available_swaps}")
    
    # Verify only P0 markers are cleared
    p0_markers = sum(1 for spot in gs.available_swaps if spot == 1)
    p1_markers = sum(1 for spot in gs.available_swaps if spot == 2)
    assert p0_markers == 0, "P0 markers should be cleared"
    assert p1_markers == 1, "P1 markers should remain"
    print("✅ Only P0 markers cleared, P1 markers remain intact")


def test_recall_legal_action_checks():
    """Test that recall is only legal when below maximum emissaries"""
    print("\n=== Test 6: Legal Action Checks ===")
    
    gs = GameState.create_initial_state()
    gs.in_draft_phase = False
    
    # Test 1: Recall legal with 0 emissaries, no decree
    gs.players[0].emissaries = 0
    gs.players[0].decree_used = False
    gs.current_player_idx = 0
    
    legal_actions = gs.get_legal_action_types()
    assert ACTION_RECALL in legal_actions, "Recall should be legal with 0 emissaries"
    print("✅ Recall legal with 0 emissaries (no decree)")
    
    # Test 2: Recall legal with 1 emissary, no decree
    gs.players[0].emissaries = 1
    legal_actions = gs.get_legal_action_types()
    assert ACTION_RECALL in legal_actions, "Recall should be legal with 1 emissary"
    print("✅ Recall legal with 1 emissary (no decree)")
    
    # Test 3: Recall NOT legal with 2 emissaries, no decree
    gs.players[0].emissaries = 2
    legal_actions = gs.get_legal_action_types()
    assert ACTION_RECALL not in legal_actions, "Recall should NOT be legal with 2 emissaries"
    print("✅ Recall NOT legal with 2 emissaries (no decree)")
    
    # Test 4: Recall legal with 0 emissaries, decree used
    gs.players[0].emissaries = 0
    gs.players[0].decree_used = True
    legal_actions = gs.get_legal_action_types()
    assert ACTION_RECALL in legal_actions, "Recall should be legal with 0 emissaries after decree"
    print("✅ Recall legal with 0 emissaries (decree used)")
    
    # Test 5: Recall NOT legal with 1 emissary, decree used
    gs.players[0].emissaries = 1
    legal_actions = gs.get_legal_action_types()
    assert ACTION_RECALL not in legal_actions, "Recall should NOT be legal with 1 emissary after decree"
    print("✅ Recall NOT legal with 1 emissary (decree used)")


def test_recall_turn_ending():
    """Test that turn ends after recall"""
    print("\n=== Test 7: Turn Ending ===")
    
    gs = GameState.create_initial_state()
    gs.in_draft_phase = False
    
    gs.players[0].emissaries = 0
    gs.players[0].decree_used = False
    gs.current_player_idx = 0
    
    current_player = gs.current_player_idx
    print(f"Current player before recall: {current_player}")
    
    action = {"type": ACTION_RECALL}
    gs.apply_action(action)
    
    print(f"Current player after recall: {gs.current_player_idx}")
    
    assert gs.current_player_idx != current_player, "Turn should end after recall"
    print("✅ Turn ends after recall")


def test_recall_illegal_when_at_max():
    """Test that recall is penalized when already at max emissaries"""
    print("\n=== Test 8: Illegal Recall Penalty ===")
    
    gs = GameState.create_initial_state()
    gs.in_draft_phase = False
    
    # Player already at max (2 emissaries, no decree)
    gs.players[0].emissaries = 2
    gs.players[0].decree_used = False
    gs.current_player_idx = 0
    
    print(f"Before illegal recall - P0 emissaries: {gs.players[0].emissaries}")
    
    # Try to recall (should be illegal)
    action = {"type": ACTION_RECALL}
    is_legal = gs.is_legal_action(action)
    
    assert not is_legal, "Recall should be illegal when at max"
    print("✅ Recall correctly identified as illegal when at max")


def test_recall_multiple_times():
    """Test that recall can be used multiple times in a game"""
    print("\n=== Test 9: Multiple Recalls ===")
    
    gs = GameState.create_initial_state()
    gs.in_draft_phase = False
    
    gs.players[0].emissaries = 0
    gs.players[0].decree_used = False
    
    # First recall
    print("First recall...")
    action = {"type": ACTION_RECALL}
    gs.apply_action(action)
    assert gs.players[0].emissaries == 2, "Should have 2 emissaries"
    print(f"After first recall - P0 emissaries: {gs.players[0].emissaries}")
    
    # Use an emissary
    gs.current_player_idx = 0
    gs.players[0].emissaries = 1
    
    # Second recall
    print("\nSecond recall...")
    action = {"type": ACTION_RECALL}
    gs.apply_action(action)
    assert gs.players[0].emissaries == 2, "Should have 2 emissaries again"
    print(f"After second recall - P0 emissaries: {gs.players[0].emissaries}")
    
    print("✅ Multiple recalls work correctly")


def test_recall_with_mixed_markers():
    """Test recall with both swap and discard markers"""
    print("\n=== Test 10: Mixed Markers ===")
    
    gs = GameState.create_initial_state()
    gs.in_draft_phase = False
    
    # Manually place markers on both swap and discard spots
    gs.available_swaps[0] = 1  # P0 swap marker
    gs.available_discards[0] = 1  # P0 discard marker
    gs.players[0].emissaries = 0
    
    print(f"Before recall - swaps: {gs.available_swaps}, discards: {gs.available_discards}")
    
    # Verify markers placed
    swap_markers = sum(1 for spot in gs.available_swaps if spot == 1)
    discard_markers = sum(1 for spot in gs.available_discards if spot == 1)
    assert swap_markers == 1, "Should have 1 swap marker"
    assert discard_markers == 1, "Should have 1 discard marker"
    print(f"✅ P0 has {swap_markers} swap marker and {discard_markers} discard marker")
    
    # Recall
    gs.current_player_idx = 0
    action = {"type": ACTION_RECALL}
    gs.apply_action(action)
    
    print(f"After recall - swaps: {gs.available_swaps}, discards: {gs.available_discards}")
    
    # Verify all markers cleared
    swap_markers = sum(1 for spot in gs.available_swaps if spot == 1)
    discard_markers = sum(1 for spot in gs.available_discards if spot == 1)
    assert swap_markers == 0, "All swap markers should be cleared"
    assert discard_markers == 0, "All discard markers should be cleared"
    print("✅ All swap and discard markers cleared")


def run_all_tests():
    """Run all recall tests"""
    print("=" * 60)
    print("TASK 22: RECALL COMPLIANCE TESTS")
    print("Testing RULES.md Section 5.3 Implementation")
    print("=" * 60)
    
    try:
        test_recall_restoration_normal()
        test_recall_restoration_after_decree()
        test_recall_marker_clearing_swap()
        test_recall_marker_clearing_discard()
        test_recall_opponent_markers_unaffected()
        test_recall_legal_action_checks()
        test_recall_turn_ending()
        test_recall_illegal_when_at_max()
        test_recall_multiple_times()
        test_recall_with_mixed_markers()
        
        print("\n" + "=" * 60)
        print("✅ ALL RECALL TESTS PASSED")
        print("=" * 60)
        print("\nSummary:")
        print("✅ Emissary restoration works correctly (2 normal, 1 after decree)")
        print("✅ Swap marker clearing works correctly")
        print("✅ Discard marker clearing works correctly")
        print("✅ Opponent markers remain unaffected")
        print("✅ Legal action checks work correctly")
        print("✅ Turn ending works correctly")
        print("✅ Illegal recall is properly handled")
        print("✅ Multiple recalls work correctly")
        print("✅ Mixed marker clearing works correctly")
        print("\nConclusion: Recall implementation is FULLY COMPLIANT with RULES.md Section 5.3")
        print("No fixes required - all functionality working as specified.")
        
        return True
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
