# naishi_env.py
"""
Gymnasium environment for training RL agents to play Naishi.
Includes full game mechanics: draft phase, develop, swap, discard, recall, decree, and end game.
The draft phase (initial card swap) is integrated as the first action of the game.
"""

import gymnasium as gym
from gymnasium import spaces
import numpy as np
import random as r
from typing import List

from naishi_core import (
    Player, River, Scorer,
    CARDS, CHARACTERS, CARDS_COUNT, CARD_TO_INT,
    NUM_DECKS, CARDS_PER_DECK, LINE_SIZE, HAND_SIZE,
    INITIAL_EMISSARIES
)

# Constants for the expanded action space
ACTION_DRAFT = 0  # NEW: Draft phase action (choose which card to give away)
ACTION_DEVELOP = 1
ACTION_SWAP = 2
ACTION_DISCARD = 3
ACTION_RECALL = 4
ACTION_DECREE = 5
ACTION_END_GAME = 6

class NaishiEnv(gym.Env):
    metadata = {'render_modes': ['human']}

    def __init__(self, opponent_policy, seed=None):
        super().__init__()
        
        self.opponent_policy = opponent_policy
        self.seed_value = seed
        
        # Observation space includes draft cards, river tops, ending_available, swap spots, and discard spots
        # [5 line, 5 hand, 5 opp line, 5 opp hand, 5 river tops, 5 river counts, 2 emissaries, 2 decree, 1 turn, 5 flags]
        # Total: 5 + 5 + 5 + 5 + 5 + 5 + 2 + 2 + 1 + 5 = 40
        self.observation_space = spaces.Box(
            low=0, high=255, shape=(40,), dtype=np.float32
        )
        
        # Action space now has 7 primary actions (added DRAFT)
        # [action_type, position, deck, swap_type, pos1, pos2, deck1, deck2]
        self.action_space = spaces.MultiDiscrete([
            7, 10, 5, 4, 5, 5, 5, 5,
        ])

        # Game state
        self.players: List[Player] = []
        self.river: River = None
        self.current_player_idx = 0
        self.turn_count = 0
        self.ending_available = False
        self.end_next_turn = False
        self.must_develop = False
        self.available_swaps = [0, 0, 0]  # 3 swap spots (shared)
        self.available_discards = [0, 0]  # 2 discard spots (shared)
        
        # Draft phase state
        self.in_draft_phase = False
        self.draft_hands = [[], []]  # Initial 2 cards for each player
        self.river_tops_at_draft = []  # River top cards visible during draft

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        
        if seed is not None: r.seed(seed)
        elif self.seed_value is not None: r.seed(self.seed_value)
        
        self.players = [Player(0), Player(1)]
        self.river = River()
        self.current_player_idx = 0
        self.turn_count = 0
        self.ending_available = False
        self.end_next_turn = False
        self.must_develop = False
        self.available_swaps = [0, 0, 0]  # 3 swap spots (shared)
        self.available_discards = [0, 0]  # 2 discard spots (shared)
        
        # Initialize draft phase
        self.in_draft_phase = True
        self._setup_draft()
        
        obs = self._get_obs()
        info = self._get_info()
        
        return obs, info

    def _setup_draft(self):
        """
        Setup the draft phase according to RULES.md:
        1. Shuffle all cards
        2. Deal River: 5 decks of 6 cards each
        3. Deal starting hands: Each player receives 2 random cards
        4. Players view river tops and choose which card to give away
        """
        total_cards = []
        for card, count in zip(CARDS, CARDS_COUNT):
            total_cards.extend([card] * count)
        r.shuffle(total_cards)
        
        # Deal river (5 decks of 6 cards)
        for i in range(NUM_DECKS):
            self.river.decks[i] = total_cards[i*CARDS_PER_DECK:(i+1)*CARDS_PER_DECK]
        
        # Store river tops for observation during draft
        self.river_tops_at_draft = [self.river.get_top_card(i) or 'Empty' for i in range(NUM_DECKS)]
        
        # Deal 2 cards to each player from the remaining cards
        self.draft_hands = [total_cards[-2:], total_cards[-4:-2]]
        
        # Initialize players with empty hands/lines (will be filled after draft)
        for player in self.players:
            player.hand = []
            player.line = ['Mountain'] * LINE_SIZE
    
    def _complete_draft(self, p0_choice, p1_choice):
        """
        Complete the draft phase by swapping chosen cards and adding mountains.
        
        Args:
            p0_choice: Index (0 or 1) of card Player 0 gives away
            p1_choice: Index (0 or 1) of card Player 1 gives away
        """
        # Swap the chosen cards
        self.draft_hands[0][p0_choice], self.draft_hands[1][p1_choice] = \
            self.draft_hands[1][p1_choice], self.draft_hands[0][p0_choice]
        
        # Add 3 Mountains to each player's hand and shuffle
        for hand in self.draft_hands:
            hand.extend(['Mountain'] * 3)
            r.shuffle(hand)
        
        # Assign final hands to players
        for i, player in enumerate(self.players):
            player.hand = self.draft_hands[i]
        
        # Clear draft state
        self.in_draft_phase = False
        self.draft_hands = [[], []]
        self.river_tops_at_draft = []

    def _get_obs(self):
        """
        Generates the observation array.
        During draft phase: includes draft cards and river tops.
        During main game: includes full game state.
        """
        encode = lambda card: CARD_TO_INT.get(card, CARD_TO_INT['Empty'])
        
        if self.in_draft_phase:
            # Draft phase observation
            current_draft_hand = self.draft_hands[self.current_player_idx]
            opponent_draft_hand = self.draft_hands[1 - self.current_player_idx]
            
            # Pad draft hands to 2 cards (in case of any issues)
            while len(current_draft_hand) < 2:
                current_draft_hand.append('Empty')
            while len(opponent_draft_hand) < 2:
                opponent_draft_hand.append('Empty')
            
            obs = [
                # Current player's line (all Mountains during draft)
                *[encode('Mountain')] * LINE_SIZE,
                # Current player's draft hand (2 cards, padded to 5 for consistency)
                *[encode(current_draft_hand[0])],
                *[encode(current_draft_hand[1])],
                *[encode('Empty')] * 3,
                # Opponent's line (all Mountains during draft)
                *[encode('Mountain')] * LINE_SIZE,
                # Opponent's hand (hidden during draft)
                *[encode('Empty')] * HAND_SIZE,
                # River tops visible during draft
                *[encode(card) for card in self.river_tops_at_draft],
                # River counts
                *self.river.cards_left(),
                # Emissaries (both start with 2)
                INITIAL_EMISSARIES,
                INITIAL_EMISSARIES,
                # Decree flags (both False)
                0, 0,
                # Turn count (0 during draft)
                0.0,
                # Flags
                0,  # must_develop (False during draft)
                0,  # ending_available (False during draft)
                1,  # swap spots available (True)
                1,  # discard spots available (True)
                # Draft phase flag
                1,  # in_draft_phase
            ]
        else:
            # Main game observation
            current = self.players[self.current_player_idx]
            opponent = self.players[1 - self.current_player_idx]
            
            obs = [
                *[encode(c) for c in current.line],
                *[encode(c) for c in current.hand],
                *[encode(c) for c in opponent.line],
                *[encode('Empty')] * HAND_SIZE,  # Opponent hand (always hidden, padded for consistency)
                *[encode(self.river.get_top_card(i) or 'Empty') for i in range(NUM_DECKS)],
                *self.river.cards_left(),
                current.emissaries,
                opponent.emissaries,
                int(current.decree_used),
                int(opponent.decree_used),
                min(self.turn_count / 50.0, 1.0),
                int(self.must_develop),
                int(self.ending_available),
                int(0 in self.available_swaps),
                int(0 in self.available_discards),
                0,  # in_draft_phase (False)
            ]
        
        return np.array(obs, dtype=np.float32)

    def _get_info(self):
        return {'turn': self.turn_count, 'action_mask': self._get_action_mask()}

    def _get_action_mask(self):
        """
        Action mask that includes draft action during draft phase,
        and standard actions during main game.
        """
        mask = np.zeros(self.action_space.nvec[0], dtype=bool)
        
        if self.in_draft_phase:
            # During draft phase, only DRAFT action is available
            mask[ACTION_DRAFT] = True
            return mask
        
        player = self.players[self.current_player_idx]
        
        if self.must_develop:
            mask[ACTION_DEVELOP] = True
            return mask

        # Standard actions
        mask[ACTION_DEVELOP] = True
        if player.emissaries > 0:
            # Check if swap spots are available
            if 0 in self.available_swaps:
                mask[ACTION_SWAP] = True
            # Check if discard spots are available
            if 0 in self.available_discards:
                mask[ACTION_DISCARD] = True
            if not self.players[0].decree_used and not self.players[1].decree_used:
                mask[ACTION_DECREE] = True
        # Check if player can recall (must have fewer than max available)
        max_emissaries = 1 if player.decree_used else INITIAL_EMISSARIES
        if player.emissaries < max_emissaries:
            mask[ACTION_RECALL] = True
        
        # Add end game action if available
        if self.ending_available:
            mask[ACTION_END_GAME] = True
            
        return mask

    def step(self, action):
        action_type = action[0]
        
        turn_ends = False
        reward = 0.0
        terminated = False

        # --- Handle Draft Phase ---
        if self.in_draft_phase:
            if action_type == ACTION_DRAFT:
                # Player chooses which card to give away (0 or 1)
                choice = action[1] % 2  # Use position parameter as choice
                
                # Store this player's choice
                if self.current_player_idx == 0:
                    p0_choice = choice
                    # Switch to opponent for their draft choice
                    self.current_player_idx = 1
                    
                    # If opponent policy exists, get their choice
                    if self.opponent_policy:
                        obs = self._get_obs()
                        info = self._get_info()
                        opponent_action, _ = self.opponent_policy.predict(
                            obs, deterministic=True, action_masks=info.get('action_mask')
                        )
                        p1_choice = opponent_action[1] % 2
                        
                        # Complete the draft with both choices
                        self._complete_draft(p0_choice, p1_choice)
                        
                        # Return to player 0 for main game
                        self.current_player_idx = 0
                    else:
                        # No opponent, just complete with random choice
                        p1_choice = r.randint(0, 1)
                        self._complete_draft(p0_choice, p1_choice)
                        self.current_player_idx = 0
                else:
                    # This shouldn't happen in normal flow, but handle it
                    p1_choice = choice
                    p0_choice = r.randint(0, 1)
                    self._complete_draft(p0_choice, p1_choice)
                    self.current_player_idx = 0
            else:
                # Invalid action during draft phase
                reward = -0.1
            
            # Return observation after draft
            obs = self._get_obs()
            info = self._get_info()
            return obs, reward, terminated, False, info
        
        # --- Main Game Phase ---
        player = self.players[self.current_player_idx]

        # --- Update game state flags first ---
        self._update_ending_availability()

        # --- Action Execution with Validity Checks ---
        if self.must_develop and action_type != ACTION_DEVELOP:
            reward = -0.1
            turn_ends = True
        
        elif action_type == ACTION_DEVELOP:
            # (Same as before)
            discard_pos, deck_idx = action[1], action[2]
            if not self.river.is_empty(deck_idx):
                location = 'line' if discard_pos < LINE_SIZE else 'hand'
                pos = discard_pos % LINE_SIZE
                player.replace_card(location, pos, self.river.draw_card(deck_idx))
            turn_ends = True
            self.must_develop = False

        elif action_type == ACTION_SWAP:
            if player.emissaries > 0 and 0 in self.available_swaps:
                player.use_emissary()
                swap_type = action[3]  # 0=hand, 1=line, 2=between, 3=river
                pos1, pos2 = action[4], action[5]
                
                if swap_type == 0:  # Hand swap
                    player.swap_in_hand(pos1, pos2)
                elif swap_type == 1:  # Line swap
                    player.swap_in_line(pos1, pos2)
                elif swap_type == 2:  # Between hand and line
                    player.swap_between_line_and_hand(pos1)
                elif swap_type == 3:  # River swap
                    if not self.river.is_empty(pos1) and not self.river.is_empty(pos2) and pos1 != pos2:
                        self.river.swap_top_cards(pos1, pos2)
                
                # Mark swap spot as used
                for i, spot in enumerate(self.available_swaps):
                    if spot == 0:
                        self.available_swaps[i] = self.current_player_idx + 1
                        break
                
                self.must_develop = True
            else: reward = -0.1; turn_ends = True
        
        elif action_type == ACTION_DISCARD:
            if player.emissaries > 0 and 0 in self.available_discards:
                player.use_emissary()
                deck1, deck2 = action[6], action[7]
                if deck1 != deck2: self.river.discard_top_cards(deck1, deck2)
                
                # Mark discard spot as used
                for i, spot in enumerate(self.available_discards):
                    if spot == 0:
                        self.available_discards[i] = self.current_player_idx + 1
                        break
                
                self.must_develop = True
            else: reward = -0.1; turn_ends = True

        elif action_type == ACTION_RECALL:
            # Check if player can recall (must have fewer than max available)
            max_emissaries = 1 if player.decree_used else INITIAL_EMISSARIES
            if player.emissaries < max_emissaries:
                # Clear spots used by this player
                for i, spot in enumerate(self.available_swaps):
                    if spot == self.current_player_idx + 1:
                        self.available_swaps[i] = 0
                for i, spot in enumerate(self.available_discards):
                    if spot == self.current_player_idx + 1:
                        self.available_discards[i] = 0
                
                player.recall_emissaries(player.decree_used)
            else: reward = -0.1
            turn_ends = True

        elif action_type == ACTION_DECREE:
            if player.emissaries > 0 and not self.players[0].decree_used and not self.players[1].decree_used:
                player.use_emissary()
                player.decree_used = True
                
                discard_pos = action[1]  # Position to swap (0-9)
                opponent = self.players[1 - self.current_player_idx]
                
                # Determine location and position
                location = 'line' if discard_pos < LINE_SIZE else 'hand'
                pos = discard_pos % LINE_SIZE
                
                # Swap cards between players at the same position
                if location == 'line':
                    player.line[pos], opponent.line[pos] = opponent.line[pos], player.line[pos]
                else:
                    player.hand[pos], opponent.hand[pos] = opponent.hand[pos], player.hand[pos]
            else: reward = -0.1
            turn_ends = True
            
        elif action_type == ACTION_END_GAME:
            if self.ending_available:
                self.end_next_turn = True
            else:
                reward = -0.1
            turn_ends = True


        # --- Post-Action State Update ---
        if not terminated:
            terminated = self._check_forced_ending()
            
        if terminated:
            reward += self._calculate_final_reward()
        
        if turn_ends and not terminated:
            self.current_player_idx = 1 - self.current_player_idx
            self.turn_count += 1
            if self.opponent_policy:
                self._opponent_turn()
                if not terminated: terminated = self._check_forced_ending()
                if terminated: reward += self._calculate_final_reward()
                else: self.current_player_idx = 1 - self.current_player_idx
        
        truncated = self.turn_count > 100
        if truncated and not terminated:
            reward += self._calculate_final_reward()

        obs = self._get_obs()
        info = self._get_info()
        
        return obs, reward, terminated, truncated, info

    def _update_ending_availability(self):
        """Sets the flag if at least one river deck is empty."""
        if not self.ending_available:
            if self.river.count_empty_decks() >= 1:
                self.ending_available = True

    def _check_forced_ending(self):
        """Checks for automatic game-ending conditions."""
        if self.end_next_turn: return True
        if self.river.count_empty_decks() >= 2:
            # Game ends after the second player's turn
            if self.current_player_idx == 1:
                return True
            else:
                self.end_next_turn = True
        return False
        
    def _opponent_turn(self):
        """Execute opponent's turn using their policy"""
        if not self.opponent_policy:
            return
        
        # Opponent takes actions until their turn ends
        opponent_turn_done = False
        while not opponent_turn_done:
            obs = self._get_obs()
            info = self._get_info()
            action_mask = info.get('action_mask')
            
            # Get opponent's action
            opponent_action, _ = self.opponent_policy.predict(
                obs, 
                deterministic=True, 
                action_masks=action_mask
            )
            
            # Execute opponent's action
            action_type = opponent_action[0]
            player = self.players[self.current_player_idx]
            
            # Draft action should not happen here (handled in main step)
            if action_type == ACTION_DRAFT:
                opponent_turn_done = True
                continue
            
            # Check if action ends turn
            if action_type == ACTION_DEVELOP:
                discard_pos, deck_idx = opponent_action[1], opponent_action[2]
                if not self.river.is_empty(deck_idx):
                    location = 'line' if discard_pos < LINE_SIZE else 'hand'
                    pos = discard_pos % LINE_SIZE
                    player.replace_card(location, pos, self.river.draw_card(deck_idx))
                opponent_turn_done = True
                self.must_develop = False
                
            elif action_type == ACTION_SWAP:
                if player.emissaries > 0 and 0 in self.available_swaps:
                    player.use_emissary()
                    swap_type = opponent_action[3]
                    pos1, pos2 = opponent_action[4], opponent_action[5]
                    
                    if swap_type == 0:
                        player.swap_in_hand(pos1, pos2)
                    elif swap_type == 1:
                        player.swap_in_line(pos1, pos2)
                    elif swap_type == 2:
                        player.swap_between_line_and_hand(pos1)
                    elif swap_type == 3:
                        if not self.river.is_empty(pos1) and not self.river.is_empty(pos2) and pos1 != pos2:
                            self.river.swap_top_cards(pos1, pos2)
                    
                    # Mark swap spot as used
                    for i, spot in enumerate(self.available_swaps):
                        if spot == 0:
                            self.available_swaps[i] = self.current_player_idx + 1
                            break
                    
                    self.must_develop = True
                else:
                    opponent_turn_done = True
                    
            elif action_type == ACTION_DISCARD:
                if player.emissaries > 0 and 0 in self.available_discards:
                    player.use_emissary()
                    deck1, deck2 = opponent_action[6], opponent_action[7]
                    if deck1 != deck2:
                        self.river.discard_top_cards(deck1, deck2)
                    
                    # Mark discard spot as used
                    for i, spot in enumerate(self.available_discards):
                        if spot == 0:
                            self.available_discards[i] = self.current_player_idx + 1
                            break
                    
                    self.must_develop = True
                else:
                    opponent_turn_done = True
                    
            elif action_type == ACTION_RECALL:
                # Check if player can recall (must have fewer than max available)
                max_emissaries = 1 if player.decree_used else INITIAL_EMISSARIES
                if player.emissaries < max_emissaries:
                    # Clear spots used by this player
                    for i, spot in enumerate(self.available_swaps):
                        if spot == self.current_player_idx + 1:
                            self.available_swaps[i] = 0
                    for i, spot in enumerate(self.available_discards):
                        if spot == self.current_player_idx + 1:
                            self.available_discards[i] = 0
                    
                    player.recall_emissaries(player.decree_used)
                opponent_turn_done = True
                
            elif action_type == ACTION_DECREE:
                if player.emissaries > 0 and not self.players[0].decree_used and not self.players[1].decree_used:
                    player.use_emissary()
                    player.decree_used = True
                    
                    discard_pos = opponent_action[1]
                    opponent = self.players[1 - self.current_player_idx]
                    
                    location = 'line' if discard_pos < LINE_SIZE else 'hand'
                    pos = discard_pos % LINE_SIZE
                    
                    if location == 'line':
                        player.line[pos], opponent.line[pos] = opponent.line[pos], player.line[pos]
                    else:
                        player.hand[pos], opponent.hand[pos] = opponent.hand[pos], player.hand[pos]
                opponent_turn_done = True
                
            elif action_type == ACTION_END_GAME:
                if self.ending_available:
                    self.end_next_turn = True
                opponent_turn_done = True
            else:
                # Unknown action, end turn
                opponent_turn_done = True

    def _calculate_final_reward(self):
        # (This function remains the same)
        scores = []
        for p in self.players:
            cards = p.get_all_cards()
            if 'Ninja' in cards:
                for i, card in enumerate(cards):
                    if card == 'Ninja':
                        cards[i] = r.choice([c for c in CHARACTERS if c != 'Ninja'])
            scores.append(Scorer.calculate_score(cards)['Total'])
        score_diff = scores[0] - scores[1]
        
        if self.current_player_idx == 1: score_diff *= -1

        return 1.0 if score_diff > 0 else -1.0 if score_diff < 0 else 0.0