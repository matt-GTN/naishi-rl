# naishi_gym_env_v2.py
"""
Improved Naishi Gym Environment with:
- Simplified action space (only meaningful actions)
- Better action masking
- Smarter random baseline
"""

import gymnasium as gym
from gymnasium import spaces
import numpy as np
import random as r
from typing import Tuple, Dict

from naishi_core import (
    Player, River, Scorer,
    CARDS, CHARACTERS, CARDS_COUNT, CARD_TO_INT,
    NUM_DECKS, CARDS_PER_DECK, LINE_SIZE, HAND_SIZE,
    INITIAL_EMISSARIES
)


class NaishiEnvV2(gym.Env):
    """
    Simplified Naishi environment focused on the core game:
    - Main action: Develop territory (choose deck)
    - Optional: Recall emissaries when needed
    - Simplified action space for faster learning
    """
    
    metadata = {'render_modes': ['human']}
    
    def __init__(self, opponent_policy=None, seed=None, reward_mode='win_loss'):
        super().__init__()
        
        self.opponent_policy = opponent_policy
        self.seed_value = seed
        self.reward_mode = reward_mode
        
        # Simplified observation space - flattened from start
        # 5 player line + 5 player hand + 5 opponent line + 5 river top + 5 river counts + 2 emissaries + 2 decree + 1 turn
        self.observation_space = spaces.Box(
            low=0, 
            high=255,
            shape=(30,),  # Simpler flat observation
            dtype=np.float32
        )
        
        # Simplified action space: Just choose which deck to develop from (0-4)
        # We'll handle emissary recall automatically
        self.action_space = spaces.Discrete(5)
        
        # Game state
        self.players = None
        self.river = None
        self.current_player_idx = 0
        self.turn_count = 0
        self.ending_available = False
        self.end_next_turn = False
    
    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        
        if seed is not None:
            r.seed(seed)
        elif self.seed_value is not None:
            r.seed(self.seed_value)
        
        self.players = [Player(0), Player(1)]
        self.river = River()
        self.current_player_idx = 0
        self.turn_count = 0
        self.ending_available = False
        self.end_next_turn = False
        
        self._setup_game()
        
        obs = self._get_obs()
        info = self._get_info()
        
        return obs, info
    
    def _setup_game(self):
        """Setup initial game state"""
        total_cards = []
        for card, count in zip(CARDS, CARDS_COUNT):
            total_cards.extend([card] * count)
        r.shuffle(total_cards)
        
        # Deal to river
        for i in range(NUM_DECKS):
            start = i * CARDS_PER_DECK
            end = (i + 1) * CARDS_PER_DECK
            self.river.decks[i] = total_cards[start:end]
        
        # Initial hands
        player_hands = [total_cards[-2:], total_cards[-4:-2]]
        
        # Exchange
        p1_choice = r.randint(0, 1)
        p2_choice = r.randint(0, 1)
        player_hands[0][p1_choice], player_hands[1][p2_choice] = \
            player_hands[1][p2_choice], player_hands[0][p1_choice]
        
        # Add mountains
        for hand in player_hands:
            hand.extend(['Mountain'] * 3)
            r.shuffle(hand)
        
        # Setup players
        for i, player in enumerate(self.players):
            player.hand = player_hands[i]
            player.line = ['Mountain'] * LINE_SIZE
    
    def _get_obs(self):
        """Get flattened observation"""
        current = self.players[self.current_player_idx]
        opponent = self.players[1 - self.current_player_idx]
        
        def encode(card):
            return CARD_TO_INT.get(card, CARD_TO_INT['Empty'])
        
        obs = []
        
        # Player line (5)
        obs.extend([encode(c) for c in current.line])
        
        # Player hand (5)
        obs.extend([encode(c) for c in current.hand])
        
        # Opponent line (5)
        obs.extend([encode(c) for c in opponent.line])
        
        # River top cards (5)
        obs.extend([encode(self.river.get_top_card(i) or 'Empty') for i in range(NUM_DECKS)])
        
        # River counts (5)
        obs.extend(self.river.cards_left())
        
        # Emissaries (2)
        obs.extend([current.emissaries, opponent.emissaries])
        
        # Decree (2)
        obs.extend([int(current.decree_used), int(opponent.decree_used)])
        
        # Turn count normalized (1)
        obs.append(min(self.turn_count / 50.0, 1.0))
        
        return np.array(obs, dtype=np.float32)
    
    def _get_info(self):
        """Get info dict"""
        return {
            'turn': self.turn_count,
            'current_player': self.current_player_idx,
            'ending_available': self.ending_available,
            'empty_decks': self.river.count_empty_decks(),
            'action_mask': self._get_action_mask(),
        }
    
    def _get_action_mask(self):
        """Return mask of valid actions (which decks have cards)"""
        mask = np.array([
            0 if self.river.is_empty(i) else 1 
            for i in range(NUM_DECKS)
        ], dtype=np.int32)
        
        # If all empty, allow action 0 (will end game)
        if mask.sum() == 0:
            mask[0] = 1
        
        return mask
    
    def step(self, action):
        """
        Execute action (develop from chosen deck)
        
        Args:
            action: Integer 0-4 (which deck to develop from)
        """
        deck_idx = int(action)
        
        reward = 0
        terminated = False
        truncated = False
        
        # Check if action is valid
        if self.river.is_empty(deck_idx):
            # Invalid action - try to recover by choosing non-empty deck
            non_empty = [i for i in range(NUM_DECKS) if not self.river.is_empty(i)]
            if non_empty:
                deck_idx = r.choice(non_empty)
            else:
                # No decks left - end game
                terminated = True
                reward = self._calculate_final_reward()
                obs = self._get_obs()
                info = self._get_info()
                return obs, reward, terminated, truncated, info
        
        # Execute develop action
        current = self.players[self.current_player_idx]
        
        # Choose which card to discard (smartly)
        discard_pos = self._choose_discard_position(current)
        
        if discard_pos < LINE_SIZE:
            location = 'line'
            pos = discard_pos
        else:
            location = 'hand'
            pos = discard_pos - LINE_SIZE
        
        new_card = self.river.draw_card(deck_idx)
        current.replace_card(location, pos, new_card)
        
        # Auto-recall emissaries if needed (simplified game)
        if current.emissaries == 0 and self.turn_count > 10:
            current.recall_emissaries(current.decree_used)
        
        # Check for game end
        if self._check_ending():
            terminated = True
            reward = self._calculate_final_reward()
        
        # Switch to opponent
        if not terminated:
            self.current_player_idx = 1 - self.current_player_idx
            self.turn_count += 1
            
            # Opponent plays
            if self.opponent_policy is not None:
                self._opponent_turn()
                
                if self._check_ending():
                    terminated = True
                    reward = self._calculate_final_reward()
                else:
                    self.current_player_idx = 1 - self.current_player_idx
                    self.turn_count += 1
        
        # Truncate if too long
        if self.turn_count > 100:
            truncated = True
            reward = self._calculate_final_reward()
        
        obs = self._get_obs()
        info = self._get_info()
        
        return obs, reward, terminated, truncated, info
    
    def _choose_discard_position(self, player):
        """
        Smart discard logic - prefer discarding mountains from line
        """
        # Try to discard mountain from line first
        for i in range(LINE_SIZE):
            if player.line[i] == 'Mountain':
                return i
        
        # Then from hand
        for i in range(HAND_SIZE):
            if player.hand[i] == 'Mountain':
                return LINE_SIZE + i
        
        # Otherwise random
        return r.randint(0, 9)
    
    def _check_ending(self):
        """Check if game should end"""
        if self.end_next_turn:
            return True
        
        empty_count = self.river.count_empty_decks()
        
        if empty_count >= 1:
            self.ending_available = True
        
        if empty_count >= 2:
            if self.current_player_idx == 0:
                self.end_next_turn = True
                return False
            else:
                return True
        
        return False
    
    def _calculate_final_reward(self):
        """Calculate reward based on mode"""
        scores = []
        for player in self.players:
            cards = player.get_all_cards()
            # Simple ninja handling
            for i, card in enumerate(cards):
                if card == 'Ninja':
                    for other in cards:
                        if other in CHARACTERS and other != 'Ninja':
                            cards[i] = other
                            break
            score = Scorer.calculate_score(cards)['Total']
            scores.append(score)
        
        score_diff = scores[0] - scores[1]
        
        if self.reward_mode == 'win_loss':
            return 1.0 if score_diff > 0 else -1.0 if score_diff < 0 else 0.0
        elif self.reward_mode == 'scaled':
            return np.clip(score_diff / 100.0, -1.0, 1.0)
        else:
            return score_diff / 100.0
    
    def _opponent_turn(self):
        """Execute opponent's turn"""
        obs = self._get_obs()
        action = self.opponent_policy(obs, self)
        # Don't calculate reward for opponent turn
        _, _, _, _, _ = self.step(action)
    
    def render(self, mode='human'):
        """Render game state"""
        lines = [
            f"\n=== Turn {self.turn_count}, Player {self.current_player_idx + 1} ===",
            f"River: {self.river.cards_left()}",
            f"Top: {[self.river.get_top_card(i) for i in range(NUM_DECKS)]}",
        ]
        
        for i, player in enumerate(self.players):
            lines.append(f"\nPlayer {i+1}:")
            lines.append(f"  Line: {player.line}")
            lines.append(f"  Hand: {player.hand}")
            lines.append(f"  Emissaries: {player.emissaries}")
        
        print("\n".join(lines))


def smart_baseline_policy(obs, env):
    """
    Smarter baseline policy:
    - Prefers non-empty decks
    - Slightly biased towards certain cards
    """
    action_mask = env._get_action_mask()
    valid_actions = np.where(action_mask == 1)[0]
    
    if len(valid_actions) == 0:
        return 0
    
    # Get top cards from valid decks
    deck_values = []
    for deck_idx in valid_actions:
        top_card = env.river.get_top_card(deck_idx)
        # Simple heuristic: prefer character cards over buildings
        if top_card in CHARACTERS:
            value = 2.0
        elif top_card in ['Fort', 'Torii', 'Banner']:
            value = 1.5
        elif top_card == 'Rice fields':
            value = 1.2
        else:
            value = 1.0
        deck_values.append(value)
    
    # Choose with weighted probability
    probs = np.array(deck_values)
    probs = probs / probs.sum()
    
    return np.random.choice(valid_actions, p=probs)


def simple_masked_policy(obs, env):
    """Simple policy that just picks valid random deck"""
    action_mask = env._get_action_mask()
    valid_actions = np.where(action_mask == 1)[0]
    return np.random.choice(valid_actions) if len(valid_actions) > 0 else 0