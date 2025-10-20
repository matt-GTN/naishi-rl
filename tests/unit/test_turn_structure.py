"""
Unit tests for GameState turn structure (Task 34).

Tests the turn state tracking mechanisms that implement RULES.md Section 4:
- Option A: Develop → Optional Emissary
- Option B: Emissary → Required Develop
- Option C: Other actions (Recall, Decree, End)

Requirements tested: 1.2, 4.1-4.8
"""

import pytest
from naishi_core.game_logic import GameState, ACTION_DEVELOP, ACTION_SWAP, ACTION_DISCARD, ACTION_RECALL, ACTION_DECREE, ACTION_END_GAME


class TestClearTurnState:
    """Test clear_turn_state() functionality (Requirement 4.8)."""
    
    def test_clear_turn_state_resets_all_flags(self):
        """WHEN clear_turn_state() is called THEN all turn-specific flags SHALL be reset."""
        gs = GameState.create_initial_state(seed=42)
        # Complete draft
        gs.apply_action_array([0, 0, 0, 0, 0, 0, 0, 0])  # P0 draft
        gs.apply_action_array([0, 1, 0, 0, 0, 0, 0, 0])  # P1 draft
        
        # Set flags manually to test clearing
        gs.optional_emissary_available = True
        gs.must_develop = True
        gs.last_action_type = ACTION_DEVELOP
        
        # Clear turn state
        gs.clear_turn_state()
        
        # Verify all flags are reset
        assert gs.optional_emissary_available == False
        assert gs.must_develop == False
        assert gs.last_action_type is None
    
    def test_clear_turn_state_called_on_player_switch(self):
        """WHEN player switches THEN clear_turn_state() SHALL be called automatically."""
        gs = GameState.create_initial_state(seed=42)
        # Complete draft
        gs.apply_action_array([0, 0, 0, 0, 0, 0, 0, 0])
        gs.apply_action_array([0, 1, 0, 0, 0, 0, 0, 0])
        
        # Set a flag
        gs.optional_emissary_available = True
        
        # Take an action that ends the turn (recall)
        gs.apply_action_array([4, 0, 0, 0, 0, 0, 0, 0])  # ACTION_RECALL
        
        # Verify flag was cleared when player switched
        assert gs.optional_emissary_available == False
        assert gs.must_develop == False
        assert gs.last_action_type is None


class TestOptionalEmissaryAvailable:
    """Test optional_emissary_available flag lifecycle (Requirements 4.1, 4.3)."""
    
    def test_optional_emissary_set_after_develop_with_emissaries(self):
        """WHEN player develops AND has emissaries AND spots available THEN optional_emissary_available SHALL be True."""
        gs = GameState.create_initial_state(seed=42)
        # Complete draft
        gs.apply_action_array([0, 0, 0, 0, 0, 0, 0, 0])
        gs.apply_action_array([0, 1, 0, 0, 0, 0, 0, 0])
        
        # Verify player has emissaries and spots available
        player = gs.players[gs.current_player_idx]
        assert player.emissaries == 2
        assert 0 in gs.available_swaps
        assert 0 in gs.available_discards
        
        # Develop (Option A)
        obs, reward, done, trunc, info = gs.apply_action_array([1, 0, 0, 0, 0, 0, 0, 0])  # ACTION_DEVELOP pos 0
        
        # Verify optional emissary is available
        assert gs.optional_emissary_available == True
        assert done == False  # Turn should not end yet
    
    def test_optional_emissary_not_set_without_emissaries(self):
        """WHEN player develops AND has no emissaries THEN optional_emissary_available SHALL be False."""
        gs = GameState.create_initial_state(seed=42)
        # Complete draft
        gs.apply_action_array([0, 0, 0, 0, 0, 0, 0, 0])
        gs.apply_action_array([0, 1, 0, 0, 0, 0, 0, 0])
        
        # Use all emissaries
        player = gs.players[gs.current_player_idx]
        player.emissaries = 0
        
        # Develop
        obs, reward, done, trunc, info = gs.apply_action_array([1, 0, 0, 0, 0, 0, 0, 0])
        
        # Verify optional emissary is NOT available
        assert gs.optional_emissary_available == False
        assert done == False  # Turn ends (player switched)
    
    def test_optional_emissary_not_set_without_spots(self):
        """WHEN player develops AND all spots are full THEN optional_emissary_available SHALL be False."""
        gs = GameState.create_initial_state(seed=42)
        # Complete draft
        gs.apply_action_array([0, 0, 0, 0, 0, 0, 0, 0])
        gs.apply_action_array([0, 1, 0, 0, 0, 0, 0, 0])
        
        # Fill all spots
        gs.available_swaps = [1, 1, 1]  # All swap spots taken
        gs.available_discards = [1, 1]  # All discard spots taken
        
        # Develop
        obs, reward, done, trunc, info = gs.apply_action_array([1, 0, 0, 0, 0, 0, 0, 0])
        
        # Verify optional emissary is NOT available
        assert gs.optional_emissary_available == False
    
    def test_optional_emissary_cleared_after_use(self):
        """WHEN optional emissary is used THEN flag SHALL be cleared and turn SHALL end."""
        gs = GameState.create_initial_state(seed=42)
        # Complete draft
        gs.apply_action_array([0, 0, 0, 0, 0, 0, 0, 0])
        gs.apply_action_array([0, 1, 0, 0, 0, 0, 0, 0])
        
        # Develop to trigger optional emissary
        gs.apply_action_array([1, 0, 0, 0, 0, 0, 0, 0])
        assert gs.optional_emissary_available == True
        
        current_player = gs.current_player_idx
        
        # Use optional emissary (swap in hand)
        obs, reward, done, trunc, info = gs.apply_action_array([2, 0, 0, 0, 0, 1, 0, 0])  # ACTION_SWAP hand
        
        # Verify flag cleared and turn ended (player switched)
        assert gs.optional_emissary_available == False
        assert gs.current_player_idx != current_player  # Player switched
    
    def test_optional_emissary_skip(self):
        """WHEN optional emissary is available AND player skips THEN turn SHALL end."""
        gs = GameState.create_initial_state(seed=42)
        # Complete draft
        gs.apply_action_array([0, 0, 0, 0, 0, 0, 0, 0])
        gs.apply_action_array([0, 1, 0, 0, 0, 0, 0, 0])
        
        # Develop to trigger optional emissary
        gs.apply_action_array([1, 0, 0, 0, 0, 0, 0, 0])
        assert gs.optional_emissary_available == True
        
        current_player = gs.current_player_idx
        
        # Skip optional emissary
        obs, reward, done, trunc, info = gs.skip_optional_emissary()
        
        # Verify flag cleared and turn ended
        assert gs.optional_emissary_available == False
        assert gs.current_player_idx != current_player  # Player switched


class TestMustDevelopFlag:
    """Test must_develop flag lifecycle (Requirements 4.2, 4.7)."""
    
    def test_must_develop_set_after_emissary_first(self):
        """WHEN player uses emissary first THEN must_develop SHALL be True and turn SHALL NOT end."""
        gs = GameState.create_initial_state(seed=42)
        # Complete draft
        gs.apply_action_array([0, 0, 0, 0, 0, 0, 0, 0])
        gs.apply_action_array([0, 1, 0, 0, 0, 0, 0, 0])
        
        # Use emissary first (swap in hand) - Option B
        obs, reward, done, trunc, info = gs.apply_action_array([2, 0, 0, 0, 0, 1, 0, 0])  # ACTION_SWAP
        
        # Verify must_develop is set and turn didn't end
        assert gs.must_develop == True
        assert done == False
        assert gs.current_player_idx == 0  # Same player
    
    def test_must_develop_cleared_after_develop(self):
        """WHEN must_develop is True AND player develops THEN flag SHALL be cleared and turn SHALL end."""
        gs = GameState.create_initial_state(seed=42)
        # Complete draft
        gs.apply_action_array([0, 0, 0, 0, 0, 0, 0, 0])
        gs.apply_action_array([0, 1, 0, 0, 0, 0, 0, 0])
        
        # Use emissary first to set must_develop
        gs.apply_action_array([2, 0, 0, 0, 0, 1, 0, 0])
        assert gs.must_develop == True
        
        current_player = gs.current_player_idx
        
        # Now develop (required)
        obs, reward, done, trunc, info = gs.apply_action_array([1, 0, 0, 0, 0, 0, 0, 0])  # ACTION_DEVELOP
        
        # Verify flag cleared and turn ended
        assert gs.must_develop == False
        assert gs.current_player_idx != current_player  # Player switched
    
    def test_must_develop_with_discard_first(self):
        """WHEN player discards first THEN must_develop SHALL be True."""
        gs = GameState.create_initial_state(seed=42)
        # Complete draft
        gs.apply_action_array([0, 0, 0, 0, 0, 0, 0, 0])
        gs.apply_action_array([0, 1, 0, 0, 0, 0, 0, 0])
        
        # Use discard first (Option B)
        obs, reward, done, trunc, info = gs.apply_action_array([3, 0, 0, 0, 0, 0, 0, 1])  # ACTION_DISCARD
        
        # Verify must_develop is set
        assert gs.must_develop == True
        assert done == False


class TestGetLegalActionTypesWithTurnState:
    """Test get_legal_action_types() with turn state (Requirements 4.4, 4.5, 4.6, 4.7)."""
    
    def test_only_develop_legal_when_must_develop(self):
        """WHEN must_develop is True THEN only ACTION_DEVELOP SHALL be legal."""
        gs = GameState.create_initial_state(seed=42)
        # Complete draft
        gs.apply_action_array([0, 0, 0, 0, 0, 0, 0, 0])
        gs.apply_action_array([0, 1, 0, 0, 0, 0, 0, 0])
        
        # Use emissary first to set must_develop
        gs.apply_action_array([2, 0, 0, 0, 0, 1, 0, 0])
        assert gs.must_develop == True
        
        # Get legal actions
        legal = gs.get_legal_action_types()
        
        # Only develop should be legal
        assert legal == [ACTION_DEVELOP]
        assert ACTION_SWAP not in legal
        assert ACTION_DISCARD not in legal
        assert ACTION_RECALL not in legal
        assert ACTION_DECREE not in legal
        assert ACTION_END_GAME not in legal
    
    def test_only_emissary_legal_when_optional_emissary_available(self):
        """WHEN optional_emissary_available is True THEN only emissary actions SHALL be legal."""
        gs = GameState.create_initial_state(seed=42)
        # Complete draft
        gs.apply_action_array([0, 0, 0, 0, 0, 0, 0, 0])
        gs.apply_action_array([0, 1, 0, 0, 0, 0, 0, 0])
        
        # Develop to trigger optional emissary
        gs.apply_action_array([1, 0, 0, 0, 0, 0, 0, 0])
        assert gs.optional_emissary_available == True
        
        # Get legal actions
        legal = gs.get_legal_action_types()
        
        # Only emissary actions should be legal (swap and discard)
        assert ACTION_SWAP in legal
        assert ACTION_DISCARD in legal
        assert ACTION_DEVELOP not in legal
        assert ACTION_RECALL not in legal
        assert ACTION_DECREE not in legal
        assert ACTION_END_GAME not in legal
    
    def test_all_actions_legal_in_normal_state(self):
        """WHEN no turn state flags are set THEN all normally available actions SHALL be legal."""
        gs = GameState.create_initial_state(seed=42)
        # Complete draft
        gs.apply_action_array([0, 0, 0, 0, 0, 0, 0, 0])
        gs.apply_action_array([0, 1, 0, 0, 0, 0, 0, 0])
        
        # Get legal actions in normal state
        legal = gs.get_legal_action_types()
        
        # Should have develop, emissary actions, recall, decree
        assert ACTION_DEVELOP in legal
        assert ACTION_SWAP in legal
        assert ACTION_DISCARD in legal
        assert ACTION_RECALL not in legal  # Player has max emissaries
        assert ACTION_DECREE in legal
        # ACTION_END_GAME not available yet (no empty decks)
    
    def test_no_emissary_actions_without_emissaries_in_optional_state(self):
        """WHEN optional_emissary_available AND player has no emissaries THEN no actions SHALL be legal."""
        gs = GameState.create_initial_state(seed=42)
        # Complete draft
        gs.apply_action_array([0, 0, 0, 0, 0, 0, 0, 0])
        gs.apply_action_array([0, 1, 0, 0, 0, 0, 0, 0])
        
        # Remove emissaries
        gs.players[gs.current_player_idx].emissaries = 0
        
        # Manually set optional_emissary_available (shouldn't happen in practice)
        gs.optional_emissary_available = True
        
        # Get legal actions
        legal = gs.get_legal_action_types()
        
        # No actions should be legal (player should skip)
        assert legal == []
    
    def test_no_swap_when_swap_spots_full_in_optional_state(self):
        """WHEN optional_emissary_available AND swap spots full THEN only discard SHALL be legal."""
        gs = GameState.create_initial_state(seed=42)
        # Complete draft
        gs.apply_action_array([0, 0, 0, 0, 0, 0, 0, 0])
        gs.apply_action_array([0, 1, 0, 0, 0, 0, 0, 0])
        
        # Fill swap spots
        gs.available_swaps = [1, 1, 1]
        
        # Develop to trigger optional emissary
        gs.apply_action_array([1, 0, 0, 0, 0, 0, 0, 0])
        assert gs.optional_emissary_available == True
        
        # Get legal actions
        legal = gs.get_legal_action_types()
        
        # Only discard should be legal
        assert ACTION_DISCARD in legal
        assert ACTION_SWAP not in legal


class TestLastActionType:
    """Test last_action_type tracking."""
    
    def test_last_action_type_set_on_action(self):
        """WHEN an action is applied THEN last_action_type SHALL be set."""
        gs = GameState.create_initial_state(seed=42)
        # Complete draft
        gs.apply_action_array([0, 0, 0, 0, 0, 0, 0, 0])
        gs.apply_action_array([0, 1, 0, 0, 0, 0, 0, 0])
        
        # Apply develop action
        gs.apply_action_array([1, 0, 0, 0, 0, 0, 0, 0])
        
        # Verify last_action_type is set
        assert gs.last_action_type == ACTION_DEVELOP
    
    def test_last_action_type_cleared_on_turn_switch(self):
        """WHEN turn switches THEN last_action_type SHALL be cleared."""
        gs = GameState.create_initial_state(seed=42)
        # Complete draft
        gs.apply_action_array([0, 0, 0, 0, 0, 0, 0, 0])
        gs.apply_action_array([0, 1, 0, 0, 0, 0, 0, 0])
        
        # Apply action that ends turn
        gs.apply_action_array([4, 0, 0, 0, 0, 0, 0, 0])  # ACTION_RECALL
        
        # Verify last_action_type is cleared
        assert gs.last_action_type is None


class TestTurnStructureIntegration:
    """Integration tests for complete turn structure flows."""
    
    def test_option_a_develop_then_optional_emissary(self):
        """Test Option A: Develop → Optional Emissary flow."""
        gs = GameState.create_initial_state(seed=42)
        # Complete draft
        gs.apply_action_array([0, 0, 0, 0, 0, 0, 0, 0])
        gs.apply_action_array([0, 1, 0, 0, 0, 0, 0, 0])
        
        current_player = gs.current_player_idx
        
        # Step 1: Develop
        obs, reward, done, trunc, info = gs.apply_action_array([1, 0, 0, 0, 0, 0, 0, 0])
        assert gs.optional_emissary_available == True
        assert gs.current_player_idx == current_player  # Same player
        assert done == False
        
        # Step 2: Use optional emissary
        obs, reward, done, trunc, info = gs.apply_action_array([2, 0, 0, 0, 0, 1, 0, 0])
        assert gs.optional_emissary_available == False
        assert gs.current_player_idx != current_player  # Player switched
    
    def test_option_a_develop_then_skip(self):
        """Test Option A: Develop → Skip optional emissary."""
        gs = GameState.create_initial_state(seed=42)
        # Complete draft
        gs.apply_action_array([0, 0, 0, 0, 0, 0, 0, 0])
        gs.apply_action_array([0, 1, 0, 0, 0, 0, 0, 0])
        
        current_player = gs.current_player_idx
        
        # Step 1: Develop
        gs.apply_action_array([1, 0, 0, 0, 0, 0, 0, 0])
        assert gs.optional_emissary_available == True
        
        # Step 2: Skip optional emissary
        obs, reward, done, trunc, info = gs.skip_optional_emissary()
        assert gs.optional_emissary_available == False
        assert gs.current_player_idx != current_player  # Player switched
    
    def test_option_b_emissary_then_required_develop(self):
        """Test Option B: Emissary → Required Develop flow."""
        gs = GameState.create_initial_state(seed=42)
        # Complete draft
        gs.apply_action_array([0, 0, 0, 0, 0, 0, 0, 0])
        gs.apply_action_array([0, 1, 0, 0, 0, 0, 0, 0])
        
        current_player = gs.current_player_idx
        
        # Step 1: Use emissary first
        obs, reward, done, trunc, info = gs.apply_action_array([2, 0, 0, 0, 0, 1, 0, 0])
        assert gs.must_develop == True
        assert gs.current_player_idx == current_player  # Same player
        assert done == False
        
        # Verify only develop is legal
        legal = gs.get_legal_action_types()
        assert legal == [ACTION_DEVELOP]
        
        # Step 2: Required develop
        obs, reward, done, trunc, info = gs.apply_action_array([1, 0, 0, 0, 0, 0, 0, 0])
        assert gs.must_develop == False
        assert gs.current_player_idx != current_player  # Player switched
    
    def test_option_c_other_actions_end_turn(self):
        """Test Option C: Other actions (Recall, Decree, End) end turn immediately."""
        gs = GameState.create_initial_state(seed=42)
        # Complete draft
        gs.apply_action_array([0, 0, 0, 0, 0, 0, 0, 0])
        gs.apply_action_array([0, 1, 0, 0, 0, 0, 0, 0])
        
        # Use an emissary to enable recall
        gs.apply_action_array([2, 0, 0, 0, 0, 1, 0, 0])  # Swap
        gs.apply_action_array([1, 0, 0, 0, 0, 0, 0, 0])  # Required develop
        
        current_player = gs.current_player_idx
        
        # Use recall (Option C)
        obs, reward, done, trunc, info = gs.apply_action_array([4, 0, 0, 0, 0, 0, 0, 0])
        
        # Turn should end immediately
        assert gs.current_player_idx != current_player  # Player switched
        assert gs.optional_emissary_available == False
        assert gs.must_develop == False


class TestCanUseOptionalEmissary:
    """Test _can_use_optional_emissary() helper method."""
    
    def test_can_use_with_emissaries_and_spots(self):
        """WHEN player has emissaries AND spots available THEN _can_use_optional_emissary SHALL return True."""
        gs = GameState.create_initial_state(seed=42)
        # Complete draft
        gs.apply_action_array([0, 0, 0, 0, 0, 0, 0, 0])
        gs.apply_action_array([0, 1, 0, 0, 0, 0, 0, 0])
        
        assert gs._can_use_optional_emissary() == True
    
    def test_cannot_use_without_emissaries(self):
        """WHEN player has no emissaries THEN _can_use_optional_emissary SHALL return False."""
        gs = GameState.create_initial_state(seed=42)
        # Complete draft
        gs.apply_action_array([0, 0, 0, 0, 0, 0, 0, 0])
        gs.apply_action_array([0, 1, 0, 0, 0, 0, 0, 0])
        
        gs.players[gs.current_player_idx].emissaries = 0
        
        assert gs._can_use_optional_emissary() == False
    
    def test_cannot_use_without_spots(self):
        """WHEN all spots are full THEN _can_use_optional_emissary SHALL return False."""
        gs = GameState.create_initial_state(seed=42)
        # Complete draft
        gs.apply_action_array([0, 0, 0, 0, 0, 0, 0, 0])
        gs.apply_action_array([0, 1, 0, 0, 0, 0, 0, 0])
        
        gs.available_swaps = [1, 1, 1]
        gs.available_discards = [1, 1]
        
        assert gs._can_use_optional_emissary() == False
    
    def test_can_use_with_only_swap_spots(self):
        """WHEN only swap spots available THEN _can_use_optional_emissary SHALL return True."""
        gs = GameState.create_initial_state(seed=42)
        # Complete draft
        gs.apply_action_array([0, 0, 0, 0, 0, 0, 0, 0])
        gs.apply_action_array([0, 1, 0, 0, 0, 0, 0, 0])
        
        gs.available_discards = [1, 1]  # Fill discard spots
        
        assert gs._can_use_optional_emissary() == True
    
    def test_can_use_with_only_discard_spots(self):
        """WHEN only discard spots available THEN _can_use_optional_emissary SHALL return True."""
        gs = GameState.create_initial_state(seed=42)
        # Complete draft
        gs.apply_action_array([0, 0, 0, 0, 0, 0, 0, 0])
        gs.apply_action_array([0, 1, 0, 0, 0, 0, 0, 0])
        
        gs.available_swaps = [1, 1, 1]  # Fill swap spots
        
        assert gs._can_use_optional_emissary() == True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
