from typing import List, Dict
from dataclasses import dataclass, field
from banner import print_banner
import random as r

# General functions
# Making a choice 
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


### Class definition ###
@dataclass
class GameState:
    cards: List[str] = field(default_factory=list)
    cards_count: List[int] = field(default_factory=list)
    total_cards_list: List[str] = field(default_factory=list)
    decks: List[List[str]] = field(default_factory=list)
    player_hands: List[List[str]] = field(default_factory=list)
    player_lines: List[List[str]] = field(default_factory=list)
    emissaries: List[int] = field(default_factory=list)
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
        
        p1_choice = get_choice(
            f'Player 1 - What card do you want to give to your opponent ? (1/2)\n\n1. {player_hands[0][0]}\n2. {player_hands[0][1]}\n\n',
            [1, 2]
        )

        p2_choice = get_choice(
            f'Player 2 - What card do you want to give to your opponent ? (1/2)\n\n1. {player_hands[1][0]}\n2. {player_hands[1][1]}\n\n',
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
        
        # Emissaries
        state.emissaries = [2, 2]
        
        return state

### Functions ###
    # Printing the Game State to the console
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

    # Discarding for Developing
    def choose_discard(self, player_index: int) -> int:
        """Display hand + line with numbers 1-10 for discarding and returns the choice"""
    
        hand = self.player_hands[player_index]
        line = self.player_lines[player_index]
    
        print("\n" + "="*18)
        print(f"|| Player {player_index + 1} ||")
        print("="*18)
    
        # Line table
        print("\n" + "="*18)
        print("|| Line         ||")
        print("="*78)
        number_row_line = "|| " + " | ".join(f"{i+1:<12}" for i in range(len(line))) + " ||"
        print(number_row_line)
        print("-"*78)
        card_row_line = "|| " + " | ".join(f"{card:<12}" for card in line) + " ||"
        print(card_row_line)
        print("="*78 + "\n")
    
        # Hand table
        print("="*18)
        print("|| Hand         ||")
        print("="*78)
        number_row_hand = "|| " + " | ".join(f"{i+1+len(line):<12}" for i in range(len(hand))) + " ||"
        print(number_row_hand)
        print("-"*78)
        card_row_hand = "|| " + " | ".join(f"{card:<12}" for card in hand) + " ||"
        print(card_row_hand)
        print("="*78 + "\n")
    
        # Ask for choice
        choice = get_choice(
            f"Player {player_index + 1}, which card do you want to discard? (1-{len(line)+len(hand)})\n",
            list(range(1, len(line)+len(hand)+1))
        )
    
        # Return a tuple: (source, index) -> 'line' or 'hand', index in that source
        if choice <= len(line):
            return ('line', choice - 1)
        else:
            return ('hand', choice - len(line) - 1)  # careful with indexing


    # Playing a turn 
    def play(self):
        current_player = self.current_player
        emissaries = self.emissaries[current_player]
        options = [
            'Emissary',
            'Developing',
            'Decree',
            'Ending']
        
        choice = get_choice(
            f'Player {current_player + 1}, what do you want to do ?\n\n1. Develop your Territory\n2.Send an Emissary\n3. Impose an Imperial Decree\n4.Declare the end of the game\n\n',
            [1, 2, 3, 4]
        )
        
        if choice == 1:
            source, index = self.choose_discard(current_player)
            if source == 'hand':
                self.player_hands[current_player][index] = self.decks[index][0]
                self.decks[index].pop(0)
                self.decks[index].append('')
                print(f"\nPlayer {current_player + 1} added {self.player_hands[current_player][index]} to the {index+1} position in their {source}.\n")
            else:
                self.player_lines[current_player][index] = self.decks[index][0]
                self.decks[index].pop(0)
                self.decks[index].append('')
                print(f"\nPlayer {current_player + 1} added {self.player_lines[current_player][index]} to the {index+1} position in their {source}.\n")
        if choice == 4:
            return True
        
        self.current_player = 1 - current_player

        
        
        







