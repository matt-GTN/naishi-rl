# naishi_callbacks.py (Corrected Version)
"""
Custom Stable-Baselines3 callbacks for monitoring and visualizing Naishi agent training.
"""

import os
import matplotlib.pyplot as plt
import numpy as np
from stable_baselines3.common.callbacks import BaseCallback

class ObservabilityCallback(BaseCallback):
    def __init__(self, check_freq: int, log_dir: str = "training_logs/", verbose=1):
        super(ObservabilityCallback, self).__init__(verbose)
        self.check_freq = check_freq
        self.log_dir = log_dir
        
        os.makedirs(log_dir, exist_ok=True)

        self.win_rates = []
        self.timesteps_history = []
        self.wins = 0
        self.losses = 0
        self.draws = 0
        
        # Action distribution tracker (for 7 primary actions)
        self.action_counts = np.zeros(7, dtype=np.int32)
        self.action_names = ["Draft", "Develop", "Swap", "Discard", "Recall", "Decree", "End Game"]
        
        # Track draft actions separately (not included in distribution %)
        self.draft_count = 0 


    def _on_step(self) -> bool:
        """
        Called after each step in the environment.
        """
        action_type = self.locals['actions'][0][0]
        
        # Track draft actions separately (action 0)
        if action_type == 0:
            self.draft_count += 1
        else:
            self.action_counts[action_type] += 1
        
        for i, done in enumerate(self.locals['dones']):
            if done:
                info = self.locals['infos'][i]
                reward = info.get('episode', {}).get('r', 0)

                if reward > 0.5: self.wins += 1
                elif reward < -0.5: self.losses += 1
                else: self.draws += 1
        
        return True

    def _on_rollout_end(self) -> bool:
        """
        Called at the end of each rollout to log and plot metrics.
        """
        total_games = self.wins + self.losses + self.draws
        # FIX: Access n_steps via `self.model.n_steps` instead of `self.n_steps`
        if total_games > 0 and self.num_timesteps % self.check_freq < self.model.n_steps:
            
            win_rate = self.wins / total_games
            loss_rate = self.losses / total_games
            draw_rate = self.draws / total_games
            
            self.win_rates.append(win_rate)
            self.timesteps_history.append(self.num_timesteps)

            if self.verbose > 0:
                print(f"\n--- Timestep {self.num_timesteps} ---")
                print(f"Games: {total_games} | Win Rate: {win_rate:.1%} | Loss Rate: {loss_rate:.1%} | Draw Rate: {draw_rate:.1%}")
                print(f"Draft actions: {self.draft_count} (1 per game)")
                
                # Calculate action distribution excluding draft (action 0)
                main_game_actions = self.action_counts[1:].sum()
                if main_game_actions > 0:
                    action_dist = self.action_counts[1:] / main_game_actions
                    dist_str = " | ".join([f"{name}: {dist:.1%}" for name, dist in zip(self.action_names[1:], action_dist)])
                    print(f"Main Game Action Dist: {dist_str}")
                print("--------------------------------\n")

            self._plot_stats()
            self.wins = self.losses = self.draws = 0
            self.action_counts.fill(0)
            self.draft_count = 0

        return True

    def _plot_stats(self):
        """Generates and saves a plot of the training progress."""
        fig, ax1 = plt.subplots(figsize=(12, 5))

        ax1.set_xlabel('Timesteps')
        ax1.set_ylabel('Win Rate', color='tab:blue')
        ax1.plot(self.timesteps_history, self.win_rates, color='tab:blue', marker='o', label='Win Rate')
        ax1.tick_params(axis='y', labelcolor='tab:blue')
        ax1.grid(True)
        ax1.yaxis.set_major_formatter(plt.FuncFormatter('{:.0%}'.format))
        fig.tight_layout()
        plt.title('Training Progress')
        
        save_path = os.path.join(self.log_dir, 'training_progress.png')
        plt.savefig(save_path)
        plt.close()