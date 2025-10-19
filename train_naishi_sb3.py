# train_sb3_sparse.py
"""
Stable-Baselines3 training optimized for sparse rewards (win/loss only)
"""

import numpy as np
import gymnasium as gym
from gymnasium import spaces
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.callbacks import BaseCallback
from stable_baselines3.common.utils import obs_as_tensor
import torch

# Import the sparse reward environment
import sys
sys.path.insert(0, '.')
from train_sparse_rewards import SparseRewardEnv, masked_random_agent


class FlattenedSparseEnv(gym.Wrapper):
    """Wrapper to flatten observation space"""
    
    def __init__(self, env):
        super().__init__(env)
        
        obs_size = 0
        sample_obs = env.observation_space.sample()
        for key in sorted(sample_obs.keys()):
            obs_size += sample_obs[key].size
        
        self.observation_space = spaces.Box(
            low=0, 
            high=255,
            shape=(obs_size,),
            dtype=np.float32
        )
    
    def reset(self, **kwargs):
        obs, info = self.env.reset(**kwargs)
        return self._flatten_obs(obs), info
    
    def step(self, action):
        obs, reward, terminated, truncated, info = self.env.step(action)
        return self._flatten_obs(obs), reward, terminated, truncated, info
    
    def _flatten_obs(self, obs_dict):
        flat_obs = []
        for key in sorted(obs_dict.keys()):
            flat_obs.append(obs_dict[key].flatten())
        return np.concatenate(flat_obs).astype(np.float32)


class SparseRewardCallback(BaseCallback):
    """
    Callback optimized for tracking sparse reward training
    """
    
    def __init__(self, eval_freq=1000, verbose=1):
        super().__init__(verbose)
        self.eval_freq = eval_freq
        self.episode_rewards = []
        self.episode_lengths = []
        self.wins = 0
        self.losses = 0
        self.draws = 0
        self.best_win_rate = 0.0
        
    def _on_step(self):
        # Check if episode finished
        if self.locals.get('dones')[0]:
            info = self.locals.get('infos')[0]
            
            # Get episode reward
            if 'episode' in info:
                reward = info['episode']['r']
                length = info['episode']['l']
                
                self.episode_rewards.append(reward)
                self.episode_lengths.append(length)
                
                # Track win/loss/draw
                if reward > 0.01:
                    self.wins += 1
                elif reward < -0.01:
                    self.losses += 1
                else:
                    self.draws += 1
                
                # Print progress every 10 episodes
                if len(self.episode_rewards) % 10 == 0:
                    recent = self.episode_rewards[-10:]
                    recent_wins = sum(1 for r in recent if r > 0.01)
                    total_games = len(self.episode_rewards)
                    win_rate = self.wins / total_games
                    
                    if win_rate > self.best_win_rate:
                        self.best_win_rate = win_rate
                    
                    print(f"Episodes: {total_games:4d} | "
                          f"Win Rate: {win_rate:.1%} | "
                          f"Recent (10): {recent_wins}/10 | "
                          f"Best: {self.best_win_rate:.1%}")
        
        return True


def make_sparse_env(reward_mode='win_loss', seed=None):
    """Factory for creating sparse reward environments"""
    def _init():
        env = SparseRewardEnv(
            reward_mode=reward_mode,
            opponent_policy=masked_random_agent,
            seed=seed
        )
        env = FlattenedSparseEnv(env)
        return env
    return _init


def train_sparse_ppo(
    total_timesteps=200000,
    reward_mode='win_loss',
    save_path='naishi_sparse_model',
    learning_rate=3e-4
):
    """
    Train PPO with sparse rewards (win/loss only)
    
    Args:
        total_timesteps: How long to train (200k+ recommended for sparse rewards)
        reward_mode: 'win_loss', 'binary', 'scaled', or 'score_diff'
        save_path: Where to save the model
        learning_rate: Learning rate (3e-4 is good default)
    """
    print("="*70)
    print(f"TRAINING PPO WITH SPARSE REWARDS ({reward_mode})")
    print("="*70)
    print(f"Total timesteps: {total_timesteps:,}")
    print(f"This will take approximately {total_timesteps // 1000} games")
    print("="*70)
    print()
    
    # Create environment
    env = DummyVecEnv([make_sparse_env(reward_mode=reward_mode, seed=42)])
    
    # PPO configuration optimized for sparse rewards
    model = PPO(
        "MlpPolicy",
        env,
        verbose=0,
        learning_rate=learning_rate,
        n_steps=2048,         # More steps before update (better for sparse rewards)
        batch_size=64,
        n_epochs=10,          # More epochs per update
        gamma=0.99,           # High discount (future matters)
        gae_lambda=0.95,      # GAE helps with sparse rewards
        clip_range=0.2,
        ent_coef=0.01,        # Encourage exploration
        vf_coef=0.5,
        max_grad_norm=0.5,
        policy_kwargs=dict(
            net_arch=[dict(pi=[256, 256], vf=[256, 256])]  # Larger network
        ),
        tensorboard_log="./naishi_sparse_tensorboard/"
    )
    
    print("Model configuration:")
    print(f"  Policy: MLP with [256, 256] layers")
    print(f"  Learning rate: {learning_rate}")
    print(f"  Batch size: 64")
    print(f"  GAE Lambda: 0.95 (helps with sparse rewards)")
    print(f"  Entropy coefficient: 0.01 (encourages exploration)")
    print()
    
    # Train with callback
    callback = SparseRewardCallback()
    
    print("Training started...")
    print("-"*70)
    model.learn(
        total_timesteps=total_timesteps,
        callback=callback,
        progress_bar=True
    )
    
    print()
    print("="*70)
    print("TRAINING COMPLETE")
    print("="*70)
    print(f"Total episodes: {len(callback.episode_rewards)}")
    print(f"Final win rate: {callback.wins / len(callback.episode_rewards):.1%}")
    print(f"Best win rate: {callback.best_win_rate:.1%}")
    print(f"Average episode length: {np.mean(callback.episode_lengths):.1f}")
    print()
    
    # Save model
    model.save(save_path)
    print(f"Model saved to: {save_path}.zip")
    print()
    
    return model, callback


def evaluate_sparse_model(model_path, n_episodes=100, reward_mode='win_loss'):
    """
    Evaluate a trained sparse reward model
    """
    print(f"Loading model from {model_path}...")
    model = PPO.load(model_path)
    
    env = SparseRewardEnv(
        reward_mode=reward_mode,
        opponent_policy=masked_random_agent,
        seed=999
    )
    env = FlattenedSparseEnv(env)
    
    print(f"Evaluating over {n_episodes} episodes...")
    print("-"*70)
    
    wins = 0
    losses = 0
    draws = 0
    rewards = []
    lengths = []
    
    for episode in range(n_episodes):
        obs, info = env.reset()
        done = False
        truncated = False
        episode_reward = 0
        steps = 0
        
        while not (done or truncated) and steps < 100:
            action, _ = model.predict(obs, deterministic=True)
            obs, reward, done, truncated, info = env.step(action)
            episode_reward += reward
            steps += 1
        
        rewards.append(episode_reward)
        lengths.append(steps)
        
        if episode_reward > 0.01:
            wins += 1
        elif episode_reward < -0.01:
            losses += 1
        else:
            draws += 1
        
        if (episode + 1) % 20 == 0:
            current_wr = wins / (episode + 1)
            print(f"  {episode + 1}/{n_episodes} - Win Rate: {current_wr:.1%}")
    
    print()
    print("="*70)
    print("EVALUATION RESULTS")
    print("="*70)
    print(f"Win Rate: {wins/n_episodes:.1%}")
    print(f"Loss Rate: {losses/n_episodes:.1%}")
    print(f"Draw Rate: {draws/n_episodes:.1%}")
    print(f"Average Reward: {np.mean(rewards):.3f} ± {np.std(rewards):.3f}")
    print(f"Average Game Length: {np.mean(lengths):.1f} steps")
    print("="*70)
    print()
    
    env.close()
    return wins / n_episodes


def progressive_training(stages=3, timesteps_per_stage=50000):
    """
    Progressive training: train in stages, saving best models
    """
    print("="*70)
    print("PROGRESSIVE SPARSE REWARD TRAINING")
    print("="*70)
    print(f"Stages: {stages}")
    print(f"Timesteps per stage: {timesteps_per_stage:,}")
    print("="*70)
    print()
    
    best_model_path = None
    best_win_rate = 0.0
    
    for stage in range(stages):
        print(f"\n{'='*70}")
        print(f"STAGE {stage + 1}/{stages}")
        print(f"{'='*70}\n")
        
        save_path = f"naishi_sparse_stage{stage+1}"
        
        # Train
        model, callback = train_sparse_ppo(
            total_timesteps=timesteps_per_stage,
            reward_mode='win_loss',
            save_path=save_path,
            learning_rate=3e-4 / (stage + 1)  # Decrease LR each stage
        )
        
        # Evaluate
        win_rate = evaluate_sparse_model(save_path, n_episodes=100)
        
        if win_rate > best_win_rate:
            best_win_rate = win_rate
            best_model_path = save_path
            print(f"✓ New best model! Win rate: {win_rate:.1%}")
        
        print()
    
    print("="*70)
    print("PROGRESSIVE TRAINING COMPLETE")
    print("="*70)
    print(f"Best model: {best_model_path}")
    print(f"Best win rate: {best_win_rate:.1%}")
    print("="*70)
    
    return best_model_path


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "train":
            # Quick training
            timesteps = int(sys.argv[2]) if len(sys.argv) > 2 else 100000
            train_sparse_ppo(total_timesteps=timesteps)
        
        elif command == "train_long":
            # Long training for better results
            train_sparse_ppo(total_timesteps=500000)
        
        elif command == "evaluate":
            model_path = sys.argv[2] if len(sys.argv) > 2 else "naishi_sparse_model"
            evaluate_sparse_model(model_path, n_episodes=100)
        
        elif command == "progressive":
            # Multi-stage training
            progressive_training(stages=3, timesteps_per_stage=100000)
        
        else:
            print("Unknown command!")
            print("\nUsage:")
            print("  python train_sb3_sparse.py train [timesteps]")
            print("  python train_sb3_sparse.py train_long")
            print("  python train_sb3_sparse.py evaluate [model_path]")
            print("  python train_sb3_sparse.py progressive")
    
    else:
        # Default: short training demo
        print("SPARSE REWARD TRAINING DEMO")
        print("="*70)
        print("Training for 50,000 timesteps...")
        print("For full training, use: python train_sb3_sparse.py train 200000")
        print("="*70)
        print()
        
        model, callback = train_sparse_ppo(total_timesteps=50000)
        
        print("\nEvaluating trained model...")
        evaluate_sparse_model("naishi_sparse_model", n_episodes=50)