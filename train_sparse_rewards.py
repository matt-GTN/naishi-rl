# train_v2.py
"""
Improved training with simplified environment and better baseline
"""

import numpy as np
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv, SubprocVecEnv
from stable_baselines3.common.callbacks import BaseCallback
from stable_baselines3.common.monitor import Monitor
import torch

from naishi_gym_env import NaishiEnvV2, smart_baseline_policy, simple_masked_policy


class WinRateCallback(BaseCallback):
    """Track win rate during training"""
    
    def __init__(self, check_freq=1000, verbose=1):
        super().__init__(verbose)
        self.check_freq = check_freq
        self.wins = 0
        self.losses = 0
        self.draws = 0
        self.episodes = 0
        self.best_win_rate = 0.0
        
    def _on_step(self):
        if self.locals.get('dones')[0]:
            reward = self.locals.get('rewards')[0]
            self.episodes += 1
            
            if reward > 0.01:
                self.wins += 1
            elif reward < -0.01:
                self.losses += 1
            else:
                self.draws += 1
            
            if self.episodes % 50 == 0:
                win_rate = self.wins / self.episodes
                recent_wins = sum(1 for i in range(max(0, self.episodes-50), self.episodes)
                                if i < len(self.locals.get('infos', [])))
                
                if win_rate > self.best_win_rate:
                    self.best_win_rate = win_rate
                    if self.verbose:
                        print(f"  🏆 New best: {win_rate:.1%}")
                
                if self.verbose and self.episodes % 100 == 0:
                    print(f"Episodes: {self.episodes:4d} | "
                          f"Win: {win_rate:.1%} | "
                          f"Loss: {self.losses/self.episodes:.1%} | "
                          f"Best: {self.best_win_rate:.1%}")
        
        return True


def make_env_v2(opponent='smart', reward_mode='win_loss', seed=None):
    """Create environment with specified opponent"""
    def _init():
        opponent_policy = smart_baseline_policy if opponent == 'smart' else simple_masked_policy
        env = NaishiEnvV2(
            opponent_policy=opponent_policy,
            reward_mode=reward_mode,
            seed=seed
        )
        env = Monitor(env)
        return env
    return _init


def train_ppo_v2(
    total_timesteps=100000,
    n_envs=4,
    opponent='smart',
    save_path='naishi_v2_model'
):
    """
    Train PPO with improved environment
    
    Args:
        total_timesteps: Training duration
        n_envs: Number of parallel environments (4-8 recommended)
        opponent: 'smart' or 'simple'
        save_path: Where to save model
    """
    print("="*70)
    print("TRAINING NAISHI V2 (SIMPLIFIED)")
    print("="*70)
    print(f"Timesteps: {total_timesteps:,}")
    print(f"Parallel envs: {n_envs}")
    print(f"Opponent: {opponent}")
    print("="*70)
    print()
    
    # Create parallel environments
    if n_envs > 1:
        env = SubprocVecEnv([
            make_env_v2(opponent=opponent, seed=i) 
            for i in range(n_envs)
        ])
    else:
        env = DummyVecEnv([make_env_v2(opponent=opponent, seed=42)])
    
    # PPO with good defaults for this problem
    model = PPO(
        "MlpPolicy",
        env,
        learning_rate=3e-4,
        n_steps=512,  # Shorter rollouts since action space is simpler
        batch_size=128,
        n_epochs=4,
        gamma=0.99,
        gae_lambda=0.95,
        clip_range=0.2,
        ent_coef=0.01,  # Exploration
        vf_coef=0.5,
        max_grad_norm=0.5,
        policy_kwargs=dict(
            net_arch=[dict(pi=[128, 128], vf=[128, 128])],
            activation_fn=torch.nn.Tanh
        ),
        verbose=0,
        tensorboard_log=f"./naishi_v2_tensorboard/"
    )
    
    print("Model configuration:")
    print("  Observation space: Flat 30-dim vector")
    print("  Action space: Discrete(5) - choose deck")
    print("  Network: [128, 128] with Tanh activation")
    print()
    
    callback = WinRateCallback()
    
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
    print(f"Episodes: {callback.episodes}")
    print(f"Final Win Rate: {callback.wins/callback.episodes:.1%}")
    print(f"Best Win Rate: {callback.best_win_rate:.1%}")
    print()
    
    model.save(save_path)
    print(f"Model saved to: {save_path}.zip")
    
    return model, callback


def evaluate_v2(model_path, n_episodes=100, opponent='smart'):
    """Evaluate trained model"""
    print(f"Loading model: {model_path}")
    model = PPO.load(model_path)
    
    env = NaishiEnvV2(
        opponent_policy=smart_baseline_policy if opponent == 'smart' else simple_masked_policy,
        reward_mode='win_loss',
        seed=999
    )
    
    print(f"Evaluating over {n_episodes} episodes...")
    print("-"*70)
    
    wins = 0
    losses = 0
    draws = 0
    scores_diff = []
    
    for episode in range(n_episodes):
        obs, info = env.reset()
        done = False
        episode_reward = 0
        
        while not done:
            action, _ = model.predict(obs, deterministic=True)
            obs, reward, done, truncated, info = env.step(action)
            episode_reward += reward
            done = done or truncated
        
        if episode_reward > 0.01:
            wins += 1
        elif episode_reward < -0.01:
            losses += 1
        else:
            draws += 1
        
        scores_diff.append(episode_reward)
        
        if (episode + 1) % 20 == 0:
            print(f"  {episode+1}/{n_episodes} - WR: {wins/(episode+1):.1%}")
    
    print()
    print("="*70)
    print("EVALUATION RESULTS")
    print("="*70)
    print(f"Opponent: {opponent} baseline")
    print(f"Win Rate: {wins/n_episodes:.1%}")
    print(f"Loss Rate: {losses/n_episodes:.1%}")
    print(f"Draw Rate: {draws/n_episodes:.1%}")
    print(f"Avg Reward: {np.mean(scores_diff):.3f}")
    print("="*70)
    
    return wins / n_episodes


def compare_to_baseline(n_games=100):
    """
    Compare random vs smart baseline vs trained model
    """
    print("="*70)
    print("BASELINE COMPARISON")
    print("="*70)
    print()
    
    results = {}
    
    # 1. Random vs Random
    print("1. Random vs Random (baseline)")
    env = NaishiEnvV2(opponent_policy=simple_masked_policy, seed=42)
    wins = 0
    for _ in range(n_games):
        obs, _ = env.reset()
        done = False
        while not done:
            action = simple_masked_policy(obs, env)
            obs, reward, done, truncated, _ = env.step(action)
            done = done or truncated
        if reward > 0:
            wins += 1
    results['random_vs_random'] = wins / n_games
    print(f"   Win Rate: {results['random_vs_random']:.1%}\n")
    
    # 2. Smart vs Random
    print("2. Smart Baseline vs Random")
    env = NaishiEnvV2(opponent_policy=simple_masked_policy, seed=42)
    wins = 0
    for _ in range(n_games):
        obs, _ = env.reset()
        done = False
        while not done:
            action = smart_baseline_policy(obs, env)
            obs, reward, done, truncated, _ = env.step(action)
            done = done or truncated
        if reward > 0:
            wins += 1
    results['smart_vs_random'] = wins / n_games
    print(f"   Win Rate: {results['smart_vs_random']:.1%}\n")
    
    # 3. Smart vs Smart
    print("3. Smart Baseline vs Smart Baseline")
    env = NaishiEnvV2(opponent_policy=smart_baseline_policy, seed=42)
    wins = 0
    for _ in range(n_games):
        obs, _ = env.reset()
        done = False
        while not done:
            action = smart_baseline_policy(obs, env)
            obs, reward, done, truncated, _ = env.step(action)
            done = done or truncated
        if reward > 0:
            wins += 1
    results['smart_vs_smart'] = wins / n_games
    print(f"   Win Rate: {results['smart_vs_smart']:.1%}\n")
    
    print("="*70)
    print("Target for RL agent: >60% vs smart baseline")
    print("="*70)
    
    return results


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "baseline":
            compare_to_baseline(n_games=200)
        
        elif command == "train":
            timesteps = int(sys.argv[2]) if len(sys.argv) > 2 else 100000
            opponent = sys.argv[3] if len(sys.argv) > 3 else 'smart'
            train_ppo_v2(
                total_timesteps=timesteps,
                n_envs=4,
                opponent=opponent
            )
        
        elif command == "evaluate":
            model_path = sys.argv[2] if len(sys.argv) > 2 else "naishi_v2_model"
            opponent = sys.argv[3] if len(sys.argv) > 3 else 'smart'
            evaluate_v2(model_path, n_episodes=200, opponent=opponent)
        
        else:
            print("Unknown command!")
            print("\nUsage:")
            print("  python train_v2.py baseline")
            print("  python train_v2.py train [timesteps] [smart|simple]")
            print("  python train_v2.py evaluate [model_path] [smart|simple]")
    
    else:
        # Default: show baseline then train
        print("Step 1: Testing baselines...")
        compare_to_baseline(n_games=100)
        
        print("\n\nStep 2: Training agent...")
        model, callback = train_ppo_v2(
            total_timesteps=100000,
            n_envs=4,
            opponent='smart'
        )
        
        print("\n\nStep 3: Evaluating...")
        evaluate_v2("naishi_v2_model", n_episodes=100, opponent='smart')