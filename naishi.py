from typing import List, Dict
from dataclasses import dataclass, field
from banner import print_banner
import random as r
from termcolor import colored
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
    cards_left: List[int] = field(default_factory=list)
    ending_available: bool = False

### Initialisation ###
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
        cards_left = [6, 6, 6, 6, 6]
        total_cards_list = []

        for card, count in zip(cards, cards_count):
            for i in range(count):
                total_cards_list.append(card)
        
        state.cards = cards
        state.card_count = cards_count
        state.cards_left = cards_left
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
            player_lines.append(base_line.copy( ))
        
        state.player_lines = player_lines
        
        # Emissaries
        state.emissaries = [2, 2]
        
        return state

### Functions ###
    # Printing the Game State to the console
    def show(self):
        # River
        print("\n")
        print(colored("=" * 18, "blue"))
        print(colored("|| River        ||", "blue"))
        print(colored("=" * 78, "blue"))
        row = "|| " + " | ".join(f"{self.decks[i][0]:<12}" if self.cards_left[i] > 0 else (" "*12) for i in range(5)) + " ||"
        print(colored(row, "blue"))
        print(colored("="*78, "blue"))
        row = "|| " + " | ".join(f"{str(self.cards_left[i])} left      " for i in range(5)) + " ||" 
        print(colored(row, "blue"))
        print(colored("="*78, "blue"))
        print("\n")
        # Player 1
        print(colored("=" * 18, "magenta"))
        print(colored("|| Player 1     ||", "magenta"))
        print(colored("=" * 18, "magenta"))
        print(colored("|| Line         ||", "magenta"))
        print(colored("=" * 78, "magenta"))
        line_row = "|| " + " | ".join(f"{card:<12}" for card in self.player_lines[0]) + " ||"
        print(colored(line_row, "magenta"))
        print(colored("=" * 78, "magenta"))
        print(colored("|| Hand         ||", "magenta"))
        print(colored("=" * 78, "magenta"))
        hand_row = "|| " + " | ".join(f"{card:<12}" for card in self.player_hands[0]) + " ||"
        print(colored(hand_row, "magenta"))
        print(colored("=" * 78, "magenta"))
        print("\n")
        # Player 2
        print(colored("=" * 18, "yellow"))
        print(colored("|| Player 2     ||", "yellow"))
        print(colored("=" * 18, "yellow"))
        print(colored("|| Line         ||", "yellow"))
        print(colored("=" * 78, "yellow"))
        line_row = "|| " + " | ".join(f"{card:<12}" for card in self.player_lines[1]) + " ||"
        print(colored(line_row, "yellow"))
        print(colored("=" * 78, "yellow"))
        print(colored("|| Hand         ||", "yellow"))
        print(colored("=" * 78, "yellow"))
        hand_row = "|| " + " | ".join(f"{card:<12}" for card in self.player_hands[1]) + " ||"
        print(colored(hand_row, "yellow"))
        print(colored("=" * 78, "yellow"))
        print("\n")

    # Discarding for Developing
    def choose_discard(self, player_index: int) -> int:
        """Display hand + line with numbers 1-10 for discarding and returns the choice"""
    
        hand = self.player_hands[player_index]
        line = self.player_lines[player_index]
        current_player = self.current_player + 1
        
        # River
        print("\n")
        print(colored("=" * 18, "blue"))
        print(colored("|| River        ||", "blue"))
        print(colored("=" * 78, "blue"))
        row = "|| " + " | ".join(f"{self.decks[i][0]:<12}" if self.cards_left[i] > 0 else (" "*12) for i in range(5)) + " ||"
        print(colored(row, "blue"))
        print(colored("="*78, "blue"))
        row = "|| " + " | ".join(f"{str(self.cards_left[i])} left      " for i in range(5)) + " ||" 
        print(colored(row, "blue"))
        print(colored("="*78, "blue"))
        print("\n")
        
        if current_player == 1:
            # Player 1
            print(colored("=" * 18, "magenta"))
            print(colored(f"|| Player {current_player}     ||", "magenta"))
            print(colored("=" * 18, "magenta"))
            print(colored("|| Line         ||", "magenta"))
            print(colored("=" * 88, "magenta"))
            line_row = "|| " + " | ".join(f"{str(i)}.{card:<12}" for i, card in enumerate(self.player_lines[0])) + " ||"
            print(colored(line_row, "magenta"))
            print(colored("=" * 88, "magenta"))
            print(colored("|| Hand         ||", "magenta"))
            print(colored("=" * 88, "magenta"))
            hand_row = "|| " + " | ".join(f"{str(i + 5)}.{card:<12}" for i, card in enumerate(self.player_hands[0])) + " ||"
            print(colored(hand_row, "magenta"))
            print(colored("=" * 88, "magenta"))
            print("\n")
        
        else:
            # Player 2
            print(colored("=" * 18, "yellow"))
            print(colored(f"|| Player {current_player}     ||", "yellow"))
            print(colored("=" * 18, "yellow"))
            print(colored("|| Line         ||", "yellow"))
            print(colored("=" * 88, "yellow"))
            line_row = "|| " + " | ".join(f"{str(i)}.{card:<12}" for i, card in enumerate(self.player_lines[1])) + " ||"
            print(colored(line_row, "yellow"))
            print(colored("=" * 88, "yellow"))
            print(colored("|| Hand         ||", "yellow"))
            print(colored("=" * 88, "yellow"))
            hand_row = "|| " + " | ".join(f"{str(i + 5)}.{card:<12}" for i, card in enumerate(self.player_hands[1])) + " ||"
            print(colored(hand_row, "yellow"))
            print(colored("=" * 88, "yellow"))
            print("\n")
    
        # Ask for choice
        choice = get_choice(
            f"Player {player_index + 1}, which card do you want to discard? (0-{len(line)+len(hand) - 1})\n",
            list(range(0, len(line)+len(hand)))
        )
    
        # Return a tuple: (source, index) -> 'line' or 'hand', index in that source
        if choice <= len(line):
            return ('line', choice)
        else:
            return ('hand', choice - len(line))  # careful with indexing


    # Playing a turn 
    def play(self):
        current_player = self.current_player
        emissaries = self.emissaries[current_player]
        options = [
            'Emissary',
            'Developing',
            'Decree',
            'Ending']
        
        if not self.ending_available:
            choice = get_choice(
                f'Player {current_player + 1}, what do you want to do ?\n\n1. Develop your Territory\n2. Send an Emissary\n3. Impose an Imperial Decree\n\n',
                [1, 2, 3]
            )
        else:
           choice = get_choice(
                f'Player {current_player + 1}, what do you want to do ?\n\n1. Develop your Territory\n2. Send an Emissary\n3. Impose an Imperial Decree\n4. Declare the end of the game\n\n',
                [1, 2, 3, 4]
            ) 
        
        if choice == 1:
            while True:
                try:
                    source, index = self.choose_discard(current_player)
                    if source == 'hand':
                        self.player_hands[current_player][index] = self.decks[index][0]
                        self.decks[index].pop(0)
                        self.cards_left[index] -= 1
                        print(f"\nPlayer {current_player + 1} added {self.player_hands[current_player][index]} to the {index+1} position in their {source}.\n")
                    else:
                        self.player_lines[current_player][index] = self.decks[index][0]
                        self.decks[index].pop(0)
                        self.cards_left[index] -= 1
                        print(f"\nPlayer {current_player + 1} added {self.player_lines[current_player][index]} to the {index+1} position in their {source}.\n")
                    break
                except IndexError:
                    print('This deck is empty, please choose another one.')
        
        if choice == 4:
            return True
        
        # Showing Ending
        if 0 in self.cards_left:
            self.ending_available = True
        
        self.current_player = 1 - current_player

        
        
        
1