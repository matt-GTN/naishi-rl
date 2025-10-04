# naishi_core/river.py

from dataclasses import dataclass, field
from typing import List, Optional
from .constants import NUM_DECKS


@dataclass
class River:
    """
    Manages the river (5 decks of cards).
    
    The river represents 5 piles of cards that players draw from.
    Each deck starts with 6 cards and gets depleted during the game.
    """
    decks: List[List[str]] = field(default_factory=list)
    
    def __post_init__(self):
        """Initialize empty decks if none provided"""
        if not self.decks:
            self.decks = [[] for _ in range(NUM_DECKS)]
    
    def cards_left(self) -> List[int]:
        """
        Returns number of cards remaining in each deck.
        
        Returns:
            List of 5 integers representing cards in each deck
        
        Example:
            >>> river.cards_left()
            [6, 5, 4, 3, 0]  # Deck 5 is empty
        """
        return [len(deck) for deck in self.decks]
    
    def get_top_card(self, deck_index: int) -> Optional[str]:
        """
        Get top card from a deck without removing it.
        
        Args:
            deck_index: Index of deck (0-4)
        
        Returns:
            Card name or None if deck is empty
        
        Example:
            >>> river.get_top_card(0)
            'Naishi'
        """
        if 0 <= deck_index < NUM_DECKS and self.decks[deck_index]:
            return self.decks[deck_index][0]
        return None
    
    def draw_card(self, deck_index: int) -> str:
        """
        Draw (remove and return) top card from a deck.
        
        Args:
            deck_index: Index of deck (0-4)
        
        Returns:
            The drawn card
        
        Raises:
            IndexError: If deck is empty or index invalid
        
        Example:
            >>> card = river.draw_card(2)
            >>> print(card)
            'Knight'
        """
        if 0 <= deck_index < NUM_DECKS and self.decks[deck_index]:
            return self.decks[deck_index].pop(0)
        raise IndexError(f"Deck {deck_index} is empty or invalid")
    
    def is_empty(self, deck_index: int) -> bool:
        """
        Check if a specific deck is empty.
        
        Args:
            deck_index: Index of deck (0-4)
        
        Returns:
            True if deck is empty
        """
        return len(self.decks[deck_index]) == 0
    
    def count_empty_decks(self) -> int:
        """
        Count how many decks are completely empty.
        
        Returns:
            Number of empty decks (0-5)
        
        Example:
            >>> river.count_empty_decks()
            2  # Two decks have been depleted
        """
        return sum(1 for deck in self.decks if not deck)
    
    def swap_top_cards(self, deck1: int, deck2: int):
        """
        Swap the top cards of two decks (emissary action).
        
        Args:
            deck1: Index of first deck
            deck2: Index of second deck
        
        Raises:
            IndexError: If either deck is empty
        
        Example:
            >>> river.swap_top_cards(0, 3)
            # Top card of deck 0 is now what was on deck 3, and vice versa
        """
        if not self.decks[deck1] or not self.decks[deck2]:
            raise IndexError("Cannot swap from empty deck")
        self.decks[deck1][0], self.decks[deck2][0] = \
            self.decks[deck2][0], self.decks[deck1][0]
    
    def discard_top_cards(self, deck1: int, deck2: int):
        """
        Discard top cards from two decks (emissary action).
        
        Args:
            deck1: Index of first deck
            deck2: Index of second deck
        
        Note:
            Silently skips empty decks rather than raising error
        
        Example:
            >>> river.discard_top_cards(1, 4)
            # Top cards from decks 1 and 4 are removed
        """
        if self.decks[deck1]:
            self.decks[deck1].pop(0)
        if self.decks[deck2]:
            self.decks[deck2].pop(0)
    
    def __repr__(self):
        """String representation showing cards remaining in each deck"""
        cards_left = self.cards_left()
        return f"River({cards_left})"