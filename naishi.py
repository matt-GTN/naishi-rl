from typing import List, Dict
from dataclasses import dataclass, field
from banner import print_banner
import random as r

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
        
game_list = total_cards_list
r.shuffle(game_list)

# Decks
decks = []
for i in range(5):
    slicer_start = i * 6
    slicer_end = (i + 1) * 6 
    decks.append(game_list[slicer_start:slicer_end])

# Hands
player_hands = []
player_hands.append(game_list[-2:])
player_hands.append(game_list[-4:-2])
for hand in range(len(player_hands)):
    for i in range(3):
        player_hands[hand].append('Mountain')
r.shuffle(player_hands[0])
r.shuffle(player_hands[1])

# Lines
base_line = ['Mountain', 'Mountain', 'Mountain', 'Mountain', 'Mountain']
player_lines = []
for i in range(2):
    player_lines.append(base_line)

# Game State
@dataclass
class GameState:
    cards: List[str] = field(default_factory=lambda:cards)
    cards_count: List[int] = field(default_factory=lambda:cards_count)
    total_cards_list: List[str] = field(default_factory=lambda:total_cards_list)
    decks: List[List[str]] = field(default_factory=lambda:decks)
    player_hands: List[List[str]] = field(default_factory=lambda:player_hands)
    player_lines: List[List[str]] = field(default_factory=lambda:player_lines)
    
    def show(self):
        print_banner()
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