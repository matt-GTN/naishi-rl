#!/usr/bin/env python3
"""
Convenience script to train a Naishi RL agent.
Imports from src.training.train_main_agent
"""
import sys
from src.training.train_main_agent import train_agent

if __name__ == "__main__":
    train_agent(
        total_timesteps=1000000,  # Increased from 200k to 1M
        use_self_play=True,
        self_play_update_freq=20480,
        checkpoint_freq=50000,
        start_from_best=True
    )
