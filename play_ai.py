#!/usr/bin/env python3
"""
Convenience script to play Human vs AI.
Imports from src.gameplay.play_vs_ai
"""
import sys
from src.gameplay.play_vs_ai import PlayVsAI

if __name__ == "__main__":
    # Default to random policy (None uses the class's built-in random_policy)
    game = PlayVsAI(ai_policy=None)
    
    # Or load a trained model if path provided
    if len(sys.argv) > 1:
        from sb3_contrib import MaskablePPO
        model_path = sys.argv[1]
        model = MaskablePPO.load(model_path)
        
        def model_policy(obs, gs):
            action_mask = gs.get_action_mask()
            action, _ = model.predict(obs, deterministic=False, action_masks=action_mask)
            return action
        
        game = PlayVsAI(ai_policy=model_policy)
    
    game.play()
