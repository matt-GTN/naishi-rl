# naishi_core/player.py

from dataclasses import dataclass, field
from typing import List
from .constants import LINE_SIZE, HAND_SIZE, PLAYER_COLORS, INITIAL_EMISSARIES

@dataclass
class Player:
    """Represents a single player's state"""
    index: int  # 0 or 1
    hand: List[str] = field(default_factory=list)
    line: List[str] = field(default_factory=list)
    emissaries: int = INITIAL_EMISSARIES
    decree_used: bool = False
    
    def get_all_cards(self) -> List[str]:
        """Returns combined line + hand (10 cards total)"""
        return self.line + self.hand
    
    def set_all_cards(self, cards: List[str]):
        """Sets line and hand from a list of 10 cards"""
        assert len(cards) == LINE_SIZE + HAND_SIZE, "Must provide exactly 10 cards"
        self.line = cards[:LINE_SIZE]
        self.hand = cards[LINE_SIZE:]
    
    @property
    def color(self) -> str:
        """Display color for this player"""
        return PLAYER_COLORS[self.index]
    
    def swap_in_hand(self, pos1: int, pos2: int):
        """Swap two cards in hand"""
        self.hand[pos1], self.hand[pos2] = self.hand[pos2], self.hand[pos1]
    
    def swap_in_line(self, pos1: int, pos2: int):
        """Swap two cards in line"""
        self.line[pos1], self.line[pos2] = self.line[pos2], self.line[pos1]
    
    def swap_between_line_and_hand(self, position: int):
        """Swap card at same position between line and hand"""
        self.line[position], self.hand[position] = self.hand[position], self.line[position]
    
    def replace_card(self, location: str, position: int, new_card: str):
        """Replace a card at a specific location"""
        if location == 'hand':
            self.hand[position] = new_card
        elif location == 'line':
            self.line[position] = new_card
        else:
            raise ValueError(f"Invalid location: {location}")
    
    def use_emissary(self):
        """Decrease emissary count"""
        if self.emissaries > 0:
            self.emissaries -= 1
        else:
            raise ValueError("No emissaries available")
    
    def recall_emissaries(self, locked_by_decree: bool) -> int:
        """Recall all available emissaries, return number recalled"""
        if locked_by_decree:
            max_emissaries = 1
        else:
            max_emissaries = INITIAL_EMISSARIES
        
        recalled = max_emissaries - self.emissaries
        self.emissaries = max_emissaries
        return recalled
    
    def __repr__(self):
        return f"Player{self.index + 1}(emissaries={self.emissaries}, decree={self.decree_used})"