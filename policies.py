# policies.py
"""
A central location for custom policy classes used in the Naishi RL project.
"""
import numpy as np

class MaskedRandomPolicy:
    """
    A simple policy that selects a random valid action from a given action mask.
    This is used as a baseline opponent for training.
    """
    def __init__(self, action_space):
        self.action_space = action_space

    def predict(self, obs, deterministic=True, action_masks=None):
        """
        Predicts an action, respecting the provided action mask.
        """
        # The primary action mask is the first `n` elements, where n is the number of primary actions.
        primary_action_mask = action_masks[:self.action_space.nvec[0]]
        
        valid_actions = np.where(primary_action_mask)[0]
        
        # Create a full random action, but overwrite the primary action type with a valid one.
        action = self.action_space.sample()
        if len(valid_actions) > 0:
            action[0] = np.random.choice(valid_actions)
        
        # Return format matches Stable-Baselines3's predict method.
        return action, None


class SelfPlayPolicy:
    """
    A policy wrapper that uses a trained model for self-play training.
    The model is periodically updated during training to play against newer versions.
    """
    def __init__(self, model=None):
        self.model = model
    
    def update_model(self, new_model):
        """Update the opponent model to a newer version."""
        self.model = new_model
    
    def predict(self, obs, deterministic=True, action_masks=None):
        """
        Predicts an action using the wrapped model.
        Falls back to random if no model is set.
        """
        if self.model is None:
            # Fallback to random action if no model yet
            from naishi_env import NaishiEnv
            action_space = NaishiEnv(opponent_policy=None).action_space
            primary_action_mask = action_masks[:action_space.nvec[0]]
            valid_actions = np.where(primary_action_mask)[0]
            action = action_space.sample()
            if len(valid_actions) > 0:
                action[0] = np.random.choice(valid_actions)
            return action, None
        
        # Use the model to predict
        action, _ = self.model.predict(obs, deterministic=deterministic)
        
        # Validate action against mask
        primary_action_mask = action_masks[:len(action_masks)]
        if not primary_action_mask[action[0]]:
            # If invalid, choose random valid action
            valid_actions = np.where(primary_action_mask)[0]
            if len(valid_actions) > 0:
                action[0] = np.random.choice(valid_actions)
        
        return action, None