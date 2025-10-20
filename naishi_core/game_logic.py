# naishi_core/game_logic.py
"""Central game logic / rule engine for Naishi.

This module implements GameState which is the single source of truth for:
- draft setup and resolution (RULES.md Section 2: Setup)
- action legality (RULES.md Section 4: Turn Structure, Section 5: Actions)
- action application (RULES.md Section 5: Actions)
- endgame / forced-end rules (RULES.md Section 7: Game End)
- serialization helpers to produce the same observation layout used by NaishiEnv

It intentionally mirrors the behavior in naishi_env.py / naishi_pvp.py so those modules
can be refactored to call into GameState rather than reimplement rules.

RULES.md Compliance:
- Section 2: Setup - Draft phase with card exchange and Mountain distribution
- Section 4: Turn Structure - Option A (Develop → Optional Emissary) and Option B (Emissary → Required Develop)
- Section 5: Actions - All 6 action types (Develop, Swap, Discard, Recall, Decree, End)
- Section 6: Emissary System - Spot tracking (3 swaps, 2 discards) and Decree mechanics
- Section 7: Game End - Declare end (1+ decks) and auto-end (2+ decks)
- Section 8: Scoring - Delegated to Scorer class
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
import random as r
import numpy as np

from .player import Player
from .river import River
from .scorer import Scorer
from .constants import (
    NUM_DECKS, CARDS_PER_DECK, CARDS, CARDS_COUNT,
    LINE_SIZE, HAND_SIZE, INITIAL_EMISSARIES,
    CARD_TO_INT, INT_TO_CARD
)

# Action ids (same as NaishiEnv / NaishiPvP)
ACTION_DRAFT = 0
ACTION_DEVELOP = 1
ACTION_SWAP = 2
ACTION_DISCARD = 3
ACTION_RECALL = 4
ACTION_DECREE = 5
ACTION_END_GAME = 6

# Helper alias for array-shaped action used by envs (length 8)
# [action_type, position(0-9), deck(0-4), swap_type(0-3), pos1(0-4), pos2(0-4), deck1(0-4), deck2(0-4)]


@dataclass
class GameState:
    """Core game state for Naishi.
    
    This class maintains all game state and enforces RULES.md compliance.
    
    Turn State Fields (RULES.md Section 4: Turn Structure):
    - optional_emissary_available: True after develop if emissary can be used (Option A)
    - must_develop: True after emissary-first action, requiring develop (Option B)
    - last_action_type: Track the last action type taken this turn
    
    Emissary State Fields (RULES.md Section 6: Emissary System):
    - available_swaps: 3 shared spots for swap actions (0=free, 1/2=player marker)
    - available_discards: 2 shared spots for discard actions (0=free, 1/2=player marker)
    
    Game End Fields (RULES.md Section 7: Game End):
    - ending_available: True when 1+ decks empty (allows declare end)
    - end_next_turn: True when game should end after opponent's turn
    """
    players: List[Player] = field(default_factory=lambda: [Player(0), Player(1)])
    river: River = field(default_factory=River)
    current_player_idx: int = 0
    turn_count: int = 0

    # Emissary pools (shared): 0 means free, 1/2 mean player 1/2 used that spot
    # RULES.md Section 6: Emissary System - 3 swap spots, 2 discard spots (shared)
    available_swaps: List[int] = field(default_factory=lambda: [0, 0, 0])   # length 3
    available_discards: List[int] = field(default_factory=lambda: [0, 0])   # length 2

    # Flags and intermediate state
    must_develop: bool = False  # RULES.md Section 4: Option B - Required develop after emissary
    ending_available: bool = False  # RULES.md Section 7: True when 1+ decks empty
    end_next_turn: bool = False  # RULES.md Section 7: True when game ends after opponent's turn
    
    # Turn state tracking (RULES.md Section 4: Turn Structure)
    optional_emissary_available: bool = False  # True after develop if emissary can be used (Option A)
    last_action_type: Optional[int] = None  # Track the last action type taken this turn

    # Draft state
    in_draft_phase: bool = True
    draft_hands: List[List[str]] = field(default_factory=lambda: [[], []])
    river_tops_at_draft: List[Optional[str]] = field(default_factory=list)

    # deterministic randomness (optional)
    rng_seed: Optional[int] = None

    # guard: safe maximum turns before forced truncate if used externally
    max_turns_truncate: int = 100

    # ----- Construction helpers -----
    @classmethod
    def create_initial_state(cls, seed: Optional[int] = None) -> "GameState":
        s = cls()
        if seed is not None:
            r.seed(seed)
            s.rng_seed = seed
        # initialize players, river
        s.players = [Player(0), Player(1)]
        s.river = River()
        s.current_player_idx = 0
        s.turn_count = 0
        s.available_swaps = [0, 0, 0]
        s.available_discards = [0, 0]
        s.must_develop = False
        s.ending_available = False
        s.end_next_turn = False
        s.optional_emissary_available = False
        s.last_action_type = None
        s.in_draft_phase = True
        s.draft_hands = [[], []]
        s._setup_draft()
        return s

    def clear_turn_state(self):
        """Clear turn-specific state flags at the start of a new turn.
        
        RULES.md Section 4: Turn Structure
        This resets turn state flags when switching players:
        - optional_emissary_available: Whether optional emissary can be used after develop (Option A)
        - must_develop: Whether develop is required after emissary-first action (Option B)
        - last_action_type: The last action type taken
        
        Called when switching to a new player's turn.
        """
        self.optional_emissary_available = False
        self.must_develop = False
        self.last_action_type = None

    def _can_use_optional_emissary(self) -> bool:
        """Check if optional emissary can be used after develop (RULES.md Section 4: Option A).
        
        Optional emissary is available if:
        1. Player has emissaries available
        2. There are free emissary spots (swap or discard spots available)
        
        Returns:
            bool: True if optional emissary can be used, False otherwise
        """
        player = self.players[self.current_player_idx]
        
        # Must have at least one emissary
        if player.emissaries <= 0:
            return False
        
        # Must have at least one free spot (swap or discard)
        has_swap_spot = 0 in self.available_swaps
        has_discard_spot = 0 in self.available_discards
        
        return has_swap_spot or has_discard_spot

    def skip_optional_emissary(self) -> Tuple[np.ndarray, float, bool, bool, Dict[str, Any]]:
        """Skip the optional emissary after develop (RULES.md Section 4: Option A).
        
        This method should be called when the player chooses not to use the optional
        emissary after developing. It clears the flag and ends the turn.
        
        Returns:
            Tuple: (obs, reward, terminated, truncated, info) - same as apply_action
        """
        if not self.optional_emissary_available:
            # Not in optional emissary state, return current state with no penalty
            return self.get_observation(), 0.0, False, False, self.get_info()
        
        # Clear the flag and end turn
        self.optional_emissary_available = False
        
        # Switch to next player
        self.current_player_idx = 1 - self.current_player_idx
        self.turn_count += 1
        self.clear_turn_state()
        
        # Check for truncation
        truncated = self.turn_count > self.max_turns_truncate
        
        return self.get_observation(), 0.0, False, truncated, self.get_info()

    # ----- Draft -----
    def _setup_draft(self):
        """Set up river decks, draft hands and initial mountains.
        
        RULES.md Section 2: Setup
        - Shuffle all 34 cards
        - Deal 5 decks of 6 cards each (River)
        - Deal 2 cards to each player for draft
        - Initialize each player's Line with 5 Mountains
        """
        total_cards = []
        for card, count in zip(CARDS, CARDS_COUNT):
            total_cards.extend([card] * count)
        r.shuffle(total_cards)

        # deal river: NUM_DECKS decks of CARDS_PER_DECK
        self.river.decks = []
        for i in range(NUM_DECKS):
            start = i * CARDS_PER_DECK
            self.river.decks.append(total_cards[start:start + CARDS_PER_DECK])

        # store river tops for draft observation
        self.river_tops_at_draft = [self.river.get_top_card(i) or 'Empty' for i in range(NUM_DECKS)]

        # remaining cards -> give 2 each for draft phase
        remaining = total_cards[NUM_DECKS * CARDS_PER_DECK:]
        assert len(remaining) >= 4, "Not enough cards for draft distribution"
        # Player 0 gets first 2 cards, Player 1 gets next 2 cards
        self.draft_hands = [remaining[:2], remaining[2:4]]

        # players start with empty line and will receive mountains and draft result at completion
        for p in self.players:
            p.hand = []
            p.line = ['Mountain'] * LINE_SIZE

    def _complete_draft(self, p0_choice: int, p1_choice: int):
        """Resolve draft by swapping chosen cards, adding mountains and giving final hands.
        
        RULES.md Section 2: Setup - Draft Phase
        - Each player chooses 1 card to give to opponent
        - Cards are exchanged simultaneously
        - Each player receives 3 Mountains, shuffled into their hand
        - Final state: 5 cards in Hand, 5 Mountains in Line
        """
        # swap chosen cards between draft hands
        self.draft_hands[0][p0_choice], self.draft_hands[1][p1_choice] = \
            self.draft_hands[1][p1_choice], self.draft_hands[0][p0_choice]

        # add 3 Mountains to each draft hand and shuffle
        for hand in self.draft_hands:
            hand.extend(['Mountain'] * 3)
            r.shuffle(hand)

        # assign to players
        for i, p in enumerate(self.players):
            p.hand = self.draft_hands[i][:HAND_SIZE]  # ensure length HAND_SIZE

        # clear draft state
        self.in_draft_phase = False
        self.river_tops_at_draft = []
        self.draft_hands = [[], []]

    # ----- Action encoding helpers -----
    @staticmethod
    def action_array_to_dict(action_array: List[int]) -> Dict[str, int]:
        """Convert the env's length-8 action array into a dict for clarity."""
        return {
            "type": int(action_array[0]),
            "pos": int(action_array[1]),    # 0..9 (line + hand)
            "deck": int(action_array[2]),   # 0..4
            "swap_type": int(action_array[3]),  # 0..3
            "pos1": int(action_array[4]),   # 0..4
            "pos2": int(action_array[5]),   # 0..4
            "deck1": int(action_array[6]),  # 0..4
            "deck2": int(action_array[7])   # 0..4
        }

    # ----- Legal actions -----
    def get_legal_action_types(self, player_idx: Optional[int] = None) -> List[int]:
        """Return list of allowed primary action types for the current player.
        
        RULES.md Section 4: Turn Structure
        - If must_develop is True: Only ACTION_DEVELOP allowed (Option B)
        - If optional_emissary_available is True: Only emissary actions allowed (Option A)
        - Otherwise: All applicable actions based on game state
        
        RULES.md Section 5: Actions
        - ACTION_DEVELOP: Always available (unless deck empty)
        - ACTION_SWAP/DISCARD: Requires emissaries and free spots
        - ACTION_RECALL: Only if below max emissaries
        - ACTION_DECREE: Once per game, requires emissary
        - ACTION_END_GAME: Only when 1+ decks empty
        """
        if self.in_draft_phase:
            return [ACTION_DRAFT]

        player = self.players[self.current_player_idx]
        allowed = []

        if self.must_develop:
            return [ACTION_DEVELOP]

        # RULES.md Section 4: If optional emissary is available after develop
        # Only emissary actions (swap/discard) are legal, plus the option to skip (handled by caller)
        if self.optional_emissary_available:
            if player.emissaries > 0:
                if 0 in self.available_swaps:
                    allowed.append(ACTION_SWAP)
                if 0 in self.available_discards:
                    allowed.append(ACTION_DISCARD)
            # Note: The caller (env/UI) should also offer a "skip" or "pass" option
            # which would clear the flag and end the turn
            return allowed

        # DEVELOP always allowed (unless river deck empty chosen, that's validated on application)
        allowed.append(ACTION_DEVELOP)

        # emissary actions only if player has emissaries
        if player.emissaries > 0:
            if 0 in self.available_swaps:
                allowed.append(ACTION_SWAP)
            if 0 in self.available_discards:
                allowed.append(ACTION_DISCARD)
            # decree: only if neither player used it
            if not self.players[0].decree_used and not self.players[1].decree_used:
                allowed.append(ACTION_DECREE)

        # recall allowed if player has fewer than max (max depends on decree)
        max_emiss = 1 if player.decree_used else INITIAL_EMISSARIES
        if player.emissaries < max_emiss:
            allowed.append(ACTION_RECALL)

        # end game if available
        if self.ending_available:
            allowed.append(ACTION_END_GAME)

        return allowed

    def is_legal_action_array(self, action_array: List[int]) -> bool:
        """Fast wrapper expecting env-style action array; checks top-level legality."""
        action = self.action_array_to_dict(action_array)
        return self.is_legal_action(action)

    def is_legal_action(self, action: Dict[str, int]) -> bool:
        """Check full legality of action dict (type + parameters) given current state."""
        a_type = action["type"]

        # Draft must be handled specially
        if self.in_draft_phase:
            return a_type == ACTION_DRAFT and (action["pos"] % 2) in (0, 1)

        player = self.players[self.current_player_idx]

        # must_develop restriction
        if self.must_develop and a_type != ACTION_DEVELOP:
            return False

        if a_type == ACTION_DEVELOP:
            # pos is 0..9; deck param is index of deck to draw from (we derive deck from pos in env logic)
            pos = action["pos"]
            deck_idx = pos % NUM_DECKS  # env uses mod mapping; we accept same pattern
            # deck must exist and not be empty to make a meaningful develop move; still allow action if deck empty? env refused draw
            return 0 <= pos < (LINE_SIZE + HAND_SIZE) and 0 <= deck_idx < NUM_DECKS

        if a_type == ACTION_SWAP:
            # player must have emissary and there must be a free swap spot
            if player.emissaries <= 0 or 0 not in self.available_swaps:
                return False
            st = action["swap_type"]
            if st not in (0, 1, 2, 3):  # hand, line, between, river
                return False
            # for hand/line swaps pos1 and pos2 should be in 0..4 and not equal for hand/line
            if st in (0, 1):
                p1, p2 = action["pos1"], action["pos2"]
                return 0 <= p1 < HAND_SIZE and 0 <= p2 < HAND_SIZE and p1 != p2
            if st == 2:
                p1 = action["pos1"]
                return 0 <= p1 < LINE_SIZE
            if st == 3:
                d1, d2 = action["pos1"], action["pos2"]
                return 0 <= d1 < NUM_DECKS and 0 <= d2 < NUM_DECKS and d1 != d2

        if a_type == ACTION_DISCARD:
            if player.emissaries <= 0 or 0 not in self.available_discards:
                return False
            d1, d2 = action["deck1"], action["deck2"]
            # allow discarding equal indices? env required different; enforce different
            return 0 <= d1 < NUM_DECKS and 0 <= d2 < NUM_DECKS and d1 != d2

        if a_type == ACTION_RECALL:
            # allowed only if player doesn't already have max (1 if decree, else 2)
            max_emiss = 1 if player.decree_used else INITIAL_EMISSARIES
            return player.emissaries < max_emiss

        if a_type == ACTION_DECREE:
            # only allowed if emissary available and neither player used decree
            if player.emissaries <= 0:
                return False
            if self.players[0].decree_used or self.players[1].decree_used:
                return False
            pos = action["pos"]
            return 0 <= pos < (LINE_SIZE + HAND_SIZE)

        if a_type == ACTION_END_GAME:
            return self.ending_available

        return False

    # ----- Action application -----
    def apply_action_array(self, action_array: List[int]) -> Tuple[np.ndarray, float, bool, bool, Dict[str, Any]]:
        """Apply env-style action array and return same tuple as env.step: (obs, reward, terminated, truncated, info)."""
        action = self.action_array_to_dict(action_array)
        return self.apply_action(action)

    def apply_action(self, action: Dict[str, int]) -> Tuple[np.ndarray, float, bool, bool, Dict[str, Any]]:
        """Apply an action (dict form). Returns (obs, reward, terminated, truncated, info).
        
        RULES.md Section 4: Turn Structure
        - ACTION_DEVELOP: May set optional_emissary_available (Option A) or clear must_develop (Option B)
        - ACTION_SWAP/DISCARD: May set must_develop (Option B) or clear optional_emissary_available (Option A)
        
        RULES.md Section 5: Actions
        - ACTION_DEVELOP: Replace card at position with card from River deck (Section 5.1)
        - ACTION_SWAP: 4 swap types - hand, line, between, river (Section 5.2)
        - ACTION_DISCARD: Remove top cards from 2 River decks (Section 5.2)
        - ACTION_RECALL: Restore emissaries and clear markers (Section 5.3)
        - ACTION_DECREE: Swap cards with opponent, lock emissary (Section 5.4)
        - ACTION_END_GAME: Set flag to end after opponent's turn (Section 7)
        
        RULES.md Section 6: Emissary System
        - Swap/Discard actions place markers in shared spots
        - Recall clears player's markers from all spots
        - Decree permanently locks one emissary
        
        RULES.md Section 7: Game End
        - ending_available set when 1+ decks empty
        - Auto-end when 2+ decks empty (after P1's turn, P2 gets final turn)
        - Declare end gives opponent one final turn
        
        Mirrors the logic in naishi_env.step and keeps state updates consistent.
        """
        reward = 0.0
        turn_ends = False
        terminated = False

        # Draft phase
        if self.in_draft_phase:
            if action["type"] != ACTION_DRAFT:
                # illegal during draft; calling code should avoid but mirror env behavior returning negative reward
                reward = -0.1
                return self.get_observation(), reward, False, False, self.get_info()
            # record draft choice for current player
            choice = action["pos"] % 2
            if self.current_player_idx == 0:
                p0_choice = choice
                # if we're simulating an opponent policy, you'd normally call it; GameState only supports both choices provided externally
                # For API convenience, if both choices provided in single call we can accept passing p1 in action dict (not standard)
                # For now, if current player is 0 we set index to 1 so next call by external controller should provide opponent choice.
                # However env implemented automatic opponent policy; for GameState integration, caller should:
                # - call apply_action for player0 draft (which flips current_player_idx to 1) and then call again with opponent's choice
                self.current_player_idx = 1
                # keep draft choice in temp field; caller must call complete draft with both choices or we can store p0 choice.
                self._pending_draft_choice_p0 = p0_choice
                # DO NOT finalize draft until both choices present
                return self.get_observation(), reward, False, False, self.get_info()
            else:
                # current_player_idx == 1: accept the choice and complete draft
                p1_choice = choice
                # p0_choice should be stored
                p0_choice = getattr(self, "_pending_draft_choice_p0", r.randint(0, 1))
                self._complete_draft(p0_choice, p1_choice)
                # reset current player back to player 0 for main game
                self.current_player_idx = 0
                # continue the game flow (no turn advancement here; env just returned observation)
                return self.get_observation(), reward, False, False, self.get_info()

        # --- Main phase ---
        player = self.players[self.current_player_idx]

        a_type = action["type"]
        
        # Track the action type for turn state management
        self.last_action_type = a_type

        if self.must_develop and a_type != ACTION_DEVELOP:
            reward = -0.1
            turn_ends = True

        elif a_type == ACTION_DEVELOP:
            # RULES.md Section 5.1: Develop Territory
            # Replace card at position with top card from corresponding River deck
            # Position mapping: 0-4 (Line) → Deck 0-4, 5-9 (Hand) → Deck 0-4 (pos % 5)
            pos = action["pos"]
            deck_idx = pos % NUM_DECKS
            # if deck available -> draw and replace
            if not self.river.is_empty(deck_idx):
                location = 'line' if pos < LINE_SIZE else 'hand'
                pos_in_loc = pos % LINE_SIZE
                # draw may raise IndexError; caller should catch if they pass invalid deck
                card = self.river.draw_card(deck_idx)
                player.replace_card(location, pos_in_loc, card)
            
            # RULES.md Section 4: Check turn context for optional emissary
            if self.must_develop:
                # This was a required develop after emissary (Option B)
                # Turn ends, no optional emissary offered
                turn_ends = True
                self.must_develop = False
            else:
                # This was a standalone develop (Option A)
                # Check if optional emissary is available
                if self._can_use_optional_emissary():
                    self.optional_emissary_available = True
                    turn_ends = False  # Don't end turn yet, allow optional emissary
                else:
                    turn_ends = True  # No optional emissary available, end turn

        elif a_type == ACTION_SWAP:
            # RULES.md Section 5.2: Emissary Actions - Swap Cards
            # 4 swap types: 0=hand, 1=line, 2=between hand/line, 3=river
            # RULES.md Section 6: Emissary System - Uses 1 emissary and 1 of 3 shared swap spots
            if player.emissaries > 0 and 0 in self.available_swaps:
                player.use_emissary()
                st = action["swap_type"]
                p1, p2 = action["pos1"], action["pos2"]
                if st == 0:
                    # Swap type 0: Swap 2 cards in Hand
                    player.swap_in_hand(p1, p2)
                elif st == 1:
                    # Swap type 1: Swap 2 cards in Line
                    player.swap_in_line(p1, p2)
                elif st == 2:
                    # Swap type 2: Swap between Line and Hand at same position
                    player.swap_between_line_and_hand(p1)
                elif st == 3:
                    # Swap type 3: Swap top cards of 2 River decks
                    if (0 <= p1 < NUM_DECKS) and (0 <= p2 < NUM_DECKS) and p1 != p2:
                        if (not self.river.is_empty(p1)) and (not self.river.is_empty(p2)):
                            self.river.swap_top_cards(p1, p2)
                # RULES.md Section 6: Place marker in one of 3 shared swap spots
                for i, spot in enumerate(self.available_swaps):
                    if spot == 0:
                        self.available_swaps[i] = self.current_player_idx + 1
                        break
                
                # RULES.md Section 4: Handle turn context
                if self.optional_emissary_available:
                    # This was optional emissary after develop (Option A) - clear flag and end turn
                    self.optional_emissary_available = False
                    turn_ends = True
                else:
                    # This was emissary-first (Option B) - must develop next
                    self.must_develop = True
                    turn_ends = False
            else:
                # illegal or no emissary/spot -> penalize
                reward = -0.1
                turn_ends = True

        elif a_type == ACTION_DISCARD:
            # RULES.md Section 5.2: Emissary Actions - Discard River Cards
            # Remove top cards from 2 different River decks
            # RULES.md Section 6: Emissary System - Uses 1 emissary and 1 of 2 shared discard spots
            if player.emissaries > 0 and 0 in self.available_discards:
                player.use_emissary()
                d1, d2 = action["deck1"], action["deck2"]
                if d1 != d2:
                    self.river.discard_top_cards(d1, d2)
                # RULES.md Section 6: Place marker in one of 2 shared discard spots
                for i, spot in enumerate(self.available_discards):
                    if spot == 0:
                        self.available_discards[i] = self.current_player_idx + 1
                        break
                
                # RULES.md Section 4: Handle turn context
                if self.optional_emissary_available:
                    # This was optional emissary after develop (Option A) - clear flag and end turn
                    self.optional_emissary_available = False
                    turn_ends = True
                else:
                    # This was emissary-first (Option B) - must develop next
                    self.must_develop = True
                    turn_ends = False
            else:
                reward = -0.1
                turn_ends = True

        elif a_type == ACTION_RECALL:
            # RULES.md Section 5.3: Recall Emissaries
            # Restore emissaries to max (2 normally, 1 if decree used)
            # RULES.md Section 6: Clear player's markers from all swap and discard spots
            max_em = 1 if player.decree_used else INITIAL_EMISSARIES
            if player.emissaries < max_em:
                # Clear all spots used by this player (free them for reuse)
                for i, spot in enumerate(self.available_swaps):
                    if spot == self.current_player_idx + 1:
                        self.available_swaps[i] = 0
                for i, spot in enumerate(self.available_discards):
                    if spot == self.current_player_idx + 1:
                        self.available_discards[i] = 0
                player.recall_emissaries(player.decree_used)
            else:
                reward = -0.1
            turn_ends = True

        elif a_type == ACTION_DECREE:
            # RULES.md Section 5.4: Decree swaps cards at same position and permanently locks one emissary
            if player.emissaries > 0 and not (self.players[0].decree_used or self.players[1].decree_used):
                player.use_emissary()
                # Decree permanently locks one emissary for the player who uses it
                player.decree_used = True
                swap_pos = action["pos"]
                opponent = self.players[1 - self.current_player_idx]
                location = 'line' if swap_pos < LINE_SIZE else 'hand'
                pos_in_loc = swap_pos % LINE_SIZE
                if location == 'line':
                    player.line[pos_in_loc], opponent.line[pos_in_loc] = opponent.line[pos_in_loc], player.line[pos_in_loc]
                else:
                    player.hand[pos_in_loc], opponent.hand[pos_in_loc] = opponent.hand[pos_in_loc], player.hand[pos_in_loc]
            else:
                # Decree already used by either player or no emissaries available
                reward = -0.1
            turn_ends = True

        elif a_type == ACTION_END_GAME:
            # RULES.md Section 7: Declare End of Game
            # Only available when 1+ decks empty
            # Opponent gets one final turn before game ends
            if self.ending_available:
                # Set flag to end after opponent's next turn
                # Use a separate flag to track that this was just set this turn
                self.end_next_turn = True
                self._end_declared_this_turn = True
            else:
                reward = -0.1
            turn_ends = True

        else:
            # unknown -> end turn (defensive)
            turn_ends = True

        # RULES.md Section 7: Update ending availability AFTER action is applied
        # This ensures players can declare end immediately when condition is met
        if not self.ending_available and self.river.count_empty_decks() >= 1:
            self.ending_available = True

        # If turn ends and game not terminated, check ending conditions and switch player
        if turn_ends and not terminated:
            # RULES.md Section 7: Check if previous player set end_next_turn flag
            # Only check if it wasn't just set this turn (by declare end)
            if self.end_next_turn and not getattr(self, '_end_declared_this_turn', False):
                terminated = True
                self.end_next_turn = False
            
            # RULES.md Section 7: Check auto-end condition (2+ decks empty) BEFORE switching
            # This ensures we check after the complete turn (including optional emissary)
            # Ensure both players get equal turns:
            # - If P2 just completed their turn and 2+ decks empty: end immediately
            # - If P1 just completed their turn and 2+ decks empty: P2 gets one final turn
            if not terminated and self.river.count_empty_decks() >= 2:
                if self.current_player_idx == 1:
                    # P2 just completed their turn, 2+ decks empty → end immediately
                    terminated = True
                else:
                    # P1 just completed their turn, 2+ decks empty → P2 gets final turn
                    self.end_next_turn = True
            
            # Clear the flag for next turn
            self._end_declared_this_turn = False
            
            # Only switch players if game didn't just terminate
            if not terminated:
                self.current_player_idx = 1 - self.current_player_idx
                self.turn_count += 1
                self.clear_turn_state()  # Clear turn state when switching players

                # note: environment uses its own opponent policy loop; GameState doesn't auto-run policies.
                # Caller (env) should call opponent policy and pass actions through GameState.apply_actionArray again.

        # Calculate final reward if game just terminated (moved here to execute AFTER terminated flag is set)
        if terminated and reward == 0.0:  # Only calculate if not already set
            scores = self.get_scores()
            p0_score = scores[0]['Total']
            p1_score = scores[1]['Total']
            
            # Reward from perspective of player who just acted
            if p0_score > p1_score:
                # Player 0 wins
                reward = 1.0 if self.current_player_idx == 0 else -1.0
            elif p1_score > p0_score:
                # Player 1 wins
                reward = 1.0 if self.current_player_idx == 1 else -1.0
            else:
                # Draw - check tiebreaker (most unique cards excluding Mountain and Ninja)
                p0_cards = self.players[0].get_all_cards()
                p1_cards = self.players[1].get_all_cards()
                p0_unique = len(set(c for c in p0_cards if c not in ['Mountain', 'Ninja']))
                p1_unique = len(set(c for c in p1_cards if c not in ['Mountain', 'Ninja']))
                
                if p0_unique > p1_unique:
                    reward = 1.0 if self.current_player_idx == 0 else -1.0
                elif p1_unique > p0_unique:
                    reward = 1.0 if self.current_player_idx == 1 else -1.0
                else:
                    reward = 0.0  # True draw

        # truncate condition (for external callers)
        truncated = self.turn_count > self.max_turns_truncate and not terminated
        if truncated and not terminated:
            # Scoring will be evaluated by caller; here we set terminated False but truncated True.
            pass

        obs = self.get_observation()
        info = self.get_info()

        return obs, reward, terminated, truncated, info

    # ----- Observation / Info (helpers for env compatibility) -----
    def get_observation(self) -> np.ndarray:
        """Return observation array matching NaishiEnv._get_obs layout.

        Layout used in the project (36 elements total):
        - Draft phase (31 + 5 padding):
            [line(5) all Mountains, current player's draft hand (2), padding (3),
             river tops (5), river counts (5), current.emissaries, opponent.emissaries, 
             current.decree_used, opponent.decree_used, turn_norm (turn_count/50 clipped), 
             flags: must_develop, ending_available, swap_available, discard_available, 
             in_draft_phase, optional_emissary_available, padding (5)]
        - Main game (36):
            [current.line(5), current.hand(5), opponent.line(5),
             river_tops(5), river_counts(5), current.emissaries, opponent.emissaries,
             current.decree_used, opponent.decree_used, turn_norm, must_develop, ending_available,
             swap_available, discard_available, in_draft_phase, optional_emissary_available]
        
        Note: Opponent hand is NEVER included (hidden information).
        """
        encode = lambda card: CARD_TO_INT.get(card, CARD_TO_INT['Empty'])
        if self.in_draft_phase:
            current = self.players[self.current_player_idx]
            opponent = self.players[1 - self.current_player_idx]
            # current player's line (Mountains)
            obs = []
            obs.extend([encode('Mountain')] * LINE_SIZE)
            # current draft hand 2 cards padded to 5
            ch = list(self.draft_hands[self.current_player_idx])
            while len(ch) < 2:
                ch.append('Empty')
            obs.extend([encode(ch[0]), encode(ch[1])])
            obs.extend([encode('Empty')] * 3)
            # opponent draft hand is hidden - not included in observation
            # river tops (5)
            obs.extend([encode(self.river_tops_at_draft[i] if i < len(self.river_tops_at_draft) else 'Empty') for i in range(NUM_DECKS)])
            # river counts
            obs.extend(self.river.cards_left())
            # emissaries: current, opponent
            obs.append(self.players[self.current_player_idx].emissaries)
            obs.append(self.players[1 - self.current_player_idx].emissaries)
            # decree flags
            obs.append(int(self.players[self.current_player_idx].decree_used))
            obs.append(int(self.players[1 - self.current_player_idx].decree_used))
            # normalized turn
            obs.append(min(self.turn_count / 50.0, 1.0))
            # flags: must_develop (False during draft), ending_available, swap available, discard available, in_draft_phase
            obs.append(0)  # must_develop false
            obs.append(int(self.ending_available))
            obs.append(int(0 in self.available_swaps))
            obs.append(int(0 in self.available_discards))
            obs.append(1)  # in_draft_phase
            obs.append(0)  # optional_emissary_available false during draft
            # Pad to match main game observation size (36 elements)
            # Draft is 31, main game is 36, so add 5 padding zeros
            obs.extend([0] * 5)
            return np.array(obs, dtype=np.float32)

        else:
            current = self.players[self.current_player_idx]
            opponent = self.players[1 - self.current_player_idx]

            obs = []
            obs.extend([CARD_TO_INT.get(c, CARD_TO_INT['Empty']) for c in current.line])
            obs.extend([CARD_TO_INT.get(c, CARD_TO_INT['Empty']) for c in current.hand])
            obs.extend([CARD_TO_INT.get(c, CARD_TO_INT['Empty']) for c in opponent.line])
            # opponent hand is hidden - not included in observation
            obs.extend([CARD_TO_INT.get(self.river.get_top_card(i) or 'Empty', CARD_TO_INT['Empty']) for i in range(NUM_DECKS)])
            obs.extend(self.river.cards_left())
            obs.append(current.emissaries)
            obs.append(opponent.emissaries)
            obs.append(int(current.decree_used))
            obs.append(int(opponent.decree_used))
            obs.append(min(self.turn_count / 50.0, 1.0))
            obs.append(int(self.must_develop))
            obs.append(int(self.ending_available))
            obs.append(int(0 in self.available_swaps))
            obs.append(int(0 in self.available_discards))
            obs.append(0)  # in_draft_phase false
            obs.append(int(self.optional_emissary_available))  # optional emissary flag
            return np.array(obs, dtype=np.float32)

    def get_info(self) -> Dict[str, Any]:
        """Return a small info dict similar to env._get_info"""
        return {"turn": self.turn_count, "action_mask": None}  # action_mask built by env wrapper

    # ----- Utility / scoring -----
    def get_scores(self, get_ninja_choice_func=None) -> List[Dict[str, int]]:
        """Return score breakdown for both players. If ninjas present, caller must provide choice function used by Scorer.handle_ninjas."""
        res = []
        for p in self.players:
            cards = p.get_all_cards()
            # if ninjas exist, require a function to pick copies; fall back to random (original env used random)
            if 'Ninja' in cards and get_ninja_choice_func is not None:
                resolved = Scorer.handle_ninjas(cards, CHARACTERS := [], get_ninja_choice_func=get_ninja_choice_func)
            else:
                resolved = cards.copy()
            res.append(Scorer.calculate_score(resolved))
        return res

    def __repr__(self):
        return f"<GameState turn={self.turn_count} cur={self.current_player_idx} swaps={self.available_swaps} discs={self.available_discards} river={self.river.cards_left()}>"
