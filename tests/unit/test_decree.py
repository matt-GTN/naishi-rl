"""
Test Task 23: Verify Decree implementation compliance with RULES.md Section 5.4

This test verifies:
1. Card swapping at same position
2. Permanent emissary lock
3. Once-per-game enforcement
4. Recall interaction (max 1 emissary after decree)
"""

import sys
sys.path.insert(0, '.')

from naishi_core.game_logic import GameState, ACTION_DECREE, ACTION_RECALL, ACTION_DEVELOP


def test_decree_card_swapping():
    """Test that decree swaps cards at the same position between players"""
    print("\n=== Test 1: Decree Card Swapping ===")
    
    gs = GameState.create_initial_state()
    
    # Set up known cards for testing - use set_all_cards to properly initialize
    p0_cards = ["Mountain", "Naishi", "Councellor", "Fort", "Monk",
                "Torii", "Knight", "Banner", "Rice fields", "Ronin"]
    p1_cards = ["Naishi", "Mountain", "Sentinel", "Fort", "Monk",
                "Knight", "Torii", "Banner", "Rice fields", "Ninja"]
    
    gs.players[0].set_all_cards(p0_cards)
    gs.players[1].set_all_cards(p1_cards)
    
    # Ensure player has emissary and decree not used
    gs.players[0].emissaries = 2
    gs.players[0].decree_used = False
    gs.players[1].decree_used = False
    gs.in_draft_phase = False  # Skip draft phase
    
    # Test swapping in Line (position 2)
    print(f"Before decree - P0 Line[2]: {gs.players[0].line[2]}, P1 Line[2]: {gs.players[1].line[2]}")
    action = {"type": ACTION_DECREE, "pos": 2}
    gs.apply_action(action)
    print(f"After decree - P0 Line[2]: {gs.players[0].line[2]}, P1 Line[2]: {gs.players[1].line[2]}")
    
    assert gs.players[0].line[2] == "Sentinel", "P0 should have P1's card"
    assert gs.players[1].line[2] == "Councellor", "P1 should have P0's card"
    print("✅ Line swap works correctly")
    
    # Reset for hand test with different cards
    gs = GameState.create_initial_state()
    p0_cards_v2 = ["Mountain", "Naishi", "Councellor", "Fort", "Monk",
                   "Torii", "Knight", "Banner", "Sentinel", "Ronin"]  # Changed hand[3] to Sentinel
    p1_cards_v2 = ["Naishi", "Mountain", "Sentinel", "Fort", "Monk",
                   "Knight", "Torii", "Banner", "Rice fields", "Ninja"]  # hand[3] is Rice fields
    gs.players[0].set_all_cards(p0_cards_v2)
    gs.players[1].set_all_cards(p1_cards_v2)
    gs.players[0].emissaries = 2
    gs.players[0].decree_used = False
    gs.players[1].decree_used = False
    gs.in_draft_phase = False
    
    # Test swapping in Hand (position 8 = hand[3])
    print(f"\nBefore decree - P0 Hand[3]: {gs.players[0].hand[3]}, P1 Hand[3]: {gs.players[1].hand[3]}")
    p0_before = gs.players[0].hand[3]
    p1_before = gs.players[1].hand[3]
    action = {"type": ACTION_DECREE, "pos": 8}
    gs.apply_action(action)
    print(f"After decree - P0 Hand[3]: {gs.players[0].hand[3]}, P1 Hand[3]: {gs.players[1].hand[3]}")
    
    assert gs.players[0].hand[3] == p1_before, "P0 should have P1's card"
    assert gs.players[1].hand[3] == p0_before, "P1 should have P0's card"
    print("✅ Hand swap works correctly")


def test_decree_permanent_lock():
    """Test that decree permanently locks one emissary"""
    print("\n=== Test 2: Permanent Emissary Lock ===")
    
    gs = GameState.create_initial_state()
    
    # Set up cards properly
    p0_cards = ["Mountain", "Naishi", "Councellor", "Fort", "Monk",
                "Torii", "Knight", "Banner", "Rice fields", "Ronin"]
    p1_cards = ["Naishi", "Mountain", "Sentinel", "Fort", "Monk",
                "Knight", "Torii", "Banner", "Rice fields", "Ninja"]
    gs.players[0].set_all_cards(p0_cards)
    gs.players[1].set_all_cards(p1_cards)
    
    gs.players[0].emissaries = 2
    gs.players[0].decree_used = False
    gs.players[1].decree_used = False
    gs.in_draft_phase = False
    
    print(f"Before decree - P0 emissaries: {gs.players[0].emissaries}, decree_used: {gs.players[0].decree_used}")
    
    # Use decree
    action = {"type": ACTION_DECREE, "pos": 0}
    gs.apply_action(action)
    
    print(f"After decree - P0 emissaries: {gs.players[0].emissaries}, decree_used: {gs.players[0].decree_used}")
    
    assert gs.players[0].emissaries == 1, "Should have 1 emissary after using decree"
    assert gs.players[0].decree_used == True, "decree_used flag should be set"
    print("✅ Emissary consumed and flag set")
    
    # Test recall restores to max of 1 (not 2)
    gs.current_player_idx = 0  # Switch back to P0
    gs.players[0].emissaries = 0
    action = {"type": ACTION_RECALL}
    gs.apply_action(action)
    
    print(f"After recall - P0 emissaries: {gs.players[0].emissaries}")
    
    assert gs.players[0].emissaries == 1, "Recall should restore to max of 1 after decree"
    print("✅ Recall correctly restores to 1 (not 2) after decree")


def test_decree_once_per_game():
    """Test that decree can only be used once per game by either player"""
    print("\n=== Test 3: Once-per-game Enforcement ===")
    
    gs = GameState.create_initial_state()
    
    # Set up cards properly
    p0_cards = ["Mountain", "Naishi", "Councellor", "Fort", "Monk",
                "Torii", "Knight", "Banner", "Rice fields", "Ronin"]
    p1_cards = ["Naishi", "Mountain", "Sentinel", "Fort", "Monk",
                "Knight", "Torii", "Banner", "Rice fields", "Ninja"]
    gs.players[0].set_all_cards(p0_cards)
    gs.players[1].set_all_cards(p1_cards)
    
    gs.players[0].emissaries = 2
    gs.players[1].emissaries = 2
    gs.players[0].decree_used = False
    gs.players[1].decree_used = False
    gs.in_draft_phase = False
    
    # Player 0 uses decree
    print("Player 0 uses decree...")
    action = {"type": ACTION_DECREE, "pos": 0}
    gs.apply_action(action)
    
    assert gs.players[0].decree_used == True, "P0 decree_used should be True"
    print("✅ P0 successfully used decree")
    
    # Check that decree is not in legal actions for either player
    gs.current_player_idx = 0
    legal_actions = gs.get_legal_action_types()
    assert ACTION_DECREE not in legal_actions, "Decree should not be legal for P0 after use"
    print("✅ Decree not legal for P0 after use")
    
    gs.current_player_idx = 1
    legal_actions = gs.get_legal_action_types()
    assert ACTION_DECREE not in legal_actions, "Decree should not be legal for P1 after P0 used it"
    print("✅ Decree not legal for P1 after P0 used it")
    
    # Try to use decree as P1 (should fail)
    gs.players[1].emissaries = 2
    action = {"type": ACTION_DECREE, "pos": 0}
    is_legal = gs.is_legal_action(action)
    assert not is_legal, "Decree should not be legal after already used"
    print("✅ Decree correctly blocked after first use")


def test_decree_recall_interaction():
    """Test that recall only restores 1 emissary after decree"""
    print("\n=== Test 4: Recall Interaction ===")
    
    gs = GameState.create_initial_state()
    
    # Set up cards properly
    p0_cards = ["Mountain", "Naishi", "Councellor", "Fort", "Monk",
                "Torii", "Knight", "Banner", "Rice fields", "Ronin"]
    p1_cards = ["Naishi", "Mountain", "Sentinel", "Fort", "Monk",
                "Knight", "Torii", "Banner", "Rice fields", "Ninja"]
    gs.players[0].set_all_cards(p0_cards)
    gs.players[1].set_all_cards(p1_cards)
    gs.in_draft_phase = False
    
    # Player without decree can recall to 2
    gs.players[0].emissaries = 0
    gs.players[0].decree_used = False
    
    print(f"P0 without decree - emissaries before recall: {gs.players[0].emissaries}")
    action = {"type": ACTION_RECALL}
    gs.apply_action(action)
    print(f"P0 without decree - emissaries after recall: {gs.players[0].emissaries}")
    
    assert gs.players[0].emissaries == 2, "Should recall to 2 without decree"
    print("✅ Recall to 2 works without decree")
    
    # Player with decree can only recall to 1
    gs.players[1].emissaries = 0
    gs.players[1].decree_used = True
    
    print(f"\nP1 with decree - emissaries before recall: {gs.players[1].emissaries}")
    gs.current_player_idx = 1
    action = {"type": ACTION_RECALL}
    gs.apply_action(action)
    print(f"P1 with decree - emissaries after recall: {gs.players[1].emissaries}")
    
    assert gs.players[1].emissaries == 1, "Should recall to 1 with decree"
    print("✅ Recall to 1 works with decree")


def test_decree_emissary_requirement():
    """Test that decree requires an emissary to use"""
    print("\n=== Test 5: Emissary Requirement ===")
    
    gs = GameState.create_initial_state()
    
    # Set up cards properly
    p0_cards = ["Mountain", "Naishi", "Councellor", "Fort", "Monk",
                "Torii", "Knight", "Banner", "Rice fields", "Ronin"]
    p1_cards = ["Naishi", "Mountain", "Sentinel", "Fort", "Monk",
                "Knight", "Torii", "Banner", "Rice fields", "Ninja"]
    gs.players[0].set_all_cards(p0_cards)
    gs.players[1].set_all_cards(p1_cards)
    gs.in_draft_phase = False
    
    gs.players[0].emissaries = 0
    gs.players[0].decree_used = False
    gs.players[1].decree_used = False
    
    print(f"P0 emissaries: {gs.players[0].emissaries}")
    
    # Check that decree is not legal without emissaries
    legal_actions = gs.get_legal_action_types()
    assert ACTION_DECREE not in legal_actions, "Decree should not be legal without emissaries"
    print("✅ Decree not legal without emissaries")
    
    # Try to use decree (should be illegal)
    action = {"type": ACTION_DECREE, "pos": 0}
    is_legal = gs.is_legal_action(action)
    assert not is_legal, "Decree should not be legal without emissaries"
    print("✅ Decree correctly blocked without emissaries")


def test_decree_turn_ending():
    """Test that turn ends after decree"""
    print("\n=== Test 6: Turn Ending ===")
    
    gs = GameState.create_initial_state()
    
    # Set up cards properly
    p0_cards = ["Mountain", "Naishi", "Councellor", "Fort", "Monk",
                "Torii", "Knight", "Banner", "Rice fields", "Ronin"]
    p1_cards = ["Naishi", "Mountain", "Sentinel", "Fort", "Monk",
                "Knight", "Torii", "Banner", "Rice fields", "Ninja"]
    gs.players[0].set_all_cards(p0_cards)
    gs.players[1].set_all_cards(p1_cards)
    gs.in_draft_phase = False
    
    gs.players[0].emissaries = 2
    gs.players[0].decree_used = False
    gs.players[1].decree_used = False
    
    current_player = gs.current_player_idx
    print(f"Current player before decree: {current_player}")
    
    # Use decree
    action = {"type": ACTION_DECREE, "pos": 0}
    gs.apply_action(action)
    
    print(f"Current player after decree: {gs.current_player_idx}")
    
    # Turn should have ended (player switched)
    assert gs.current_player_idx != current_player, "Turn should end after decree"
    print("✅ Turn ends after decree")
    
    # Verify no must_develop flag is set
    assert not gs.must_develop, "must_develop should not be set after decree"
    print("✅ No must_develop flag after decree")


def test_decree_position_mapping():
    """Test that positions 0-4 map to Line and 5-9 map to Hand"""
    print("\n=== Test 7: Position Mapping ===")
    
    gs = GameState.create_initial_state()
    
    # Set up distinct cards using set_all_cards
    p0_cards = ["Card0", "Card1", "Card2", "Card3", "Card4",
                "Card5", "Card6", "Card7", "Card8", "Card9"]
    p1_cards = ["CardA", "CardB", "CardC", "CardD", "CardE",
                "CardF", "CardG", "CardH", "CardI", "CardJ"]
    gs.players[0].set_all_cards(p0_cards)
    gs.players[1].set_all_cards(p1_cards)
    
    gs.players[0].emissaries = 2
    gs.players[0].decree_used = False
    gs.players[1].decree_used = False
    gs.in_draft_phase = False
    
    # Test Line position (pos 3 -> line[3])
    print(f"\nTesting Line position 3:")
    print(f"Before - P0 line[3]: {gs.players[0].line[3]}, P1 line[3]: {gs.players[1].line[3]}")
    action = {"type": ACTION_DECREE, "pos": 3}
    gs.apply_action(action)
    print(f"After - P0 line[3]: {gs.players[0].line[3]}, P1 line[3]: {gs.players[1].line[3]}")
    assert gs.players[0].line[3] == "CardD", "Should swap line cards"
    assert gs.players[1].line[3] == "Card3", "Should swap line cards"
    print("✅ Line position mapping works")
    
    # Reset and test Hand position (pos 7 -> hand[2])
    gs = GameState.create_initial_state()
    gs.players[0].set_all_cards(p0_cards)
    gs.players[1].set_all_cards(p1_cards)
    gs.players[0].emissaries = 2
    gs.players[0].decree_used = False
    gs.players[1].decree_used = False
    gs.in_draft_phase = False
    
    print(f"\nTesting Hand position 7 (hand[2]):")
    print(f"Before - P0 hand[2]: {gs.players[0].hand[2]}, P1 hand[2]: {gs.players[1].hand[2]}")
    action = {"type": ACTION_DECREE, "pos": 7}
    gs.apply_action(action)
    print(f"After - P0 hand[2]: {gs.players[0].hand[2]}, P1 hand[2]: {gs.players[1].hand[2]}")
    assert gs.players[0].hand[2] == "CardH", "Should swap hand cards"
    assert gs.players[1].hand[2] == "Card7", "Should swap hand cards"
    print("✅ Hand position mapping works")


def run_all_tests():
    """Run all decree tests"""
    print("=" * 60)
    print("TASK 23: DECREE COMPLIANCE TESTS")
    print("Testing RULES.md Section 5.4 Implementation")
    print("=" * 60)
    
    try:
        test_decree_card_swapping()
        test_decree_permanent_lock()
        test_decree_once_per_game()
        test_decree_recall_interaction()
        test_decree_emissary_requirement()
        test_decree_turn_ending()
        test_decree_position_mapping()
        
        print("\n" + "=" * 60)
        print("✅ ALL DECREE TESTS PASSED")
        print("=" * 60)
        print("\nSummary:")
        print("✅ Card swapping at same position works correctly")
        print("✅ Permanent emissary lock works correctly")
        print("✅ Once-per-game enforcement works correctly")
        print("✅ Recall interaction works correctly (max 1 after decree)")
        print("✅ Emissary requirement enforced correctly")
        print("✅ Turn ending works correctly")
        print("✅ Position mapping works correctly")
        print("\nConclusion: Decree implementation is FULLY COMPLIANT with RULES.md Section 5.4")
        
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
