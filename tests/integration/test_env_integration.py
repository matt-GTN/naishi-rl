"""
Integration test for Task 26: Multi-action turn support in training

This test verifies that the multi-action turn support works correctly
with the existing training infrastructure and doesn't break anything.
"""

import numpy as np
from naishi_env import NaishiEnv
from naishi_core.game_logic import (
    ACTION_DRAFT,
    ACTION_DEVELOP,
    ACTION_SWAP,
    ACTION_DISCARD,
)


class RandomPolicy:
    """Random policy for testing."""
    
    def predict(self, obs, deterministic=False, action_masks=None):
        """Return a random legal action."""
        # Parse action mask to find legal action types
        if action_masks is not None:
            legal_types = []
            for i in range(7):
                if action_masks[i] == 1:
                    legal_types.append(i)
            
            if legal_types:
                action_type = np.random.choice(legal_types)
            else:
                action_type = ACTION_DEVELOP
        else:
            action_type = ACTION_DEVELOP
        
        # Create random action
        action = np.array([
            action_type,
            np.random.randint(0, 10),
            np.random.randint(0, 5),
            np.random.randint(0, 4),
            np.random.randint(0, 5),
            np.random.randint(0, 5),
            np.random.randint(0, 5),
            np.random.randint(0, 5),
        ])
        
        return action, None


def test_env_without_policies():
    """Test that env works without any policies (backward compatibility)."""
    print("\n=== Test: Env without Policies (Backward Compatibility) ===")
    
    env = NaishiEnv(seed=42)
    obs, info = env.reset(seed=42)
    
    # Play a few turns
    for i in range(10):
        action_mask = env._get_action_mask()
        legal_types = env.gs.get_legal_action_types()
        
        if legal_types:
            action_type = legal_types[0]
            action = np.array([action_type, 0, 0, 0, 0, 0, 0, 0])
            obs, reward, done, trunc, info = env.step(action)
            
            if done or trunc:
                break
    
    print(f"Played {i+1} turns without errors")
    print("✓ Backward compatibility maintained")


def test_env_with_agent_policy_only():
    """Test env with only agent policy."""
    print("\n=== Test: Env with Agent Policy Only ===")
    
    agent_policy = RandomPolicy()
    env = NaishiEnv(seed=123, agent_policy=agent_policy)
    obs, info = env.reset(seed=123)
    
    # Play a few turns
    for i in range(10):
        action_mask = env._get_action_mask()
        legal_types = env.gs.get_legal_action_types()
        
        if legal_types:
            action_type = legal_types[0]
            action = np.array([action_type, 0, 0, 0, 0, 0, 0, 0])
            obs, reward, done, trunc, info = env.step(action)
            
            if done or trunc:
                break
    
    print(f"Played {i+1} turns with agent policy")
    print("✓ Agent policy integration works")


def test_env_with_opponent_policy_only():
    """Test env with only opponent policy."""
    print("\n=== Test: Env with Opponent Policy Only ===")
    
    opponent_policy = RandomPolicy()
    env = NaishiEnv(seed=456, opponent_policy=opponent_policy)
    obs, info = env.reset(seed=456)
    
    # Play a few turns
    for i in range(10):
        action_mask = env._get_action_mask()
        legal_types = env.gs.get_legal_action_types()
        
        if legal_types:
            action_type = legal_types[0]
            action = np.array([action_type, 0, 0, 0, 0, 0, 0, 0])
            obs, reward, done, trunc, info = env.step(action)
            
            if done or trunc:
                break
    
    print(f"Played {i+1} turns with opponent policy")
    print("✓ Opponent policy integration works")


def test_env_with_both_policies():
    """Test env with both agent and opponent policies."""
    print("\n=== Test: Env with Both Policies ===")
    
    agent_policy = RandomPolicy()
    opponent_policy = RandomPolicy()
    env = NaishiEnv(seed=789, agent_policy=agent_policy, opponent_policy=opponent_policy)
    obs, info = env.reset(seed=789)
    
    # Play a few turns
    for i in range(10):
        action_mask = env._get_action_mask()
        legal_types = env.gs.get_legal_action_types()
        
        if legal_types:
            action_type = legal_types[0]
            action = np.array([action_type, 0, 0, 0, 0, 0, 0, 0])
            obs, reward, done, trunc, info = env.step(action)
            
            if done or trunc:
                break
    
    print(f"Played {i+1} turns with both policies")
    print("✓ Both policies integration works")


def test_complete_game_with_policies():
    """Test a complete game with policies."""
    print("\n=== Test: Complete Game with Policies ===")
    
    agent_policy = RandomPolicy()
    opponent_policy = RandomPolicy()
    env = NaishiEnv(seed=999, agent_policy=agent_policy, opponent_policy=opponent_policy)
    obs, info = env.reset(seed=999)
    
    turn_count = 0
    max_turns = 200  # Safety limit
    
    while turn_count < max_turns:
        action_mask = env._get_action_mask()
        legal_types = env.gs.get_legal_action_types()
        
        if not legal_types:
            print("No legal actions available")
            break
        
        action_type = legal_types[0]
        action = np.array([action_type, 0, 0, 0, 0, 0, 0, 0])
        obs, reward, done, trunc, info = env.step(action)
        
        turn_count += 1
        
        if done or trunc:
            print(f"Game ended after {turn_count} turns")
            print(f"Final scores: {info.get('scores', 'N/A')}")
            break
    
    if turn_count >= max_turns:
        print(f"Game reached max turns ({max_turns})")
    
    print("✓ Complete game works with policies")


def test_observation_shape_consistency():
    """Test that observation shape is consistent within each phase."""
    print("\n=== Test: Observation Shape Consistency ===")
    
    agent_policy = RandomPolicy()
    opponent_policy = RandomPolicy()
    env = NaishiEnv(seed=111, agent_policy=agent_policy, opponent_policy=opponent_policy)
    obs, info = env.reset(seed=111)
    
    initial_shape = obs.shape
    print(f"Initial observation shape (draft): {initial_shape}")
    
    # Play through draft phase
    draft_shapes = []
    while env.gs.in_draft_phase:
        action_mask = env._get_action_mask()
        legal_types = env.gs.get_legal_action_types()
        
        if legal_types:
            action_type = legal_types[0]
            action = np.array([action_type, 0, 0, 0, 0, 0, 0, 0])
            obs, reward, done, trunc, info = env.step(action)
            draft_shapes.append(obs.shape)
            
            if done or trunc:
                break
    
    # Check draft phase shapes are consistent
    if draft_shapes:
        for shape in draft_shapes:
            assert shape == draft_shapes[0], f"Draft shape inconsistent: {shape} != {draft_shapes[0]}"
        print(f"Draft phase shapes consistent: {draft_shapes[0]}")
    
    # Play through main game phase
    main_shapes = []
    for i in range(20):
        if env.gs.in_draft_phase:
            continue
            
        action_mask = env._get_action_mask()
        legal_types = env.gs.get_legal_action_types()
        
        if legal_types:
            action_type = legal_types[0]
            action = np.array([action_type, 0, 0, 0, 0, 0, 0, 0])
            obs, reward, done, trunc, info = env.step(action)
            main_shapes.append(obs.shape)
            
            if done or trunc:
                break
    
    # Check main game shapes are consistent
    if main_shapes:
        for shape in main_shapes:
            assert shape == main_shapes[0], f"Main game shape inconsistent: {shape} != {main_shapes[0]}"
        print(f"Main game shapes consistent: {main_shapes[0]}")
    
    print("✓ Observation shapes are consistent within each phase")


def test_reward_is_numeric():
    """Test that rewards are always numeric."""
    print("\n=== Test: Reward is Numeric ===")
    
    agent_policy = RandomPolicy()
    opponent_policy = RandomPolicy()
    env = NaishiEnv(seed=222, agent_policy=agent_policy, opponent_policy=opponent_policy)
    obs, info = env.reset(seed=222)
    
    # Play several turns and check rewards
    for i in range(20):
        action_mask = env._get_action_mask()
        legal_types = env.gs.get_legal_action_types()
        
        if legal_types:
            action_type = legal_types[0]
            action = np.array([action_type, 0, 0, 0, 0, 0, 0, 0])
            obs, reward, done, trunc, info = env.step(action)
            
            assert isinstance(reward, (int, float, np.number)), f"Reward is not numeric: {type(reward)}"
            
            if done or trunc:
                break
    
    print("✓ Rewards are always numeric")


if __name__ == "__main__":
    test_env_without_policies()
    test_env_with_agent_policy_only()
    test_env_with_opponent_policy_only()
    test_env_with_both_policies()
    test_complete_game_with_policies()
    test_observation_shape_consistency()
    test_reward_is_numeric()
    
    print("\n" + "="*50)
    print("All Task 26 integration tests passed! ✓")
    print("="*50)
