# train_naishi.py

import numpy as np
from naishi_gym_env import NaishiEnv


def random_agent(obs, env):
    """Simple random agent that takes valid actions"""
    return env.action_space.sample()


def train_with_random_opponent(episodes=1000):
    """
    Basic training loop with a random opponent.
    This is a starting point - you'll want to use proper RL algorithms later.
    """
    env = NaishiEnv(opponent_policy=random_agent, seed=42)
    
    total_rewards = []
    win_count = 0
    
    for episode in range(episodes):
        obs, info = env.reset()
        episode_reward = 0
        done = False
        truncated = False
        step_count = 0
        
        while not (done or truncated):
            # Random action for now (replace with your RL agent)
            action = env.action_space.sample()
            
            obs, reward, done, truncated, info = env.step(action)
            episode_reward += reward
            step_count += 1
            
            # Avoid infinite loops
            if step_count > 50:
                truncated = True
        
        total_rewards.append(episode_reward)
        
        # Track wins (positive reward means we won)
        if episode_reward > 0:
            win_count += 1
        
        # Print progress
        if (episode + 1) % 100 == 0:
            avg_reward = np.mean(total_rewards[-100:])
            win_rate = win_count / (episode + 1)
            print(f"Episode {episode + 1}/{episodes}")
            print(f"  Avg Reward (last 100): {avg_reward:.2f}")
            print(f"  Win Rate: {win_rate:.2%}")
            print(f"  Last Episode Steps: {step_count}")
            print()
    
    return total_rewards


def test_environment():
    """Test that the environment works correctly"""
    print("Testing Naishi Gym Environment...\n")
    
    env = NaishiEnv(seed=42)
    
    # Test reset
    obs, info = env.reset()
    print("✓ Environment reset successful")
    print(f"  Observation keys: {list(obs.keys())}")
    print(f"  Info: {info}\n")
    
    # Test rendering
    print("Initial state:")
    env.render()
    print()
    
    # Test a few random actions
    print("Testing random actions...")
    for i in range(5):
        action = env.action_space.sample()
        obs, reward, done, truncated, info = env.step(action)
        
        action_names = ['develop', 'swap', 'discard', 'recall', 'decree', 'end']
        print(f"  Step {i+1}: Action={action_names[action[0]]}, Reward={reward:.2f}, Done={done}")
        
        if done or truncated:
            print(f"  Game ended after {i+1} steps")
            break
    
    print("\n✓ Environment test completed successfully!")
    env.close()


if __name__ == "__main__":
    # First, test the environment
    test_environment()
    
    print("\n" + "="*50)
    print("Starting training with random agent...")
    print("="*50 + "\n")
    
    # Then run basic training
    rewards = train_with_random_opponent(episodes=500)
    
    print("\nTraining completed!")
    print(f"Average reward over all episodes: {np.mean(rewards):.2f}")
    print(f"Final 100 episodes average: {np.mean(rewards[-100:]):.2f}")