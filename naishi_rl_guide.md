# Complete Guide: Reinforcement Learning for Naishi Card Game

## Table of Contents
1. [Introduction to RL Concepts](#1-introduction-to-rl-concepts)
2. [Installation](#2-installation)
3. [Understanding the Gym Environment](#3-understanding-the-gym-environment)
4. [Running Your First Training](#4-running-your-first-training)
5. [Using Stable-Baselines3](#5-using-stable-baselines3)
6. [Improving Your Agent](#6-improving-your-agent)
7. [Next Steps](#7-next-steps)

---

## 1. Introduction to RL Concepts

### What is Reinforcement Learning?
Reinforcement Learning (RL) is a type of machine learning where an **agent** learns to make decisions by interacting with an **environment**. The agent:
- Observes the current **state** (what's happening)
- Takes an **action** (makes a move)
- Receives a **reward** (feedback on how good the action was)
- Learns to maximize total reward over time

### Key Components for Naishi

**Agent**: Your AI player learning to play Naishi

**Environment**: The Naishi game (board, cards, rules)

**State/Observation**: What the agent can see:
- Your cards (line + hand)
- Opponent's line (their hand is hidden)
- River cards
- Emissaries, decree status, etc.

**Actions**: What the agent can do:
- Develop territory (draw from river)
- Send emissary (swap/discard)
- Recall emissaries
- Impose decree
- End game

**Reward**: How we tell the agent if it's winning:
- Positive reward for winning
- Negative reward for losing
- Small penalties for invalid moves

---

## 2. Installation

### Step 1: Install Required Packages

```bash
# Basic setup (for simple training)
pip install gymnasium numpy termcolor

# Advanced setup (for Stable-Baselines3)
pip install stable-baselines3[extra]

# For visualization
pip install tensorboard matplotlib
```

### Step 2: Organize Your Files

Your project structure should look like:
```
naishi_rl_project/
├── naishi_core/          # Your existing game code
│   ├── __init__.py
│   ├── constants.py
│   ├── player.py
│   ├── river.py
│   ├── scorer.py
│   └── utils.py
├── naishi_gym_env.py     # New: Gym environment
├── train_naishi.py       # New: Basic training script
├── train_naishi_sb3.py   # New: Advanced training with SB3
└── banner.py             # Your existing banner
```

---

## 3. Understanding the Gym Environment

### What is a Gym Environment?

Gymnasium (formerly OpenAI Gym) is a standard interface for RL environments. It defines:
- How to reset the game
- How to take actions
- What observations look like
- What rewards are given

### The NaishiEnv Class

```python
from naishi_gym_env import NaishiEnv

# Create environment
env = NaishiEnv(seed=42)

# Reset to start new game
observation, info = env.reset()

# Take an action
action = env.action_space.sample()  # Random action
observation, reward, done, truncated, info = env.step(action)

# Render the game state
env.render()
```

### Understanding Observations

The observation is a dictionary containing:
- `player_line`: Your 5 line cards (encoded as integers)
- `player_hand`: Your 5 hand cards
- `opponent_line`: Opponent's visible line
- `river_top`: Top card of each river deck
- `river_count`: Cards remaining in each deck
- `player_emissaries`: How many emissaries you have
- And more...

### Understanding Actions

Actions are encoded as a 4-element array:
```python
action = [action_type, param1, param2, param3]

# Examples:
[0, 2, 0, 0]  # Develop territory from deck 2
[1, 0, 3, 3]  # Swap cards in river (decks 0 and 3)
[3, 0, 0, 0]  # Recall emissaries
[5, 0, 0, 0]  # End game
```

---

## 4. Running Your First Training

### Test the Environment

First, make sure everything works:

```bash
python train_naishi.py
```

This will:
1. Test the environment setup
2. Run 500 episodes with random agents
3. Show win rate and average rewards

Expected output:
```
Testing Naishi Gym Environment...
✓ Environment reset successful
...
Episode 100/500
  Avg Reward (last 100): -2.45
  Win Rate: 48.00%
  Last Episode Steps: 12
```

### Understanding the Results

- **Avg Reward**: Should be around 0 for random vs random
- **Win Rate**: Should be around 50% for evenly matched random agents
- **Steps**: How many actions per game (typically 10-30)

---

## 5. Using Stable-Baselines3

Stable-Baselines3 (SB3) provides professional-grade RL algorithms.

### Quick Start

```bash
# Train a PPO agent (recommended for beginners)
python train_naishi_sb3.py train_ppo

# This will train for 100,000 timesteps (~30-60 minutes)
# Model saved to: naishi_ppo_model.zip
```

### Evaluate Your Agent

```bash
# Test how well the agent learned
python train_naishi_sb3.py evaluate naishi_ppo_model
```

Expected results after 100k timesteps:
- Win rate vs random: 60-75%
- Average reward: +5 to +15

### Watch Your Agent Play

```bash
# See the agent in action
python train_naishi_sb3.py play naishi_ppo_model
```

### Compare Algorithms

```bash
# Train and compare PPO, A2C, and DQN
python train_naishi_sb3.py compare
```

**Algorithm Guide**:
- **PPO** (Proximal Policy Optimization): Best all-around, stable, good for beginners
- **A2C** (Advantage Actor-Critic): Faster but less stable
- **DQN** (Deep Q-Network): Good for discrete actions, learns optimal play

---

## 6. Improving Your Agent

### Hyperparameter Tuning

Edit `train_naishi_sb3.py` to adjust:

```python
model = PPO(
    "MlpPolicy",
    env,
    learning_rate=3e-4,      # Try: 1e-4 to 1e-3
    n_steps=2048,            # Try: 1024 to 4096
    batch_size=64,           # Try: 32 to 256
    gamma=0.99,              # Discount factor (0.95-0.99)
    # ...
)
```

**Tips**:
- Lower `learning_rate` = slower but more stable
- Higher `n_steps` = more exploration
- Larger `batch_size` = more stable updates (needs more memory)

### Reward Shaping

Current reward is just final score difference. You can add intermediate rewards:

```python
def _calculate_intermediate_reward(self):
    """Add small rewards during game"""
    reward = 0
    
    # Reward for good card placement
    # Reward for using emissaries effectively
    # Penalty for invalid actions
    
    return reward
```

### Curriculum Learning

Train in stages:

1. **Stage 1**: Random opponent (easy)
2. **Stage 2**: Trained agent as opponent (medium)
3. **Stage 3**: Self-play (hard)

```python
# Load previous model as opponent
old_model = PPO.load("naishi_ppo_model_v1")

def trained_opponent(obs, env):
    action, _ = old_model.predict(obs)
    return action

env = NaishiEnv(opponent_policy=trained_opponent)
```

### Feature Engineering

Improve the observation space:

```python
# Add derived features
def _get_enhanced_obs(self):
    obs = self._get_obs()
    
    # Add: card counts, adjacency info, potential scores
    obs['card_counts'] = self._count_card_types()
    obs['line_score_estimate'] = self._estimate_score()
    
    return obs
```

---

## 7. Next Steps

### Beginner Tasks
1. ✅ Run basic training (train_naishi.py)
2. ✅ Train your first PPO agent
3. ✅ Evaluate and watch it play
4. 🎯 Tune hyperparameters to improve win rate to 70%+

### Intermediate Tasks
1. 🎯 Implement reward shaping
2. 🎯 Add intermediate rewards for good play
3. 🎯 Train agents with self-play
4. 🎯 Compare multiple algorithms

### Advanced Tasks
1. 🎯 Implement Monte Carlo Tree Search (MCTS)
2. 🎯 Use recurrent policies (LSTM) to handle hidden information
3. 🎯 Multi-agent training with diverse opponents
4. 🎯 Implement AlphaZero-style training

### Resources

**Learn RL Basics**:
- [Spinning Up in Deep RL](https://spinningup.openai.com/) - OpenAI's RL tutorial
- [Hugging Face Deep RL Course](https://huggingface.co/learn/deep-rl-course/) - Hands-on course

**Stable-Baselines3 Docs**:
- [SB3 Documentation](https://stable-baselines3.readthedocs.io/)
- [SB3 RL Zoo](https://github.com/DLR-RM/rl-baselines3-zoo) - Trained agents & hyperparameters

**Advanced Topics**:
- AlphaGo/AlphaZero papers for self-play
- Multi-agent RL for competitive games
- Imperfect information game theory

---

## Common Issues & Solutions

### Issue: "Module not found"
```bash
# Make sure you're in the right directory
cd naishi_rl_project

# Install dependencies
pip install -r requirements.txt
```

### Issue: Training is very slow
- Reduce `total_timesteps` for testing
- Use vectorized environments (multiple parallel games)
- Consider using GPU (install `stable-baselines3[extra]`)

### Issue: Agent learns very slowly
- Check reward signal (should see positive/negative rewards)
- Increase training time (100k → 1M timesteps)
- Tune learning rate and batch size
- Add reward shaping

### Issue: Agent always loses
- Verify environment is correct (test with random agents)
- Check that rewards are balanced (not always negative)
- Try different algorithms (PPO, A2C, DQN)
- Increase network size or training time

---

## Quick Reference

### Training Commands
```bash
# Basic training
python train_naishi.py

# Train PPO agent
python train_naishi_sb3.py train_ppo

# Train DQN agent  
python train_naishi_sb3.py train_dqn

# Evaluate model
python train_naishi_sb3.py evaluate naishi_ppo_model

# Watch agent play
python train_naishi_sb3.py play naishi_ppo_model

# Compare algorithms
python train_naishi_sb3.py compare
```

### Environment API
```python
# Create environment
env = NaishiEnv(seed=42)

# Reset game
obs, info = env.reset()

# Take action
obs, reward, done, truncated, info = env.step(action)

# Render
env.render()

# Clean up
env.close()
```

---

## Success Metrics

Track these to monitor progress:

1. **Win Rate vs Random**: 70%+ is good, 80%+ is excellent
2. **Average Episode Reward**: Should increase over time
3. **Episode Length**: Efficient play = shorter games
4. **Invalid Action Rate**: Should decrease to near 0%
5. **Final Score**: Agent should consistently score 40-60 points

Good luck training your Naishi agent! 🎮🤖
