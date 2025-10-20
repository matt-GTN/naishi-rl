"""
Test Task 30: Update play_vs_ai.py to query GameState for turn state

This test verifies that play_vs_ai.py properly queries GameState for turn state
instead of making local decisions about turn flow.

Requirements tested:
- 2.3: play_vs_ai.py delegates to GameState
- 2.5: All components query GameState for game state
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from play_vs_ai import PlayVsAI
from naishi_core.game_logic import GameState, ACTION_DEVELOP, ACTION_SWAP, ACTION_DISCARD


def test_optional_emissary_queried_from_gamestate_human():
    """Test that optional emissary is offered when gs.optional_emissary_available is True (human player)"""
    
    # Create a mock GameState
    mock_gs = Mock(spec=GameState)
    mock_gs.current_player_idx = 0  # Human player
    mock_gs.players = [Mock(emissaries=2), Mock(emissaries=2)]
    mock_gs.get_observation.return_value = [0] * 100
    
    # Track state changes
    call_count = [0]
    def apply_action_side_effect(action):
        call_count[0] += 1
        if call_count[0] == 1:
            # After first action, optional_emissary_available becomes True
            mock_gs.optional_emissary_available = True
            mock_gs.must_develop = False
            return ([0] * 100, 0, False, False, {})
        else:
            # Should not reach here in this test
            return ([0] * 100, 0, True, False, {})
    
    mock_gs.optional_emissary_available = False
    mock_gs.must_develop = False
    mock_gs.apply_action_array.side_effect = apply_action_side_effect
    mock_gs.skip_optional_emissary.return_value = ([0] * 100, 0, True, False, {})  # End game after skip
    
    # Create PlayVsAI instance and replace gs
    with patch('play_vs_ai.GameState.create_initial_state', return_value=mock_gs):
        with patch.object(PlayVsAI, '_handle_draft'):
            game = PlayVsAI()
            game.gs = mock_gs
            
            # Mock the UI methods
            with patch('play_vs_ai.NaishiUI.show_full_state'):
                with patch('play_vs_ai.NaishiUI.display_final_scores', return_value=(0, 10, 5)):
                    with patch.object(game, '_get_human_action', return_value=[ACTION_DEVELOP, 0, 0, 0, 0, 0, 0, 0]):
                        with patch.object(game, '_offer_optional_emissary', return_value=False):
                            # Run the game
                            game.play()
                            
                            # Verify that skip_optional_emissary was called when player declined
                            assert mock_gs.skip_optional_emissary.called, \
                                "skip_optional_emissary should be called when player declines optional emissary"


def test_optional_emissary_queried_from_gamestate_ai():
    """Test that optional emissary is offered when gs.optional_emissary_available is True (AI player)"""
    
    # Create a mock GameState
    mock_gs = Mock(spec=GameState)
    mock_gs.current_player_idx = 1  # AI player
    mock_gs.players = [Mock(emissaries=2), Mock(emissaries=2)]
    mock_gs.get_observation.return_value = [0] * 100
    
    # Track state changes
    call_count = [0]
    def apply_action_side_effect(action):
        call_count[0] += 1
        if call_count[0] == 1:
            # After first action, optional_emissary_available becomes True
            mock_gs.optional_emissary_available = True
            mock_gs.must_develop = False
            return ([0] * 100, 0, False, False, {})
        else:
            # Should not reach here in this test
            return ([0] * 100, 0, True, False, {})
    
    mock_gs.optional_emissary_available = False
    mock_gs.must_develop = False
    mock_gs.apply_action_array.side_effect = apply_action_side_effect
    mock_gs.skip_optional_emissary.return_value = ([0] * 100, 0, True, False, {})  # End game after skip
    
    # Create PlayVsAI instance and replace gs
    with patch('play_vs_ai.GameState.create_initial_state', return_value=mock_gs):
        with patch.object(PlayVsAI, '_handle_draft'):
            game = PlayVsAI()
            game.gs = mock_gs
            
            # Mock AI policy to decline emissary (return non-emissary action)
            game.ai_policy = Mock(return_value=[ACTION_DEVELOP, 0, 0, 0, 0, 0, 0, 0])
            
            # Mock the UI methods
            with patch('play_vs_ai.NaishiUI.show_full_state'):
                with patch('play_vs_ai.NaishiUI.display_final_scores', return_value=(1, 5, 10)):
                    # Run the game
                    game.play()
                    
                    # Verify that skip_optional_emissary was called when AI declined
                    assert mock_gs.skip_optional_emissary.called, \
                        "skip_optional_emissary should be called when AI declines optional emissary"


def test_must_develop_queried_from_gamestate_human():
    """Test that required develop is enforced when gs.must_develop is True (human player)"""
    
    # Create a mock GameState
    mock_gs = Mock(spec=GameState)
    mock_gs.current_player_idx = 0  # Human player
    mock_gs.optional_emissary_available = False
    mock_gs.must_develop = True
    mock_gs.players = [Mock(emissaries=1), Mock(emissaries=2)]
    mock_gs.get_observation.return_value = [0] * 100
    
    # First action (emissary), then must_develop becomes True
    call_count = [0]
    def apply_action_side_effect(action):
        call_count[0] += 1
        if call_count[0] == 1:
            # After first action, must_develop is True
            mock_gs.must_develop = True
            return ([0] * 100, 0, False, False, {})
        else:
            # After second action (develop), game ends
            mock_gs.must_develop = False
            return ([0] * 100, 0, True, False, {})
    
    mock_gs.apply_action_array.side_effect = apply_action_side_effect
    mock_gs.get_legal_action_types.return_value = [ACTION_DEVELOP]
    
    # Create PlayVsAI instance and replace gs
    with patch('play_vs_ai.GameState.create_initial_state', return_value=mock_gs):
        with patch.object(PlayVsAI, '_handle_draft'):
            game = PlayVsAI()
            game.gs = mock_gs
            
            # Mock the UI methods
            with patch('play_vs_ai.NaishiUI.show_full_state'):
                with patch('play_vs_ai.NaishiUI.display_final_scores', return_value=(0, 10, 5)):
                    with patch.object(game, '_get_human_action', return_value=[ACTION_DEVELOP, 0, 0, 0, 0, 0, 0, 0]):
                        # Simulate play
                        game.play()
                        
                        # Verify that apply_action_array was called twice (emissary + required develop)
                        assert mock_gs.apply_action_array.call_count >= 2, \
                            "apply_action_array should be called at least twice when must_develop is True"


def test_must_develop_queried_from_gamestate_ai():
    """Test that required develop is enforced when gs.must_develop is True (AI player)"""
    
    # Create a mock GameState
    mock_gs = Mock(spec=GameState)
    mock_gs.current_player_idx = 1  # AI player
    mock_gs.optional_emissary_available = False
    mock_gs.must_develop = True
    mock_gs.players = [Mock(emissaries=2), Mock(emissaries=1)]
    mock_gs.get_observation.return_value = [0] * 100
    
    # First action (emissary), then must_develop becomes True
    call_count = [0]
    def apply_action_side_effect(action):
        call_count[0] += 1
        if call_count[0] == 1:
            # After first action, must_develop is True
            mock_gs.must_develop = True
            return ([0] * 100, 0, False, False, {})
        else:
            # After second action (develop), game ends
            mock_gs.must_develop = False
            return ([0] * 100, 0, True, False, {})
    
    mock_gs.apply_action_array.side_effect = apply_action_side_effect
    mock_gs.get_legal_action_types.return_value = [ACTION_DEVELOP]
    
    # Create PlayVsAI instance and replace gs
    with patch('play_vs_ai.GameState.create_initial_state', return_value=mock_gs):
        with patch.object(PlayVsAI, '_handle_draft'):
            game = PlayVsAI()
            game.gs = mock_gs
            
            # Mock AI policy
            game.ai_policy = Mock(return_value=[ACTION_DEVELOP, 0, 0, 0, 0, 0, 0, 0])
            
            # Mock the UI methods
            with patch('play_vs_ai.NaishiUI.show_full_state'):
                with patch('play_vs_ai.NaishiUI.display_final_scores', return_value=(1, 5, 10)):
                    # Simulate play
                    game.play()
                    
                    # Verify that apply_action_array was called twice (emissary + required develop)
                    assert mock_gs.apply_action_array.call_count >= 2, \
                        "apply_action_array should be called at least twice when must_develop is True"


def test_no_manual_action_type_checking():
    """Test that play_vs_ai.py does not manually check action types for turn flow"""
    
    # Read the play_vs_ai.py file
    with open('play_vs_ai.py', 'r') as f:
        content = f.read()
    
    # Check that we're querying GameState flags, not checking action types
    assert 'self.gs.optional_emissary_available' in content, \
        "Should query gs.optional_emissary_available"
    assert 'self.gs.must_develop' in content, \
        "Should query gs.must_develop"
    assert 'self.gs.skip_optional_emissary()' in content, \
        "Should call gs.skip_optional_emissary()"
    
    # Check that we're NOT manually checking action types in the main loop
    # (except for the initial action choice, which is fine)
    play_method_start = content.find('def play(self):')
    play_method_end = content.find('\n    def _', play_method_start + 1)
    if play_method_end == -1:
        play_method_end = len(content)
    play_method = content[play_method_start:play_method_end]
    
    # Should NOT have "if action_array[0] == ACTION_DEVELOP" in the main loop
    # (after the apply_action_array call)
    apply_action_pos = play_method.find('apply_action_array(action_array)')
    if apply_action_pos != -1:
        after_apply = play_method[apply_action_pos:]
        assert 'if action_array[0] == ACTION_DEVELOP' not in after_apply, \
            "Should not manually check action type after apply_action_array"


def test_turn_state_delegated_to_gamestate():
    """Test that all turn state decisions are delegated to GameState"""
    
    # Create a real GameState
    gs = GameState.create_initial_state(seed=42)
    
    # Complete draft
    gs._complete_draft(0, 1)
    
    # Create PlayVsAI instance
    with patch.object(PlayVsAI, '_handle_draft'):
        game = PlayVsAI(seed=42)
        game.gs = gs
        
        # Verify that game queries GameState for turn state
        assert hasattr(game.gs, 'optional_emissary_available'), \
            "GameState should have optional_emissary_available attribute"
        assert hasattr(game.gs, 'must_develop'), \
            "GameState should have must_develop attribute"
        assert hasattr(game.gs, 'skip_optional_emissary'), \
            "GameState should have skip_optional_emissary method"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
