"""
Unit tests for all GameState actions (Task 35).

Tests all action types to ensure they comply with RULES.md:
- ACTION_DEVELOP (Section 5.1)
- ACTION_SWAP (Section 5.2 - all 4 types)
- ACTION_DISCARD (Section 5.2)
- ACTION_RECALL (Section 5.3)
- ACTION_DECREE (Section 5.4)
- ACTION_END_GAME (Section 7)

Requirements tested: 1.3-1.7
"""

import pytest
from naishi_core.game_logic import (
    GameState, 
    ACTION_DEVELOP, 
    ACTION_SWAP, 
    ACTION_DISCARD, 
    ACTION_RECALL, 
    ACTION_DECREE, 
    ACTION_END_GAME
)
from naishi_core.constants import LINE_SIZE, HAND_SIZE, NUM_DECKS


def complete_draft(gs):
    """Helper to complete draft phase."""
    gs.apply_action_array([0, 0, 0, 0, 0, 0, 0, 0])  # P0 draft
    gs.apply_action_array([0, 1, 0, 0, 0, 0, 0, 0])  # P1 draft


class TestActionDevelop:
    """Test ACTION_DEVELOP (RULES.md Section 5.1) - Requirement 1.3."""
    
    def test_develop_line_position(self):
        """WHEN player develops line position THEN card SHALL be replaced from correct deck."""
        gs = GameState.create_initial_state(seed=42)
        complete_draft(gs)
        
        player = gs.players[gs.current_player_idx]
        original_card = player.line[0]
        river_top = gs.river.get_top_card(0)
        
        # Develop position 0 (line position 0, deck 0)
        obs, reward, done, trunc, info = gs.apply_action_array([1, 0, 0, 0, 0, 0, 0, 0])
        
        # Verify card was replaced
        assert player.line[0] == river_top
        assert player.line[0] != original_card
    
    def test_develop_hand_position(self):
        """WHEN player develops hand position THEN card SHALL be replaced from correct deck."""
        gs = GameState.create_initial_state(seed=42)
        complete_draft(gs)
        
        player = gs.players[gs.current_player_idx]
        original_card = player.hand[0]
        # Position 5 maps to deck 0 (5 % 5 = 0)
        river_top = gs.river.get_top_card(0)
        
        # Develop position 5 (hand position 0, deck 0)
        obs, reward, done, trunc, info = gs.apply_action_array([1, 5, 0, 0, 0, 0, 0, 0])
        
        # Verify card was replaced
        assert player.hand[0] == river_top
        assert player.hand[0] != original_card

    def test_develop_position_mapping(self):
        """WHEN player develops position 0-9 THEN correct deck SHALL be used (pos % 5)."""
        gs = GameState.create_initial_state(seed=42)
        complete_draft(gs)
        
        # Test position mapping: pos % 5 = deck
        test_cases = [
            (0, 0), (1, 1), (2, 2), (3, 3), (4, 4),  # Line
            (5, 0), (6, 1), (7, 2), (8, 3), (9, 4)   # Hand
        ]
        
        for pos, expected_deck in test_cases:
            gs_test = GameState.create_initial_state(seed=42)
            complete_draft(gs_test)
            
            river_top = gs_test.river.get_top_card(expected_deck)
            gs_test.apply_action_array([1, pos, 0, 0, 0, 0, 0, 0])
            
            player = gs_test.players[0]
            if pos < LINE_SIZE:
                assert player.line[pos] == river_top
            else:
                assert player.hand[pos - LINE_SIZE] == river_top
    
    def test_develop_empty_deck_handling(self):
        """WHEN player develops from empty deck THEN action SHALL complete without error."""
        gs = GameState.create_initial_state(seed=42)
        complete_draft(gs)
        
        # Empty deck 0
        gs.river.decks[0] = []
        
        player = gs.players[gs.current_player_idx]
        original_card = player.line[0]
        
        # Develop position 0 (empty deck)
        obs, reward, done, trunc, info = gs.apply_action_array([1, 0, 0, 0, 0, 0, 0, 0])
        
        # Card should remain unchanged when deck is empty
        assert player.line[0] == original_card
    
    def test_develop_triggers_optional_emissary(self):
        """WHEN player develops AND can use emissary THEN optional_emissary_available SHALL be True."""
        gs = GameState.create_initial_state(seed=42)
        complete_draft(gs)
        
        # Develop
        obs, reward, done, trunc, info = gs.apply_action_array([1, 0, 0, 0, 0, 0, 0, 0])
        
        # Should trigger optional emissary
        assert gs.optional_emissary_available == True
        assert done == False
    
    def test_develop_after_emissary_clears_must_develop(self):
        """WHEN must_develop is True AND player develops THEN flag SHALL be cleared."""
        gs = GameState.create_initial_state(seed=42)
        complete_draft(gs)
        
        # Use emissary first to set must_develop
        gs.apply_action_array([2, 0, 0, 0, 0, 1, 0, 0])  # Swap
        assert gs.must_develop == True
        
        # Develop (required)
        obs, reward, done, trunc, info = gs.apply_action_array([1, 0, 0, 0, 0, 0, 0, 0])
        
        # Flag should be cleared
        assert gs.must_develop == False


class TestActionSwap:
    """Test ACTION_SWAP (RULES.md Section 5.2) - Requirement 1.4."""
    
    def test_swap_in_hand(self):
        """WHEN player swaps in hand THEN two hand cards SHALL be swapped."""
        gs = GameState.create_initial_state(seed=42)
        complete_draft(gs)
        
        player = gs.players[gs.current_player_idx]
        card0 = player.hand[0]
        card1 = player.hand[1]
        
        # Swap hand positions 0 and 1 (swap_type=0, pos1=0, pos2=1)
        obs, reward, done, trunc, info = gs.apply_action_array([2, 0, 0, 0, 0, 1, 0, 0])
        
        # Verify swap occurred
        assert player.hand[0] == card1
        assert player.hand[1] == card0
    
    def test_swap_in_line(self):
        """WHEN player swaps in line THEN two line cards SHALL be swapped."""
        gs = GameState.create_initial_state(seed=42)
        complete_draft(gs)
        
        player = gs.players[gs.current_player_idx]
        card0 = player.line[0]
        card1 = player.line[1]
        
        # Swap line positions 0 and 1 (swap_type=1, pos1=0, pos2=1)
        obs, reward, done, trunc, info = gs.apply_action_array([2, 0, 0, 1, 0, 1, 0, 0])
        
        # Verify swap occurred
        assert player.line[0] == card1
        assert player.line[1] == card0
    
    def test_swap_between_hand_and_line(self):
        """WHEN player swaps between hand and line THEN cards at same position SHALL be swapped."""
        gs = GameState.create_initial_state(seed=42)
        complete_draft(gs)
        
        player = gs.players[gs.current_player_idx]
        line_card = player.line[2]
        hand_card = player.hand[2]
        
        # Swap between line and hand at position 2 (swap_type=2, pos1=2)
        obs, reward, done, trunc, info = gs.apply_action_array([2, 0, 0, 2, 2, 0, 0, 0])
        
        # Verify swap occurred
        assert player.line[2] == hand_card
        assert player.hand[2] == line_card
    
    def test_swap_in_river(self):
        """WHEN player swaps in river THEN top cards of two decks SHALL be swapped."""
        gs = GameState.create_initial_state(seed=42)
        complete_draft(gs)
        
        deck0_top = gs.river.get_top_card(0)
        deck1_top = gs.river.get_top_card(1)
        
        # Swap river decks 0 and 1 (swap_type=3, pos1=0, pos2=1)
        obs, reward, done, trunc, info = gs.apply_action_array([2, 0, 0, 3, 0, 1, 0, 0])
        
        # Verify swap occurred
        assert gs.river.get_top_card(0) == deck1_top
        assert gs.river.get_top_card(1) == deck0_top

    def test_swap_consumes_emissary(self):
        """WHEN player swaps THEN one emissary SHALL be consumed."""
        gs = GameState.create_initial_state(seed=42)
        complete_draft(gs)
        
        player = gs.players[gs.current_player_idx]
        initial_emissaries = player.emissaries
        
        # Swap in hand
        gs.apply_action_array([2, 0, 0, 0, 0, 1, 0, 0])
        
        # Verify emissary consumed
        assert player.emissaries == initial_emissaries - 1
    
    def test_swap_occupies_spot(self):
        """WHEN player swaps THEN one swap spot SHALL be occupied."""
        gs = GameState.create_initial_state(seed=42)
        complete_draft(gs)
        
        # Initially all spots free
        assert gs.available_swaps == [0, 0, 0]
        
        # Swap in hand
        gs.apply_action_array([2, 0, 0, 0, 0, 1, 0, 0])
        
        # One spot should be occupied by player 1 (current_player_idx=0, so marker=1)
        assert gs.available_swaps.count(0) == 2
        assert 1 in gs.available_swaps
    
    def test_swap_sets_must_develop_when_emissary_first(self):
        """WHEN player swaps first THEN must_develop SHALL be True."""
        gs = GameState.create_initial_state(seed=42)
        complete_draft(gs)
        
        # Swap first (Option B)
        obs, reward, done, trunc, info = gs.apply_action_array([2, 0, 0, 0, 0, 1, 0, 0])
        
        # Should set must_develop
        assert gs.must_develop == True
        assert done == False
    
    def test_swap_clears_optional_emissary_when_after_develop(self):
        """WHEN player swaps after develop THEN optional_emissary_available SHALL be cleared."""
        gs = GameState.create_initial_state(seed=42)
        complete_draft(gs)
        
        # Develop first to trigger optional emissary
        gs.apply_action_array([1, 0, 0, 0, 0, 0, 0, 0])
        assert gs.optional_emissary_available == True
        
        # Use optional emissary (swap)
        obs, reward, done, trunc, info = gs.apply_action_array([2, 0, 0, 0, 0, 1, 0, 0])
        
        # Flag should be cleared
        assert gs.optional_emissary_available == False
    
    def test_swap_fails_without_emissaries(self):
        """WHEN player has no emissaries THEN swap SHALL fail with penalty."""
        gs = GameState.create_initial_state(seed=42)
        complete_draft(gs)
        
        # Remove emissaries
        player = gs.players[gs.current_player_idx]
        player.emissaries = 0
        
        # Try to swap
        obs, reward, done, trunc, info = gs.apply_action_array([2, 0, 0, 0, 0, 1, 0, 0])
        
        # Should fail with penalty
        assert reward == -0.1
    
    def test_swap_fails_when_all_spots_full(self):
        """WHEN all swap spots are full THEN swap SHALL fail with penalty."""
        gs = GameState.create_initial_state(seed=42)
        complete_draft(gs)
        
        # Fill all swap spots
        gs.available_swaps = [1, 1, 1]
        
        # Try to swap
        obs, reward, done, trunc, info = gs.apply_action_array([2, 0, 0, 0, 0, 1, 0, 0])
        
        # Should fail with penalty
        assert reward == -0.1


class TestActionDiscard:
    """Test ACTION_DISCARD (RULES.md Section 5.2) - Requirement 1.4."""
    
    def test_discard_removes_two_cards(self):
        """WHEN player discards THEN top cards from two decks SHALL be removed."""
        gs = GameState.create_initial_state(seed=42)
        complete_draft(gs)
        
        deck0_top = gs.river.get_top_card(0)
        deck1_top = gs.river.get_top_card(1)
        deck0_count = len(gs.river.decks[0])
        deck1_count = len(gs.river.decks[1])
        
        # Discard from decks 0 and 1 (deck1=0, deck2=1)
        obs, reward, done, trunc, info = gs.apply_action_array([3, 0, 0, 0, 0, 0, 0, 1])
        
        # Verify cards removed
        assert len(gs.river.decks[0]) == deck0_count - 1
        assert len(gs.river.decks[1]) == deck1_count - 1
        assert gs.river.get_top_card(0) != deck0_top
        assert gs.river.get_top_card(1) != deck1_top
    
    def test_discard_consumes_emissary(self):
        """WHEN player discards THEN one emissary SHALL be consumed."""
        gs = GameState.create_initial_state(seed=42)
        complete_draft(gs)
        
        player = gs.players[gs.current_player_idx]
        initial_emissaries = player.emissaries
        
        # Discard
        gs.apply_action_array([3, 0, 0, 0, 0, 0, 0, 1])
        
        # Verify emissary consumed
        assert player.emissaries == initial_emissaries - 1
    
    def test_discard_occupies_spot(self):
        """WHEN player discards THEN one discard spot SHALL be occupied."""
        gs = GameState.create_initial_state(seed=42)
        complete_draft(gs)
        
        # Initially all spots free
        assert gs.available_discards == [0, 0]
        
        # Discard
        gs.apply_action_array([3, 0, 0, 0, 0, 0, 0, 1])
        
        # One spot should be occupied
        assert gs.available_discards.count(0) == 1
        assert 1 in gs.available_discards

    def test_discard_sets_must_develop_when_emissary_first(self):
        """WHEN player discards first THEN must_develop SHALL be True."""
        gs = GameState.create_initial_state(seed=42)
        complete_draft(gs)
        
        # Discard first (Option B)
        obs, reward, done, trunc, info = gs.apply_action_array([3, 0, 0, 0, 0, 0, 0, 1])
        
        # Should set must_develop
        assert gs.must_develop == True
        assert done == False
    
    def test_discard_clears_optional_emissary_when_after_develop(self):
        """WHEN player discards after develop THEN optional_emissary_available SHALL be cleared."""
        gs = GameState.create_initial_state(seed=42)
        complete_draft(gs)
        
        # Develop first to trigger optional emissary
        gs.apply_action_array([1, 0, 0, 0, 0, 0, 0, 0])
        assert gs.optional_emissary_available == True
        
        # Use optional emissary (discard)
        obs, reward, done, trunc, info = gs.apply_action_array([3, 0, 0, 0, 0, 0, 0, 1])
        
        # Flag should be cleared
        assert gs.optional_emissary_available == False
    
    def test_discard_fails_without_emissaries(self):
        """WHEN player has no emissaries THEN discard SHALL fail with penalty."""
        gs = GameState.create_initial_state(seed=42)
        complete_draft(gs)
        
        # Remove emissaries
        player = gs.players[gs.current_player_idx]
        player.emissaries = 0
        
        # Try to discard
        obs, reward, done, trunc, info = gs.apply_action_array([3, 0, 0, 0, 0, 0, 0, 1])
        
        # Should fail with penalty
        assert reward == -0.1
    
    def test_discard_fails_when_all_spots_full(self):
        """WHEN all discard spots are full THEN discard SHALL fail with penalty."""
        gs = GameState.create_initial_state(seed=42)
        complete_draft(gs)
        
        # Fill all discard spots
        gs.available_discards = [1, 1]
        
        # Try to discard
        obs, reward, done, trunc, info = gs.apply_action_array([3, 0, 0, 0, 0, 0, 0, 1])
        
        # Should fail with penalty
        assert reward == -0.1
    
    def test_discard_requires_different_decks(self):
        """WHEN player tries to discard same deck twice THEN it SHALL be handled correctly."""
        gs = GameState.create_initial_state(seed=42)
        complete_draft(gs)
        
        # Try to discard same deck (deck1=0, deck2=0) - should be caught by is_legal_action
        is_legal = gs.is_legal_action_array([3, 0, 0, 0, 0, 0, 0, 0])
        
        # Should not be legal
        assert is_legal == False


class TestActionRecall:
    """Test ACTION_RECALL (RULES.md Section 5.3) - Requirement 1.5."""
    
    def test_recall_restores_emissaries(self):
        """WHEN player recalls THEN emissaries SHALL be restored to max."""
        gs = GameState.create_initial_state(seed=42)
        complete_draft(gs)
        
        player = gs.players[0]  # Track player 0
        
        # Use emissaries (swap first, then develop - this is Option B)
        gs.apply_action_array([2, 0, 0, 0, 0, 1, 0, 0])  # Swap (must develop next)
        gs.apply_action_array([1, 0, 0, 0, 0, 0, 0, 0])  # Develop (turn ends, switches to P1)
        
        # Now P1's turn - skip it
        gs.apply_action_array([1, 0, 0, 0, 0, 0, 0, 0])  # P1 develop
        gs.skip_optional_emissary()  # Skip optional emissary
        
        # Back to P0 - use second emissary
        gs.apply_action_array([2, 0, 0, 0, 0, 1, 0, 0])  # Swap
        gs.apply_action_array([1, 0, 0, 0, 0, 0, 0, 0])  # Develop
        
        # Player 0 should have 0 emissaries
        assert player.emissaries == 0
        
        # P1's turn - skip it
        gs.apply_action_array([1, 0, 0, 0, 0, 0, 0, 0])
        gs.skip_optional_emissary()
        
        # P0 recalls
        obs, reward, done, trunc, info = gs.apply_action_array([4, 0, 0, 0, 0, 0, 0, 0])
        
        # Should restore to 2 (max without decree)
        assert player.emissaries == 2
    
    def test_recall_clears_player_markers(self):
        """WHEN player recalls THEN their markers SHALL be cleared from spots."""
        gs = GameState.create_initial_state(seed=42)
        complete_draft(gs)
        
        # P0 uses swap and discard to occupy spots
        gs.apply_action_array([2, 0, 0, 0, 0, 1, 0, 0])  # Swap (player 0 = marker 1)
        gs.apply_action_array([1, 0, 0, 0, 0, 0, 0, 0])  # Develop (turn ends)
        
        # P1's turn - skip
        gs.apply_action_array([1, 0, 0, 0, 0, 0, 0, 0])
        gs.skip_optional_emissary()
        
        # P0 uses discard
        gs.apply_action_array([3, 0, 0, 0, 0, 0, 0, 1])  # Discard (player 0 = marker 1)
        gs.apply_action_array([1, 0, 0, 0, 0, 0, 0, 0])  # Develop (turn ends)
        
        # Verify spots occupied by player 0 (marker = 1)
        assert 1 in gs.available_swaps
        assert 1 in gs.available_discards
        
        # P1's turn - skip
        gs.apply_action_array([1, 0, 0, 0, 0, 0, 0, 0])
        gs.skip_optional_emissary()
        
        # P0 recalls
        gs.apply_action_array([4, 0, 0, 0, 0, 0, 0, 0])
        
        # Player 0's markers (1) should be cleared
        assert 1 not in gs.available_swaps
        assert 1 not in gs.available_discards
    
    def test_recall_only_clears_own_markers(self):
        """WHEN player recalls THEN only their markers SHALL be cleared."""
        gs = GameState.create_initial_state(seed=42)
        complete_draft(gs)
        
        # Player 0 uses swap
        gs.apply_action_array([2, 0, 0, 0, 0, 1, 0, 0])
        gs.apply_action_array([1, 0, 0, 0, 0, 0, 0, 0])
        
        # Player 1 uses swap
        gs.apply_action_array([2, 0, 0, 0, 0, 1, 0, 0])
        gs.apply_action_array([1, 0, 0, 0, 0, 0, 0, 0])
        
        # Both players should have markers
        assert 1 in gs.available_swaps  # Player 0
        assert 2 in gs.available_swaps  # Player 1
        
        # Player 0 recalls
        gs.apply_action_array([4, 0, 0, 0, 0, 0, 0, 0])
        
        # Only player 0's markers cleared
        assert 1 not in gs.available_swaps
        assert 2 in gs.available_swaps  # Player 1's marker remains

    def test_recall_ends_turn(self):
        """WHEN player recalls THEN turn SHALL end."""
        gs = GameState.create_initial_state(seed=42)
        complete_draft(gs)
        
        # Use emissary to enable recall
        gs.apply_action_array([2, 0, 0, 0, 0, 1, 0, 0])
        gs.apply_action_array([1, 0, 0, 0, 0, 0, 0, 0])
        
        current_player = gs.current_player_idx
        
        # Recall
        obs, reward, done, trunc, info = gs.apply_action_array([4, 0, 0, 0, 0, 0, 0, 0])
        
        # Turn should end (player switched)
        assert gs.current_player_idx != current_player
    
    def test_recall_fails_at_max_emissaries(self):
        """WHEN player has max emissaries THEN recall SHALL fail with penalty."""
        gs = GameState.create_initial_state(seed=42)
        complete_draft(gs)
        
        player = gs.players[gs.current_player_idx]
        assert player.emissaries == 2  # At max
        
        # Try to recall
        obs, reward, done, trunc, info = gs.apply_action_array([4, 0, 0, 0, 0, 0, 0, 0])
        
        # Should fail with penalty
        assert reward == -0.1
    
    def test_recall_after_decree_restores_to_one(self):
        """WHEN player recalls after using decree THEN only 1 emissary SHALL be restored."""
        gs = GameState.create_initial_state(seed=42)
        complete_draft(gs)
        
        player = gs.players[0]  # Track player 0
        
        # P0 uses decree (ends turn)
        gs.apply_action_array([5, 0, 0, 0, 0, 0, 0, 0])
        
        # Player should have decree_used flag and 1 emissary
        assert player.decree_used == True
        assert player.emissaries == 1
        
        # P1's turn - skip
        gs.apply_action_array([1, 0, 0, 0, 0, 0, 0, 0])
        gs.skip_optional_emissary()
        
        # P0 uses the remaining emissary
        gs.apply_action_array([2, 0, 0, 0, 0, 1, 0, 0])
        gs.apply_action_array([1, 0, 0, 0, 0, 0, 0, 0])
        
        assert player.emissaries == 0
        
        # P1's turn - skip
        gs.apply_action_array([1, 0, 0, 0, 0, 0, 0, 0])
        gs.skip_optional_emissary()
        
        # P0 recalls
        gs.apply_action_array([4, 0, 0, 0, 0, 0, 0, 0])
        
        # Should restore to 1 (not 2)
        assert player.emissaries == 1


class TestActionDecree:
    """Test ACTION_DECREE (RULES.md Section 5.4) - Requirement 1.6."""
    
    def test_decree_swaps_cards_at_same_position(self):
        """WHEN player uses decree THEN cards at same position SHALL be swapped."""
        gs = GameState.create_initial_state(seed=42)
        complete_draft(gs)
        
        player = gs.players[gs.current_player_idx]
        opponent = gs.players[1 - gs.current_player_idx]
        
        player_card = player.line[2]
        opponent_card = opponent.line[2]
        
        # Use decree on position 2
        obs, reward, done, trunc, info = gs.apply_action_array([5, 2, 0, 0, 0, 0, 0, 0])
        
        # Verify swap occurred
        assert player.line[2] == opponent_card
        assert opponent.line[2] == player_card
    
    def test_decree_swaps_hand_positions(self):
        """WHEN player uses decree on hand position THEN hand cards SHALL be swapped."""
        gs = GameState.create_initial_state(seed=42)
        complete_draft(gs)
        
        player = gs.players[gs.current_player_idx]
        opponent = gs.players[1 - gs.current_player_idx]
        
        player_card = player.hand[2]
        opponent_card = opponent.hand[2]
        
        # Use decree on position 7 (hand position 2)
        obs, reward, done, trunc, info = gs.apply_action_array([5, 7, 0, 0, 0, 0, 0, 0])
        
        # Verify swap occurred
        assert player.hand[2] == opponent_card
        assert opponent.hand[2] == player_card
    
    def test_decree_consumes_emissary(self):
        """WHEN player uses decree THEN one emissary SHALL be consumed."""
        gs = GameState.create_initial_state(seed=42)
        complete_draft(gs)
        
        player = gs.players[gs.current_player_idx]
        initial_emissaries = player.emissaries
        
        # Use decree
        gs.apply_action_array([5, 0, 0, 0, 0, 0, 0, 0])
        
        # Verify emissary consumed
        assert player.emissaries == initial_emissaries - 1
    
    def test_decree_permanently_locks_emissary(self):
        """WHEN player uses decree THEN decree_used flag SHALL be set permanently."""
        gs = GameState.create_initial_state(seed=42)
        complete_draft(gs)
        
        player = gs.players[gs.current_player_idx]
        
        # Use decree
        gs.apply_action_array([5, 0, 0, 0, 0, 0, 0, 0])
        
        # Verify decree_used flag set
        assert player.decree_used == True
    
    def test_decree_only_usable_once_per_game(self):
        """WHEN decree is used THEN it SHALL not be usable again by either player."""
        gs = GameState.create_initial_state(seed=42)
        complete_draft(gs)
        
        # Player 0 uses decree
        gs.apply_action_array([5, 0, 0, 0, 0, 0, 0, 0])
        
        # Player 1 tries to use decree
        legal = gs.get_legal_action_types()
        
        # Decree should not be legal
        assert ACTION_DECREE not in legal

    def test_decree_ends_turn(self):
        """WHEN player uses decree THEN turn SHALL end."""
        gs = GameState.create_initial_state(seed=42)
        complete_draft(gs)
        
        current_player = gs.current_player_idx
        
        # Use decree
        obs, reward, done, trunc, info = gs.apply_action_array([5, 0, 0, 0, 0, 0, 0, 0])
        
        # Turn should end (player switched)
        assert gs.current_player_idx != current_player
    
    def test_decree_fails_without_emissaries(self):
        """WHEN player has no emissaries THEN decree SHALL fail with penalty."""
        gs = GameState.create_initial_state(seed=42)
        complete_draft(gs)
        
        # Remove emissaries
        player = gs.players[gs.current_player_idx]
        player.emissaries = 0
        
        # Try to use decree
        obs, reward, done, trunc, info = gs.apply_action_array([5, 0, 0, 0, 0, 0, 0, 0])
        
        # Should fail with penalty
        assert reward == -0.1
    
    def test_decree_fails_if_already_used(self):
        """WHEN decree already used THEN it SHALL fail with penalty."""
        gs = GameState.create_initial_state(seed=42)
        complete_draft(gs)
        
        # Use decree
        gs.apply_action_array([5, 0, 0, 0, 0, 0, 0, 0])
        
        # Try to use decree again (different player)
        obs, reward, done, trunc, info = gs.apply_action_array([5, 0, 0, 0, 0, 0, 0, 0])
        
        # Should fail with penalty
        assert reward == -0.1
    
    def test_decree_affects_recall_max(self):
        """WHEN player uses decree THEN recall SHALL only restore to 1 emissary."""
        gs = GameState.create_initial_state(seed=42)
        complete_draft(gs)
        
        player = gs.players[0]  # Track player 0
        
        # P0 uses decree (consumes 1 emissary, ends turn)
        gs.apply_action_array([5, 0, 0, 0, 0, 0, 0, 0])
        assert player.emissaries == 1
        
        # P1's turn - skip
        gs.apply_action_array([1, 0, 0, 0, 0, 0, 0, 0])
        gs.skip_optional_emissary()
        
        # P0 uses remaining emissary
        gs.apply_action_array([2, 0, 0, 0, 0, 1, 0, 0])
        gs.apply_action_array([1, 0, 0, 0, 0, 0, 0, 0])
        assert player.emissaries == 0
        
        # P1's turn - skip
        gs.apply_action_array([1, 0, 0, 0, 0, 0, 0, 0])
        gs.skip_optional_emissary()
        
        # P0 recalls
        gs.apply_action_array([4, 0, 0, 0, 0, 0, 0, 0])
        
        # Should only restore to 1
        assert player.emissaries == 1


class TestActionEndGame:
    """Test ACTION_END_GAME (RULES.md Section 7) - Requirement 1.7."""
    
    def test_end_game_not_available_initially(self):
        """WHEN no decks are empty THEN end game SHALL not be available."""
        gs = GameState.create_initial_state(seed=42)
        complete_draft(gs)
        
        # Check legal actions
        legal = gs.get_legal_action_types()
        
        # End game should not be available
        assert ACTION_END_GAME not in legal
        assert gs.ending_available == False
    
    def test_end_game_available_when_one_deck_empty(self):
        """WHEN 1+ decks are empty THEN end game SHALL be available."""
        gs = GameState.create_initial_state(seed=42)
        complete_draft(gs)
        
        # Empty one deck
        gs.river.decks[0] = []
        gs.ending_available = True
        
        # Check legal actions
        legal = gs.get_legal_action_types()
        
        # End game should be available
        assert ACTION_END_GAME in legal
    
    def test_end_game_sets_end_next_turn_flag(self):
        """WHEN player declares end THEN end_next_turn flag SHALL be set."""
        gs = GameState.create_initial_state(seed=42)
        complete_draft(gs)
        
        # Empty one deck and enable ending
        gs.river.decks[0] = []
        gs.ending_available = True
        
        # Declare end
        obs, reward, done, trunc, info = gs.apply_action_array([6, 0, 0, 0, 0, 0, 0, 0])
        
        # Flag should be set
        assert gs.end_next_turn == True
    
    def test_end_game_gives_opponent_final_turn(self):
        """WHEN player declares end THEN opponent SHALL get one final turn."""
        gs = GameState.create_initial_state(seed=42)
        complete_draft(gs)
        
        # Empty one deck and enable ending
        gs.river.decks[0] = []
        gs.ending_available = True
        
        current_player = gs.current_player_idx
        
        # Declare end (this ends the turn and switches to opponent)
        obs, reward, done, trunc, info = gs.apply_action_array([6, 0, 0, 0, 0, 0, 0, 0])
        
        # Should switch to opponent and set end_next_turn
        assert gs.current_player_idx != current_player
        assert gs.end_next_turn == True
        assert done == False  # Game not ended yet
        
        # Opponent takes turn using emissary first (Option B) to avoid optional emissary
        obs, reward, done, trunc, info = gs.apply_action_array([2, 0, 0, 0, 0, 1, 0, 0])  # Swap
        assert gs.must_develop == True
        assert done == False
        
        # Required develop - this should trigger game end
        obs, reward, done, trunc, info = gs.apply_action_array([1, 2, 0, 0, 0, 0, 0, 0])
        
        # Game should end after opponent's turn
        assert done == True
    
    def test_end_game_fails_when_not_available(self):
        """WHEN ending not available THEN end game SHALL fail with penalty."""
        gs = GameState.create_initial_state(seed=42)
        complete_draft(gs)
        
        # Try to end game (no decks empty)
        obs, reward, done, trunc, info = gs.apply_action_array([6, 0, 0, 0, 0, 0, 0, 0])
        
        # Should fail with penalty
        assert reward == -0.1

    def test_auto_end_when_two_decks_empty_after_p1(self):
        """WHEN 2+ decks empty after P1's turn THEN P2 SHALL get final turn."""
        gs = GameState.create_initial_state(seed=42)
        complete_draft(gs)
        
        # Empty two decks
        gs.river.decks[0] = []
        gs.river.decks[1] = []
        
        # P1 (player 0) takes turn using emissary first (Option B) to avoid optional emissary
        assert gs.current_player_idx == 0
        obs, reward, done, trunc, info = gs.apply_action_array([2, 0, 0, 0, 0, 1, 0, 0])  # Swap
        assert gs.must_develop == True
        assert done == False
        
        # Required develop - this should trigger auto-end logic
        obs, reward, done, trunc, info = gs.apply_action_array([1, 2, 0, 0, 0, 0, 0, 0])
        
        # Should set end_next_turn flag and switch to P2
        assert gs.end_next_turn == True
        assert gs.current_player_idx == 1
        assert done == False
        
        # P2 takes final turn using emissary first (Option B)
        obs, reward, done, trunc, info = gs.apply_action_array([2, 0, 0, 0, 0, 1, 0, 0])  # Swap
        assert gs.must_develop == True
        assert done == False
        
        # Required develop - this should end the game
        obs, reward, done, trunc, info = gs.apply_action_array([1, 2, 0, 0, 0, 0, 0, 0])
        
        # Game should end
        assert done == True
    
    def test_auto_end_when_two_decks_empty_after_p2(self):
        """WHEN 2+ decks empty after P2's turn THEN game SHALL end immediately."""
        gs = GameState.create_initial_state(seed=42)
        complete_draft(gs)
        
        # P1 takes turn using emissary first (Option B) to switch to P2
        gs.apply_action_array([2, 0, 0, 0, 0, 1, 0, 0])  # Swap
        gs.apply_action_array([1, 0, 0, 0, 0, 0, 0, 0])  # Develop
        assert gs.current_player_idx == 1
        
        # Empty two decks
        gs.river.decks[0] = []
        gs.river.decks[1] = []
        
        # P2 takes turn using emissary first (Option B)
        obs, reward, done, trunc, info = gs.apply_action_array([2, 0, 0, 0, 0, 1, 0, 0])  # Swap
        assert gs.must_develop == True
        assert done == False
        
        # Required develop - should end immediately since P2 just finished with 2+ decks empty
        obs, reward, done, trunc, info = gs.apply_action_array([1, 2, 0, 0, 0, 0, 0, 0])
        
        # Game should end immediately (P2 completed turn with 2+ decks empty)
        assert done == True
    
    def test_ending_available_updates_after_action(self):
        """WHEN deck becomes empty THEN ending_available SHALL be updated."""
        gs = GameState.create_initial_state(seed=42)
        complete_draft(gs)
        
        # Reduce deck 0 to 1 card
        gs.river.decks[0] = [gs.river.decks[0][0]]
        
        assert gs.ending_available == False
        
        # Develop from deck 0 (will empty it)
        obs, reward, done, trunc, info = gs.apply_action_array([1, 0, 0, 0, 0, 0, 0, 0])
        
        # ending_available should now be True
        assert gs.ending_available == True


class TestActionIntegration:
    """Integration tests for action combinations."""
    
    def test_develop_then_swap_then_develop_next_turn(self):
        """Test complete turn with develop → optional swap."""
        gs = GameState.create_initial_state(seed=42)
        complete_draft(gs)
        
        player = gs.players[gs.current_player_idx]
        initial_emissaries = player.emissaries
        
        # Develop
        gs.apply_action_array([1, 0, 0, 0, 0, 0, 0, 0])
        assert gs.optional_emissary_available == True
        
        # Use optional swap
        gs.apply_action_array([2, 0, 0, 0, 0, 1, 0, 0])
        assert gs.optional_emissary_available == False
        assert player.emissaries == initial_emissaries - 1
        
        # Next turn should work normally
        obs, reward, done, trunc, info = gs.apply_action_array([1, 0, 0, 0, 0, 0, 0, 0])
        assert done == False
    
    def test_swap_then_develop_then_next_turn(self):
        """Test complete turn with swap → required develop."""
        gs = GameState.create_initial_state(seed=42)
        complete_draft(gs)
        
        player = gs.players[gs.current_player_idx]
        initial_emissaries = player.emissaries
        
        # Swap first
        gs.apply_action_array([2, 0, 0, 0, 0, 1, 0, 0])
        assert gs.must_develop == True
        
        # Required develop
        gs.apply_action_array([1, 0, 0, 0, 0, 0, 0, 0])
        assert gs.must_develop == False
        assert player.emissaries == initial_emissaries - 1
        
        # Next turn should work normally
        obs, reward, done, trunc, info = gs.apply_action_array([1, 0, 0, 0, 0, 0, 0, 0])
        assert done == False
    
    def test_multiple_swaps_fill_spots(self):
        """Test that multiple swaps fill all spots."""
        gs = GameState.create_initial_state(seed=42)
        complete_draft(gs)
        
        # Use 3 swaps (filling all spots)
        for i in range(3):
            gs.apply_action_array([2, 0, 0, 0, 0, 1, 0, 0])  # Swap
            gs.apply_action_array([1, 0, 0, 0, 0, 0, 0, 0])  # Develop
        
        # All swap spots should be full
        assert 0 not in gs.available_swaps
        
        # Swap should not be legal
        legal = gs.get_legal_action_types()
        assert ACTION_SWAP not in legal
    
    def test_recall_frees_spots_for_reuse(self):
        """Test that recall frees spots for reuse."""
        gs = GameState.create_initial_state(seed=42)
        complete_draft(gs)
        
        # P0 uses 2 swaps
        gs.apply_action_array([2, 0, 0, 0, 0, 1, 0, 0])  # Swap
        gs.apply_action_array([1, 0, 0, 0, 0, 0, 0, 0])  # Develop (turn ends)
        
        # P1's turn - skip
        gs.apply_action_array([1, 0, 0, 0, 0, 0, 0, 0])
        gs.skip_optional_emissary()
        
        # P0 uses second swap
        gs.apply_action_array([2, 0, 0, 0, 0, 1, 0, 0])
        gs.apply_action_array([1, 0, 0, 0, 0, 0, 0, 0])
        
        # 2 spots should be occupied by P0 (marker 1)
        assert gs.available_swaps.count(1) == 2
        assert gs.available_swaps.count(0) == 1
        
        # P1's turn - skip
        gs.apply_action_array([1, 0, 0, 0, 0, 0, 0, 0])
        gs.skip_optional_emissary()
        
        # P0 recalls
        gs.apply_action_array([4, 0, 0, 0, 0, 0, 0, 0])
        
        # P0's spots should be freed
        assert gs.available_swaps.count(1) == 0
        assert gs.available_swaps.count(0) == 3
        
        # P1's turn - skip
        gs.apply_action_array([1, 0, 0, 0, 0, 0, 0, 0])
        gs.skip_optional_emissary()
        
        # P0 can use swap again
        legal = gs.get_legal_action_types()
        assert ACTION_SWAP in legal


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
