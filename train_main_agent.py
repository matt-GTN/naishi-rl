# train_main_agent.py
"""
Main training script for the Naishi RL agent using Stable-Baselines3.
Now includes self-play training where the agent trains against itself.
"""
import numpy as np
import os
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.callbacks import BaseCallback

# Local imports
from naishi_env import NaishiEnv
from naishi_callbacks import ObservabilityCallback
from policies import SelfPlayPolicy

class SelfPlayCallback(BaseCallback):
    """
    Callback that periodically updates the opponent model for self-play
    and saves versioned checkpoints.
    """
    def __init__(self, opponent_policy, update_freq=20480, save_freq=50000, 
                 checkpoint_dir="models/checkpoints", verbose=0):
        super().__init__(verbose)
        self.opponent_policy = opponent_policy
        self.update_freq = update_freq
        self.save_freq = save_freq
        self.checkpoint_dir = checkpoint_dir
        self.last_update = 0
        self.last_save = 0
        
        # Create checkpoint directory
        os.makedirs(checkpoint_dir, exist_ok=True)
        
    def _on_step(self):
        # Update opponent model
        if self.num_timesteps - self.last_update >= self.update_freq:
            self.opponent_policy.update_model(self.model)
            self.last_update = self.num_timesteps
            if self.verbose > 0:
                print(f"\n[Self-Play] Updated opponent model at timestep {self.num_timesteps}")
        
        # Save checkpoint
        if self.num_timesteps - self.last_save >= self.save_freq:
            checkpoint_path = os.path.join(
                self.checkpoint_dir, 
                f"naishi_model_{self.num_timesteps}"
            )
            self.model.save(checkpoint_path)
            self.last_save = self.num_timesteps
            if self.verbose > 0:
                print(f"[Checkpoint] Saved model to {checkpoint_path}.zip")
        
        return True

def find_latest_model():
    """
    Find the most recent timestamped model in the models directory.
    Returns the path to the model (without .zip extension) or None if no model exists.
    """
    import glob
    
    if not os.path.exists("models"):
        return None
    
    # Look for timestamped model files only (exclude naishi_model.zip)
    model_files = glob.glob("models/naishi_model_*.zip")
    
    if not model_files:
        return None
    
    # Sort by modification time (most recent first)
    model_files.sort(key=os.path.getmtime, reverse=True)
    
    # Return path without .zip extension
    latest = model_files[0][:-4]  # Remove .zip
    return latest

def train_agent(total_timesteps=200000, use_self_play=True, self_play_update_freq=20480,
                checkpoint_freq=50000, resume_from=None, start_from_best=True):
    """
    Train the Naishi agent with optional self-play and automatic checkpointing.
    
    Args:
        total_timesteps: Total training timesteps
        use_self_play: If True, train against itself; if False, train against random
        self_play_update_freq: How often to update the opponent model (in timesteps)
        checkpoint_freq: How often to save checkpoints (in timesteps)
        resume_from: Path to a checkpoint to resume training from (e.g., "models/checkpoints/naishi_model_100000")
        start_from_best: If True, initialize opponent with the best existing model
    """
    from datetime import datetime
    
    # Generate unique timestamp for this training run
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    print("--- Starting Naishi Agent Training ---")
    print(f"Training ID: {timestamp}")
    
    if use_self_play:
        print("Mode: Self-Play (agent trains against itself)")
        opponent = SelfPlayPolicy(model=None)
    else:
        print("Mode: Random Opponent")
        from policies import MaskedRandomPolicy
        opponent = MaskedRandomPolicy(NaishiEnv(opponent_policy=None).action_space)

    # Factory function to create the environment
    def make_env():
        env = NaishiEnv(opponent_policy=opponent, seed=np.random.randint(0, 10000))
        return Monitor(env)

    env = DummyVecEnv([make_env])

    # Setup callbacks
    callbacks = [
        ObservabilityCallback(check_freq=2048 * 10, log_dir="./training_logs/")
    ]
    
    if use_self_play:
        callbacks.append(
            SelfPlayCallback(
                opponent_policy=opponent,
                update_freq=self_play_update_freq,
                save_freq=checkpoint_freq,
                checkpoint_dir=f"models/checkpoints/{timestamp}",
                verbose=1
            )
        )

    # Load existing model or create new one
    if resume_from:
        print(f"Resuming training from: {resume_from}")
        model = PPO.load(resume_from, env=env, tensorboard_log="./tensorboard_logs/")
        print(f"Model loaded successfully")
    else:
        # Check if we should start from the best existing model
        latest_model = find_latest_model() if start_from_best else None
        
        if latest_model:
            print(f"Found existing model: {latest_model}.zip")
            print("Loading as starting point for new training run...")
            try:
                model = PPO.load(latest_model, env=env, tensorboard_log="./tensorboard_logs/")
                print("✓ Loaded successfully - training will continue from this model")
            except Exception as e:
                print(f"✗ Failed to load model: {e}")
                print("Starting with fresh model instead")
                model = PPO(
                    "MlpPolicy",
                    env,
                    verbose=0,
                    n_steps=2048,
                    batch_size=64,
                    n_epochs=10,
                    gamma=0.99,
                    gae_lambda=0.95,
                    tensorboard_log="./tensorboard_logs/"
                )
        else:
            print("No existing model found - starting fresh")
            model = PPO(
                "MlpPolicy",
                env,
                verbose=0,
                n_steps=2048,
                batch_size=64,
                n_epochs=10,
                gamma=0.99,
                gae_lambda=0.95,
                tensorboard_log="./tensorboard_logs/"
            )
    
    # Initialize self-play opponent with the starting model
    if use_self_play:
        opponent.update_model(model)
        print(f"Self-play opponent initialized with current model")
        print(f"Opponent will update every {self_play_update_freq} timesteps")
        print(f"Checkpoints will be saved every {checkpoint_freq} timesteps to models/checkpoints/{timestamp}/")

    print("Training started... Logs and charts will be saved in './training_logs/'")
    
    model.learn(
        total_timesteps=total_timesteps,
        callback=callbacks,
        progress_bar=True,
        reset_num_timesteps=False if resume_from else True
    )

    # Create models directory if it doesn't exist
    os.makedirs("models", exist_ok=True)
    
    # Save final model with unique timestamp
    final_path = f"models/naishi_model_{timestamp}"
    model.save(final_path)
    
    # Also save as the default model (overwrites previous default)
    model.save("models/naishi_model")
    
    print("--- Training Complete ---")
    print(f"Final model saved to:")
    print(f"  - {final_path}.zip (unique version)")
    print(f"  - models/naishi_model.zip (default - for play_vs_ai.py)")
    print(f"\nAll checkpoints saved to: models/checkpoints/{timestamp}/")

if __name__ == "__main__":
    # Default: Train against the strongest existing model (or start fresh if none exists)
    train_agent(
        total_timesteps=200000,
        use_self_play=True,
        self_play_update_freq=20480,  # Update opponent every ~10 callback checks
        checkpoint_freq=50000,  # Save checkpoint every 50k timesteps
        start_from_best=True  # Always start from the best existing model
    )
    
    # Example: Resume from specific checkpoint (uncomment to use)
    # train_agent(
    #     total_timesteps=200000,
    #     use_self_play=True,
    #     self_play_update_freq=20480,
    #     checkpoint_freq=50000,
    #     resume_from="models/checkpoints/20251020_143022/naishi_model_100000"
    # )
    
    # Example: Start completely fresh (ignore existing models)
    # train_agent(
    #     total_timesteps=200000,
    #     use_self_play=True,
    #     self_play_update_freq=20480,
    #     checkpoint_freq=50000,
    #     start_from_best=False
    # )