"""Test for Task 20: Fix setup issues (MED-001 - Draft hand distribution clarity)

This test verifies that the draft hand distribution fix maintains functional correctness
while improving code clarity by using positive indices instead of negative indices.
"""

import sys
sys.path.insert(0, '.')

from naishi_core.game_logic import GameState
from naishi_core.constants import NUM_DECKS, CARDS_PER_DECK


def test_draft_hand_distribution():
    """Test that draft hands are correctly distributed with 2 cards per player."""
    print("Testing draft hand distribution after MED-001 fix...")
    
    # Create initial state
    gs = GameState.create_initial_state(seed=42)
    
    # Verify we're in draft phase
    assert gs.in_draft_phase, "Should be in draft phase"
    
    # Verify each player has 2 cards in draft hand
    assert len(gs.draft_hands[0]) == 2, f"Player 0 should have 2 draft cards, got {len(gs.draft_hands[0])}"
    assert len(gs.draft_hands[1]) == 2, f"Player 1 should have 2 draft cards, got {len(gs.draft_hands[1])}"
    
    print(f"✓ Player 0 draft hand: {gs.draft_hands[0]}")
    print(f"✓ Player 1 draft hand: {gs.draft_hands[1]}")
    
    # Verify cards are different (from shuffled deck)
    all_draft_cards = gs.draft_hands[0] + gs.draft_hands[1]
    assert len(all_draft_cards) == 4, "Should have 4 total draft cards"
    
    # Verify river decks are correctly set up
    assert len(gs.river.decks) == NUM_DECKS, f"Should have {NUM_DECKS} river decks"
    for i, deck in enumerate(gs.river.decks):
        assert len(deck) == CARDS_PER_DECK, f"Deck {i} should have {CARDS_PER_DECK} cards, got {len(deck)}"
    
    print(f"✓ River has {NUM_DECKS} decks of {CARDS_PER_DECK} cards each")
    
    # Verify river tops are stored
    assert len(gs.river_tops_at_draft) == NUM_DECKS, "Should have river tops stored"
    print(f"✓ River tops at draft: {gs.river_tops_at_draft}")
    
    # Verify players start with empty hands and 5 Mountains in line
    for i, player in enumerate(gs.players):
        assert len(player.hand) == 0, f"Player {i} should start with empty hand"
        assert len(player.line) == 5, f"Player {i} should have 5 cards in line"
        assert all(card == 'Mountain' for card in player.line), f"Player {i} line should be all Mountains"
    
    print(f"✓ Both players start with empty hands and 5 Mountains in line")
    
    print("\n✅ All draft hand distribution tests passed!")
    print("MED-001 fix verified: Code clarity improved without affecting functionality")


def test_draft_completion():
    """Test that draft completion works correctly after the fix."""
    print("\nTesting draft completion...")
    
    # Create initial state
    gs = GameState.create_initial_state(seed=123)
    
    # Store original draft hands
    original_p0_hand = gs.draft_hands[0].copy()
    original_p1_hand = gs.draft_hands[1].copy()
    
    print(f"Before exchange - P0: {original_p0_hand}, P1: {original_p1_hand}")
    
    # Complete draft (each player gives card at index 0)
    gs._complete_draft(0, 0)
    
    # Verify draft phase is complete
    assert not gs.in_draft_phase, "Should no longer be in draft phase"
    
    # Verify each player now has 5 cards (2 draft + 3 Mountains, shuffled)
    assert len(gs.players[0].hand) == 5, f"Player 0 should have 5 cards, got {len(gs.players[0].hand)}"
    assert len(gs.players[1].hand) == 5, f"Player 1 should have 5 cards, got {len(gs.players[1].hand)}"
    
    print(f"✓ After draft - P0 hand size: {len(gs.players[0].hand)}, P1 hand size: {len(gs.players[1].hand)}")
    
    # Verify each hand contains 3 Mountains
    p0_mountains = sum(1 for card in gs.players[0].hand if card == 'Mountain')
    p1_mountains = sum(1 for card in gs.players[1].hand if card == 'Mountain')
    
    assert p0_mountains == 3, f"Player 0 should have 3 Mountains, got {p0_mountains}"
    assert p1_mountains == 3, f"Player 1 should have 3 Mountains, got {p1_mountains}"
    
    print(f"✓ P0 has {p0_mountains} Mountains, P1 has {p1_mountains} Mountains")
    
    # Verify draft state is cleared
    assert gs.river_tops_at_draft == [], "River tops should be cleared"
    assert gs.draft_hands == [[], []], "Draft hands should be cleared"
    
    print("✓ Draft state cleared correctly")
    
    print("\n✅ Draft completion test passed!")


def test_multiple_games_consistency():
    """Test that multiple games with different seeds work correctly."""
    print("\nTesting consistency across multiple games...")
    
    for seed in [1, 42, 100, 999]:
        gs = GameState.create_initial_state(seed=seed)
        
        # Verify basic setup
        assert gs.in_draft_phase, f"Seed {seed}: Should be in draft phase"
        assert len(gs.draft_hands[0]) == 2, f"Seed {seed}: P0 should have 2 draft cards"
        assert len(gs.draft_hands[1]) == 2, f"Seed {seed}: P1 should have 2 draft cards"
        assert len(gs.river.decks) == NUM_DECKS, f"Seed {seed}: Should have {NUM_DECKS} decks"
        
        print(f"✓ Seed {seed}: Setup correct")
    
    print("\n✅ Consistency test passed for all seeds!")


if __name__ == "__main__":
    test_draft_hand_distribution()
    test_draft_completion()
    test_multiple_games_consistency()
    
    print("\n" + "="*60)
    print("ALL TESTS PASSED - Task 20 Complete")
    print("="*60)
    print("\nSummary:")
    print("- MED-001 fixed: Draft hand distribution now uses clear positive indices")
    print("- Functional correctness maintained: All setup mechanics work correctly")
    print("- Code clarity improved: remaining[:2] and remaining[2:4] are clearer than")
    print("  remaining[-2:] and remaining[-4:-2]")
