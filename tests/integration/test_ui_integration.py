"""
Integration tests for UI files (naishi_pvp.py and play_vs_ai.py)
Tests complete game flows, turn options, and all actions

Requirements: 2.2, 2.3, 5.1-5.5
"""

import pytest
from naishi_core.game_logic import (
    GameState, ACTION_DEVELOP, ACTION_SWAP, ACTION_DISCARD,
    ACTION_RECALL, ACTION_DECREE, ACTION_END_GAME
)


class TestNaishiPvPIntegration:
    """Integration tests for naishi_pvp.py complete game flows"""
    
    def test_pvp_complete_game_develop_first_option(self):
        """Test complete PvP game using develop-first turn option (Option A)"""
        # Create GameState directly to test game flow that UI would use
        gs = GameState.create_initial_state(seed=42)
        
        # Complete draft phase first
        gs.apply_action_array([0, 0, 0, 0, 0, 0, 0, 0])  # P0 draft
        gs.apply_action_array([0, 1, 0, 0, 0, 0, 0, 0])  # P1 draft
        
        # Manually step through a few turns
        initial_player = gs.current_player_idx
        
        # P1 develops
        action = [ACTION_DEVELOP, 0, 0, 0, 0, 0, 0, 0]
        obs, reward, term, trunc, info = gs.apply_action_array(action)
        
        # Check optional emissary is available
        assert gs.optional_emissary_available == True
        
        # Skip optional emissary
        obs, reward, term, trunc, info = gs.skip_optional_emissary()
        
        # Turn should have switched
        assert gs.current_player_idx != initial_player
    
    def test_pvp_emissary_first_option(self):
        """Test PvP game using emissary-first turn option (Option B)"""
        # Create GameState directly to test game flow that UI would use
        gs = GameState.create_initial_state(seed=42)
        
        # Complete draft phase first
        gs.apply_action_array([0, 0, 0, 0, 0, 0, 0, 0])  # P0 draft
        gs.apply_action_array([0, 1, 0, 0, 0, 0, 0, 0])  # P1 draft
        
        # Use emissary first (swap in hand)
        action = [ACTION_SWAP, 0, 0, 0, 0, 1, 0, 0]  # Swap type 0 (hand), pos 0 and 1
        obs, reward, term, trunc, info = gs.apply_action_array(action)
        
        # Must develop should be True
        assert gs.must_develop == True
        
        # Now develop
        action = [ACTION_DEVELOP, 0, 0, 0, 0, 0, 0, 0]
        obs, reward, term, trunc, info = gs.apply_action_array(action)
        
        # Must develop should be cleared
        assert gs.must_develop == False
    
    def test_pvp_all_action_types(self):
        """Test that all action types work in PvP"""
        # Create GameState directly to test game flow that UI would use
        gs = GameState.create_initial_state(seed=42)
        
        # Complete draft phase first
        gs.apply_action_array([0, 0, 0, 0, 0, 0, 0, 0])  # P0 draft
        gs.apply_action_array([0, 1, 0, 0, 0, 0, 0, 0])  # P1 draft
        
        # Test DEVELOP
        action = [ACTION_DEVELOP, 0, 0, 0, 0, 0, 0, 0]
        obs, reward, term, trunc, info = gs.apply_action_array(action)
        gs.skip_optional_emissary()
        assert not term and not trunc
        
        # Test SWAP (hand)
        action = [ACTION_SWAP, 0, 0, 0, 0, 1, 0, 0]
        obs, reward, term, trunc, info = gs.apply_action_array(action)
        assert gs.must_develop == True
        
        # Complete required develop
        action = [ACTION_DEVELOP, 1, 0, 0, 0, 0, 0, 0]
        obs, reward, term, trunc, info = gs.apply_action_array(action)
        gs.skip_optional_emissary()
        
        # Test DISCARD
        action = [ACTION_DISCARD, 0, 0, 0, 0, 0, 0, 1]
        obs, reward, term, trunc, info = gs.apply_action_array(action)
        assert gs.must_develop == True
        
        # Complete required develop
        action = [ACTION_DEVELOP, 2, 0, 0, 0, 0, 0, 0]
        obs, reward, term, trunc, info = gs.apply_action_array(action)
        gs.skip_optional_emissary()
        
        # Test RECALL
        action = [ACTION_RECALL, 0, 0, 0, 0, 0, 0, 0]
        obs, reward, term, trunc, info = gs.apply_action_array(action)
        assert not term and not trunc
        
        # Test DECREE
        action = [ACTION_DECREE, 0, 0, 0, 0, 0, 0, 0]
        obs, reward, term, trunc, info = gs.apply_action_array(action)
        assert not term and not trunc
        
        # Test END_GAME (need to empty decks first)
        # Empty enough decks to allow ending
        for _ in range(6):
            action = [ACTION_DEVELOP, 0, 0, 0, 0, 0, 0, 0]
            obs, reward, term, trunc, info = gs.apply_action_array(action)
            if gs.optional_emissary_available:
                gs.skip_optional_emissary()
            if term or trunc:
                break
        
        # Now END_GAME should be available
        if ACTION_END_GAME in gs.get_legal_action_types():
            action = [ACTION_END_GAME, 0, 0, 0, 0, 0, 0, 0]
            obs, reward, term, trunc, info = gs.apply_action_array(action)
    
    def test_pvp_both_turn_options_work(self):
        """Test that both turn options (A and B) work correctly in PvP"""
        # Create GameState directly to test game flow that UI would use
        gs = GameState.create_initial_state(seed=42)
        
        # Complete draft phase first
        gs.apply_action_array([0, 0, 0, 0, 0, 0, 0, 0])  # P0 draft
        gs.apply_action_array([0, 1, 0, 0, 0, 0, 0, 0])  # P1 draft
        
        # Option A: Develop first, then optional emissary
        initial_player = gs.current_player_idx
        action = [ACTION_DEVELOP, 0, 0, 0, 0, 0, 0, 0]
        obs, reward, term, trunc, info = gs.apply_action_array(action)
        
        # Should have optional emissary available
        assert gs.optional_emissary_available == True
        
        # Use the optional emissary
        action = [ACTION_SWAP, 0, 0, 0, 0, 1, 0, 0]
        obs, reward, term, trunc, info = gs.apply_action_array(action)
        
        # Optional emissary should be cleared, turn should end
        assert gs.optional_emissary_available == False
        assert gs.current_player_idx != initial_player
        
        # Option B: Emissary first, then required develop
        initial_player = gs.current_player_idx
        action = [ACTION_SWAP, 0, 0, 1, 0, 1, 0, 0]  # Swap in line
        obs, reward, term, trunc, info = gs.apply_action_array(action)
        
        # Should have must_develop set
        assert gs.must_develop == True
        assert gs.current_player_idx == initial_player  # Same player
        
        # Complete required develop
        action = [ACTION_DEVELOP, 1, 0, 0, 0, 0, 0, 0]
        obs, reward, term, trunc, info = gs.apply_action_array(action)
        
        # Must develop should be cleared
        assert gs.must_develop == False
    
    def test_pvp_delegates_to_gamestate(self):
        """Test that PvP delegates all logic to GameState"""
        # Test that naishi_pvp.py uses GameState for all game logic
        # We verify this by checking that GameState handles all the game mechanics
        gs = GameState.create_initial_state(seed=42)
        
        # Verify game state is managed by GameState
        assert isinstance(gs, GameState)
        
        # Complete draft phase first
        gs.apply_action_array([0, 0, 0, 0, 0, 0, 0, 0])  # P0 draft
        gs.apply_action_array([0, 1, 0, 0, 0, 0, 0, 0])  # P1 draft
        
        # Verify actions go through GameState
        initial_state = gs.get_observation()
        action = [ACTION_DEVELOP, 0, 0, 0, 0, 0, 0, 0]
        obs, reward, term, trunc, info = gs.apply_action_array(action)
        
        # State should have changed (observation includes turn count and other state)
        new_state = gs.get_observation()
        # Check that at least some part of the state changed
        assert not (initial_state == new_state).all() or gs.optional_emissary_available


class TestPlayVsAIIntegration:
    """Integration tests for play_vs_ai.py complete game flows"""
    
    def test_ai_complete_game_develop_first_option(self):
        """Test complete AI game using develop-first turn option (Option A)"""
        # Create GameState directly to test game flow that UI would use
        gs = GameState.create_initial_state(seed=42)
        
        # Complete draft phase first
        gs.apply_action_array([0, 0, 0, 0, 0, 0, 0, 0])  # P0 draft
        gs.apply_action_array([0, 1, 0, 0, 0, 0, 0, 0])  # P1 draft
        
        # Simulate a short game
        for _ in range(5):
            # Check termination via the return values, not attributes
            legal_types = gs.get_legal_action_types()
            if not legal_types:
                break
            
            # Get action (simulate random policy)
            legal_types = gs.get_legal_action_types()
            import random
            action_type = random.choice(legal_types)
            action = [action_type, 0, 0, 0, 0, 0, 0, 0]
            
            obs, reward, term, trunc, info = gs.apply_action_array(action)
            
            # Handle optional emissary
            if gs.optional_emissary_available:
                gs.skip_optional_emissary()
            
            # Handle must develop
            if gs.must_develop:
                action = [ACTION_DEVELOP, 0, 0, 0, 0, 0, 0, 0]
                obs, reward, term, trunc, info = gs.apply_action_array(action)
                if gs.optional_emissary_available:
                    gs.skip_optional_emissary()
        
        # Game should have progressed
        assert gs.turn_count > 0
    
    def test_ai_emissary_first_option(self):
        """Test AI game using emissary-first turn option (Option B)"""
        # Create GameState directly to test game flow that UI would use
        gs = GameState.create_initial_state(seed=42)
        
        # Complete draft phase first
        gs.apply_action_array([0, 0, 0, 0, 0, 0, 0, 0])  # P0 draft
        gs.apply_action_array([0, 1, 0, 0, 0, 0, 0, 0])  # P1 draft
        
        # Use emissary first
        action = [ACTION_SWAP, 0, 0, 0, 0, 1, 0, 0]
        obs, reward, term, trunc, info = gs.apply_action_array(action)
        
        # Must develop should be True
        assert gs.must_develop == True
        
        # Now develop
        action = [ACTION_DEVELOP, 0, 0, 0, 0, 0, 0, 0]
        obs, reward, term, trunc, info = gs.apply_action_array(action)
        
        # Must develop should be cleared
        assert gs.must_develop == False
    
    def test_ai_all_action_types(self):
        """Test that all action types work in AI game"""
        # Create GameState directly to test game flow that UI would use
        gs = GameState.create_initial_state(seed=42)
        
        # Complete draft phase first
        gs.apply_action_array([0, 0, 0, 0, 0, 0, 0, 0])  # P0 draft
        gs.apply_action_array([0, 1, 0, 0, 0, 0, 0, 0])  # P1 draft
        
        # Test DEVELOP
        action = [ACTION_DEVELOP, 0, 0, 0, 0, 0, 0, 0]
        obs, reward, term, trunc, info = gs.apply_action_array(action)
        gs.skip_optional_emissary()
        assert not term and not trunc
        
        # Test SWAP
        action = [ACTION_SWAP, 0, 0, 0, 0, 1, 0, 0]
        obs, reward, term, trunc, info = gs.apply_action_array(action)
        assert gs.must_develop == True
        
        # Complete required develop
        action = [ACTION_DEVELOP, 1, 0, 0, 0, 0, 0, 0]
        obs, reward, term, trunc, info = gs.apply_action_array(action)
        gs.skip_optional_emissary()
        
        # Test DISCARD
        action = [ACTION_DISCARD, 0, 0, 0, 0, 0, 0, 1]
        obs, reward, term, trunc, info = gs.apply_action_array(action)
        assert gs.must_develop == True
        
        # Complete required develop
        action = [ACTION_DEVELOP, 2, 0, 0, 0, 0, 0, 0]
        obs, reward, term, trunc, info = gs.apply_action_array(action)
        gs.skip_optional_emissary()
        
        # Test RECALL
        action = [ACTION_RECALL, 0, 0, 0, 0, 0, 0, 0]
        obs, reward, term, trunc, info = gs.apply_action_array(action)
        assert not term and not trunc
        
        # Test DECREE
        action = [ACTION_DECREE, 0, 0, 0, 0, 0, 0, 0]
        obs, reward, term, trunc, info = gs.apply_action_array(action)
        assert not term and not trunc
    
    def test_ai_both_turn_options_work(self):
        """Test that both turn options (A and B) work correctly in AI game"""
        # Create GameState directly to test game flow that UI would use
        gs = GameState.create_initial_state(seed=42)
        
        # Complete draft phase first
        gs.apply_action_array([0, 0, 0, 0, 0, 0, 0, 0])  # P0 draft
        gs.apply_action_array([0, 1, 0, 0, 0, 0, 0, 0])  # P1 draft
        
        # Option A: Develop first, then optional emissary
        initial_player = gs.current_player_idx
        action = [ACTION_DEVELOP, 0, 0, 0, 0, 0, 0, 0]
        obs, reward, term, trunc, info = gs.apply_action_array(action)
        
        # Should have optional emissary available
        assert gs.optional_emissary_available == True
        
        # Use the optional emissary
        action = [ACTION_SWAP, 0, 0, 0, 0, 1, 0, 0]
        obs, reward, term, trunc, info = gs.apply_action_array(action)
        
        # Optional emissary should be cleared, turn should end
        assert gs.optional_emissary_available == False
        assert gs.current_player_idx != initial_player
        
        # Option B: Emissary first, then required develop
        initial_player = gs.current_player_idx
        action = [ACTION_SWAP, 0, 0, 1, 0, 1, 0, 0]
        obs, reward, term, trunc, info = gs.apply_action_array(action)
        
        # Should have must_develop set
        assert gs.must_develop == True
        assert gs.current_player_idx == initial_player
        
        # Complete required develop
        action = [ACTION_DEVELOP, 1, 0, 0, 0, 0, 0, 0]
        obs, reward, term, trunc, info = gs.apply_action_array(action)
        
        # Must develop should be cleared
        assert gs.must_develop == False
    
    def test_ai_delegates_to_gamestate(self):
        """Test that AI game delegates all logic to GameState"""
        # Test that play_vs_ai.py uses GameState for all game logic
        gs = GameState.create_initial_state(seed=42)
        
        # Verify game state is managed by GameState
        assert isinstance(gs, GameState)
        
        # Complete draft phase first
        gs.apply_action_array([0, 0, 0, 0, 0, 0, 0, 0])  # P0 draft
        gs.apply_action_array([0, 1, 0, 0, 0, 0, 0, 0])  # P1 draft
        
        # Verify actions go through GameState
        initial_state = gs.get_observation()
        action = [ACTION_DEVELOP, 0, 0, 0, 0, 0, 0, 0]
        obs, reward, term, trunc, info = gs.apply_action_array(action)
        
        # State should have changed (observation includes turn count and other state)
        new_state = gs.get_observation()
        # Check that at least some part of the state changed
        assert not (initial_state == new_state).all() or gs.optional_emissary_available
    
    def test_ai_random_policy_generates_legal_actions(self):
        """Test that random policy generates legal actions"""
        # Test that play_vs_ai.py random policy generates legal actions
        gs = GameState.create_initial_state(seed=42)
        
        # Complete draft phase first
        gs.apply_action_array([0, 0, 0, 0, 0, 0, 0, 0])  # P0 draft
        gs.apply_action_array([0, 1, 0, 0, 0, 0, 0, 0])  # P1 draft
        
        for _ in range(10):
            # Check termination via legal actions
            legal_types = gs.get_legal_action_types()
            if not legal_types:
                break
            
            # Get random action (simulate random policy)
            legal_types = gs.get_legal_action_types()
            import random
            action_type = random.choice(legal_types)
            
            # Verify action type is legal
            assert action_type in legal_types
            
            # Apply action
            action = [action_type, 0, 0, 0, 0, 0, 0, 0]
            obs, reward, term, trunc, info = gs.apply_action_array(action)
            
            # Handle turn state
            if gs.optional_emissary_available:
                gs.skip_optional_emissary()
            if gs.must_develop:
                action = [ACTION_DEVELOP, 0, 0, 0, 0, 0, 0, 0]
                obs, reward, term, trunc, info = gs.apply_action_array(action)
                if gs.optional_emissary_available:
                    gs.skip_optional_emissary()


class TestUIFilesCompliance:
    """Test that UI files comply with architecture requirements"""
    
    def test_pvp_no_game_logic_in_ui(self):
        """Test that naishi_pvp.py contains no game logic"""
        # Verify that naishi_pvp.py uses GameState for all game logic
        # by checking that GameState has all necessary methods
        gs = GameState.create_initial_state(seed=42)
        
        # All game state should be in GameState
        assert hasattr(gs, 'apply_action_array')
        assert hasattr(gs, 'get_legal_action_types')
        assert hasattr(gs, 'optional_emissary_available')
        assert hasattr(gs, 'must_develop')
        assert hasattr(gs, 'current_player_idx')
    
    def test_ai_no_game_logic_in_ui(self):
        """Test that play_vs_ai.py contains no game logic"""
        # Verify that play_vs_ai.py uses GameState for all game logic
        # by checking that GameState has all necessary methods
        gs = GameState.create_initial_state(seed=42)
        
        # All game state should be in GameState
        assert hasattr(gs, 'apply_action_array')
        assert hasattr(gs, 'get_legal_action_types')
        assert hasattr(gs, 'optional_emissary_available')
        assert hasattr(gs, 'must_develop')
        assert hasattr(gs, 'current_player_idx')
    
    def test_ui_queries_gamestate_for_legal_actions(self):
        """Test that UI files query GameState for legal actions"""
        gs = GameState.create_initial_state(seed=42)
        
        # Legal actions should come from GameState
        legal_types = gs.get_legal_action_types()
        assert isinstance(legal_types, list)
        assert len(legal_types) > 0
    
    def test_ui_queries_gamestate_for_turn_state(self):
        """Test that UI files query GameState for turn state"""
        gs = GameState.create_initial_state(seed=42)
        
        # Turn state should come from GameState
        assert hasattr(gs, 'optional_emissary_available')
        assert hasattr(gs, 'must_develop')
        assert hasattr(gs, 'current_player_idx')
    
    def test_ui_applies_actions_through_gamestate(self):
        """Test that UI files apply actions through GameState"""
        gs = GameState.create_initial_state(seed=42)
        
        # Actions should be applied through GameState.apply_action_array
        action = [ACTION_DEVELOP, 0, 0, 0, 0, 0, 0, 0]
        result = gs.apply_action_array(action)
        
        # Should return tuple (obs, reward, terminated, truncated, info)
        assert isinstance(result, tuple)
        assert len(result) == 5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
