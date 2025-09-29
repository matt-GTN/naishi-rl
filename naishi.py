from typing import List, Dict
from dataclasses import dataclass, field
from banner import print_banner
import random as r

# Game State
@dataclass
class GameState:
    cards: List[str] = field(default_factory=list)
    cards_count: List[int] = field(default_factory=list)
    total_cards_list: List[str] = field(default_factory=list)
    decks: List[List[str]] = field(default_factory=list)
    player_hands: List[List[str]] = field(default_factory=list)
    player_lines: List[List[str]] = field(default_factory=list)
    current_player: int = 0
    
    @staticmethod
    def create_initial_state(seed=None):
        print("\n")
        print_banner()
        print("\n\n")
        """Factory method - replaces global initialization"""
        if seed is not None:
            r.seed(seed)
           
        state = GameState()
        
        # Cards
        cards = ["Naishi", 
                "Councellor", 
                "Sentinel", 
                "Fort", 
                "Monk", 
                "Torii",
                "Knight",
                "Banner",
                "Rice fields",
                "Ronin",
                "Ninja"]

        cards_count = [2, 4, 4, 4, 3, 4, 2, 2, 5, 2, 2]
        total_cards_list = []

        for card, count in zip(cards, cards_count):
            for i in range(count):
                total_cards_list.append(card)
        
        state.cards = cards
        state.card_count = cards_count
        state.total_cards_list = total_cards_list

        # Decks
        game_list = total_cards_list
        r.shuffle(game_list)
        decks = []
        for i in range(5):
            slicer_start = i * 6
            slicer_end = (i + 1) * 6 
            decks.append(game_list[slicer_start:slicer_end])
        
        state.decks = decks

        # Hands
        player_hands = []
        player_hands.append(game_list[-2:])
        player_hands.append(game_list[-4:-2])
        
        # Drafting
        def get_choice(prompt, options):
            while True:
                try:
                    choice = int(input(prompt))
                    if choice in options:
                        return choice
                    else:
                        print(f"Please enter only {options}.")
                except ValueError:
                    print("Please enter a number.")

        p1_choice = get_choice(
            f'Player 1 - What card do you want to give to your opponent ? {player_hands[0][0]} or {player_hands[0][1]} ? (1/2) ',
            [1, 2]
        )

        p2_choice = get_choice(
            f'Player 2 - What card do you want to give to your opponent ? {player_hands[1][0]} or {player_hands[1][1]} ? (1/2) ',
            [1, 2]
        )
        
        if p1_choice == 1:
            if p2_choice == 1:
                player_hands[0][0], player_hands[1][0] = player_hands[1][0], player_hands[0][0]
            else:
                player_hands[0][0], player_hands[1][1] = player_hands[1][1], player_hands[0][0]
        else:
            if p2_choice == 1:
                player_hands[0][1], player_hands[1][0] = player_hands[1][0], player_hands[0][1]
            else:
                player_hands[0][1], player_hands[1][1] = player_hands[1][1], player_hands[0][1]
            
                  
            
        
        for hand in range(len(player_hands)):
            for i in range(3):
                player_hands[hand].append('Mountain')
        
        r.shuffle(player_hands[0])
        r.shuffle(player_hands[1])
        
        state.player_hands = player_hands

        # Lines
        base_line = ['Mountain', 'Mountain', 'Mountain', 'Mountain', 'Mountain']
        player_lines = []
        
        for i in range(2):
            player_lines.append(base_line)
        
        state.player_lines = player_lines
        
        return state
    
    def show(self):
        # Decks
        print("\n")
        print("="*78)
        print("|| Deck 1       | Deck 2       | Deck 3       | Deck 4       | Deck 5       ||")
        print("="*78)
        
        for i in range(len(self.decks[0])):
            if i != 0:
                print("-"*78)
            row = "|| " + " | ".join(f"{self.decks[j][i]:<12}" for j in range(5)) + " ||"
            print(row)
        
        print("="*78)
        print("\n")
        
        # Player 1
        print("="* 18)
        print("|| Player 1     ||")
        print("="* 18)
        print("\n")
        print("="* 18)
        print("|| Line         ||")
        print("="* 78)
        line_row = "|| " + " | ".join(f"{card:<12}" for card in self.player_lines[0]) + " ||"
        print(line_row)
        print("="* 78)
        print("\n")
        print("="* 18)
        print("|| Hand         ||")
        print("="* 78)
        hand_row = "|| " + " | ".join(f"{card:<12}" for card in self.player_hands[0]) + " ||"
        print(hand_row)
        print("="* 78)
        print("\n")
        
        
        # Player 2
        print("="* 18)
        print("|| Player 2     ||")
        print("="* 18)
        print("\n")
        print("="* 18)
        print("|| Line         ||")
        print("="* 78)
        line_row = "|| " + " | ".join(f"{card:<12}" for card in self.player_lines[1]) + " ||"
        print(line_row)
        print("="* 78)
        print("\n")
        print("="* 18)
        print("|| Hand         ||")
        print("="* 78)
        hand_row = "|| " + " | ".join(f"{card:<12}" for card in self.player_hands[1]) + " ||"
        print(hand_row)
        print("="* 78)
        print("\n")