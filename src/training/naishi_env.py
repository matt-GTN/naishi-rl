# naishi_env.py
import numpy as np
import gymnasium as gym
from gymnasium import spaces
from naishi_core.game_logic import (
    GameState,
    ACTION_DRAFT,
    ACTION_DEVELOP,
    ACTION_SWAP,
    ACTION_DISCARD,
    ACTION_RECALL,
    ACTION_DECREE,
    ACTION_END_GAME,
)

class NaishiEnv(gym.Env):
    """Gymnasium environment powered by naishi_core.GameState."""

    metadata = {"render_modes": ["human"], "render_fps": 10}

    def __init__(self, render_mode=None, seed=None, opponent_policy=None, agent_policy=None):
        super().__init__()
        self.render_mode = render_mode
        self.opponent_policy = opponent_policy
        self.agent_policy = agent_policy  # Policy for the main agent (for multi-action turns)
        self.gs: GameState = None

        # --- Spaces ---
        # 8-dimensional discrete action (same as before)
        self.action_space = spaces.MultiDiscrete([7, 10, 5, 4, 5, 5, 5, 5])
        
        # Observation space: 5 (line) + 5 (hand) + 5 (opp line) + 
        #                   5 (river tops) + 5 (river counts) + 2 (emissaries) + 
        #                   2 (decree) + 1 (turn) + 6 (flags) = 36
        # Flags: must_develop, ending_available, swap_available, discard_available, 
        #        in_draft_phase, optional_emissary_available
        # Note: Opponent hand is NEVER included (hidden information)
        # Draft phase is 31 elements (2 draft cards + 3 padding instead of 5 hand cards)
        self.observation_space = spaces.Box(0, 255, shape=(36,), dtype=np.float32)


        if seed is not None:
            self.reset(seed=seed)

    # -----------------------------------------------------------

    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed)
        self.gs = GameState.create_initial_state(seed)
        obs = self.gs.get_observation()
        info = self.gs.get_info()
        return obs, info

    # -----------------------------------------------------------

    def step(self, action):
        """Run one RL step with multi-action turn support."""
        # Apply the initial action
        obs, reward, terminated, truncated, info = self.gs.apply_action_array(action)
        
        # Handle multi-action turns for the current player
        if not (terminated or truncated):
            obs, reward, terminated, truncated, info = self._handle_multi_action_turn(
                obs, reward, terminated, truncated, info, is_opponent=False
            )
        
        # Opponent automatic move (if provided and game not over)
        if not (terminated or truncated) and self.opponent_policy is not None:
            action_mask = self._get_action_mask()
            opp_action, _ = self.opponent_policy.predict(obs, deterministic=False, action_masks=action_mask)
            obs, reward2, terminated, truncated, info = self.gs.apply_action_array(opp_action)
            reward -= reward2  # symmetric reward scheme
            
            # Handle multi-action turns for the opponent
            if not (terminated or truncated):
                obs, reward2_multi, terminated, truncated, info = self._handle_multi_action_turn(
                    obs, 0.0, terminated, truncated, info, is_opponent=True
                )
                reward -= reward2_multi  # symmetric reward scheme

        return obs, reward, terminated, truncated, info

    # -----------------------------------------------------------

    def _handle_multi_action_turn(self, obs, reward, terminated, truncated, info, is_opponent):
        """
        Handle multi-action turns according to RULES.md Section 4.
        
        After an action, check if:
        1. optional_emissary_available is True (Option A: develop → optional emissary)
        2. must_develop is True (Option B: emissary → required develop)
        
        Args:
            obs: Current observation
            reward: Accumulated reward
            terminated: Game terminated flag
            truncated: Game truncated flag
            info: Game info dict
            is_opponent: Whether this is the opponent's turn
            
        Returns:
            Tuple of (obs, reward, terminated, truncated, info) with accumulated rewards
        """
        accumulated_reward = reward
        
        # Determine which policy to use
        if is_opponent:
            policy = self.opponent_policy
        else:
            policy = self.agent_policy
        
        # Handle optional emissary (Option A: develop → optional emissary)
        if self.gs.optional_emissary_available:
            if policy is not None:
                # Policy decides whether to use optional emissary
                action_mask = self._get_action_mask()
                emissary_action, _ = policy.predict(
                    obs, deterministic=False, action_masks=action_mask
                )
                
                # Apply the action (could be swap/discard or any other action to skip)
                obs, r, terminated, truncated, info = self.gs.apply_action_array(emissary_action)
                accumulated_reward += r if not is_opponent else -r
                
                if terminated or truncated:
                    return obs, accumulated_reward, terminated, truncated, info
            else:
                # No policy available - skip optional emissary
                obs, r, terminated, truncated, info = self.gs.skip_optional_emissary()
                accumulated_reward += r if not is_opponent else -r
                return obs, accumulated_reward, terminated, truncated, info
        
        # Handle must develop (Option B: emissary → required develop)
        if self.gs.must_develop:
            if policy is not None:
                # Policy must develop
                action_mask = self._get_action_mask()
                develop_action, _ = policy.predict(
                    obs, deterministic=False, action_masks=action_mask
                )
                
                # Apply the develop action
                obs, r, terminated, truncated, info = self.gs.apply_action_array(develop_action)
                accumulated_reward += r if not is_opponent else -r
            else:
                # No policy available - this is an error state, but we'll just return
                # The next step() call should handle it
                pass
        
        return obs, accumulated_reward, terminated, truncated, info

    # -----------------------------------------------------------

    def _get_action_mask(self):
        """
        Return a mask compatible with MaskablePPO for MultiDiscrete([7,10,5,4,5,5,5,5]).
        It must have shape (sum(nvec),) = (46,) where each sub-mask corresponds
        to the legal choices for each discrete dimension.
        """
        mask_segments = []

           # --- 1️⃣ Action type (0–6)
        type_mask = np.zeros(7, dtype=np.int8)
        for t in self.gs.get_legal_action_types():
            type_mask[t] = 1
        mask_segments.append(type_mask)

           # --- 2️⃣ to 8️⃣ Other sub-actions (we allow all values, MaskablePPO will prune by type)
        for n in self.action_space.nvec[1:]:
            mask_segments.append(np.ones(n, dtype=np.int8))

           # Concatenate into shape (46,)
        return np.concatenate(mask_segments)



    # -----------------------------------------------------------

    def render(self):
        """Optional human rendering."""
        p0, p1 = self.gs.players
        print(f"\nTurn {self.gs.turn_count}, Player {self.gs.current_player_idx}")
        print(f"P0 line: {p0.line}  hand: {p0.hand}  emissaries: {p0.emissaries}")
        print(f"P1 line: {p1.line}  hand: {p1.hand}  emissaries: {p1.emissaries}")
        print(f"River tops: {[self.gs.river.get_top_card(i) for i in range(5)]}")
