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

def check_adjacency(position, cards):
    adjacents = {}
    try:
        if position != 0 or position != 5:
            adjacents['left'] = {
                'card': cards[position - 1],
                'position': position - 1
            }
        if position != 4 or position != 9:
            adjacents['right'] = {
                'card': cards[position + 1],
                'position': position + 1
            }
    
        if position < 5:
            adjacents['down'] = {
                'card': cards[position + 5],
                'position': position + 5
            }
        if position > 4: 
            adjacents['up'] = {
                'card': cards[position - 5],
                'position': position - 5
            }
    except IndexError:
        pass
    
    return adjacents
    

### Class definition ###
@dataclass
class GameState:
    cards: List[str] = field(default_factory=list)
    characters: List[str] = field(default_factory=list)
    cards_count: List[int] = field(default_factory=list)
    total_cards_list: List[str] = field(default_factory=list)
    decks: List[List[str]] = field(default_factory=list)
    player_hands: List[List[str]] = field(default_factory=list)
    player_lines: List[List[str]] = field(default_factory=list)
    emissaries: List[int] = field(default_factory=list)
    current_player: int = 0
    available_swaps: List[int] = field(default_factory=list)
    available_discards: List[int] = field(default_factory=list)
    cards_left: List[int] = field(default_factory=list)
    error_message: str = ''
    game_message: str = ''
    ending_available: bool = False
    end_next_turn: bool = False
    decree_used: List[bool] = field(default_factory=list)

### Initialisation ###
    @staticmethod
    def create_initial_state(seed=None):
        print("\n")
        print_banner()
        print("\n\n")
        """Initialize the game state with base info"""
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
        
        characters = [
            "Naishi", 
            "Councellor", 
            "Sentinel",  
            "Monk", 
            "Knight",
            "Ronin",
        ]

        cards_count = [2, 4, 4, 4, 3, 4, 2, 2, 5, 2, 2]
        cards_left = [6, 6, 6, 6, 6]
        total_cards_list = []

        for card, count in zip(cards, cards_count):
            for i in range(count):
                total_cards_list.append(card)
        
        state.characters = characters
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
        
        # River printing for drafting
        print("\n")
        print(colored("=" * 18, "blue"))
        print(colored("|| River        ||", "blue"))
        print(colored("=" * 78, "blue"))
        row = "|| " + " | ".join(f"{state.decks[i][0]:<12}" if state.cards_left[i] > 0 else (" "*12) for i in range(5)) + " ||"
        print(colored(row, "blue"))
        print(colored("="*78, "blue"))
        row = "|| " + " | ".join(f"{str(state.cards_left[i])} left      " for i in range(5)) + " ||" 
        print(colored(row, "blue"))
        print(colored("="*78, "blue"))
        print("\n")
        
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
        state.decree_used = [False, False]
        state.available_swaps = [0, 0, 0]
        state.available_discards = [0, 0]
        return state

### Functions ###
    # Printing the Game State to the console
    def show(self):
        # River and Emissaries
        current_player = self.current_player + 1
        print("\n")
        print(colored("=" * 18, "blue") + " " * 69 + "=" * 15 + " " * 2 + "=" * 15)
        print(colored("|| River        ||", "blue") + " " * 69 + colored("|| Swaps     ||  || Discards  ||", 'white'))
        print(colored("=" * 78, "blue") + " " * 9 + "=" * 15 + " " * 2 + "=" * 15)
        row = "|| " + " | ".join(f"{self.decks[i][0]:<12}" if self.decks[i] else (" "*12) for i in range(5)) + " ||"
        row += " "*9 + colored("|| ", 'white')
        for i, spot in enumerate(self.available_swaps):
            if spot == 1:
                row += colored("X", "magenta")
            elif spot == 2:
                row += colored("O", "yellow")
            else:
                row += " "
            
            if i != 2:
                row += colored(" | ", 'white')
            else: 
                row += colored(" ||  ||  ", 'white')
        
        for i, spot in enumerate(self.available_discards):
            if spot == 1:
                row += colored("X", "magenta")
            elif spot == 2:
                row += colored("O", "yellow")
            else:
                row += " "
            
            if i != 1:
                row += colored("  |  ", 'white')
            else: 
                row += colored("  ||", 'white')
        
        print(colored(row, "blue"))
        print(colored("="*78, "blue") + " " * 9 + "=" * 32)
        row = "|| " + " | ".join(f"{str(self.cards_left[i])} left      " for i in range(5)) + " ||" 
        row += " "*9 + colored("|| Imp. Decree  ||  ", 'white')
        if self.decree_used[0]:
            row += colored("O", "magenta")
        elif self.decree_used[1]:
            row += colored("O", "yellow")
        else:
            row += " "
        row += "  ||"
        print(colored(row, "blue"))
        print(colored("="*78, "blue") + " " * 9 + "=" * 25)
        print("\n")
        # Player 1
        print(colored(("=" * 18) + (" " * 42) + ("=" * 18), "magenta"))
        print(colored("|| Line         ||" + (" " * 42) + "|| Player 1     ||", "magenta"))
        print(colored("=" * 78, "magenta"))
        line_row = "|| " + " | ".join(f"{card:<12}" for card in self.player_lines[0]) + " ||"
        print(colored(line_row, "magenta"))
        print(colored("=" * 78, "magenta"))
        
        if current_player == 1:
            print(colored("|| Hand         ||", "magenta"))
            print(colored("=" * 78, "magenta"))
            hand_row = "|| " + " | ".join(f"{card:<12}" for card in self.player_hands[0]) + " ||"
            print(colored(hand_row, "magenta"))
            print(colored("=" * 78, "magenta"))
        
        print("\n")
        # Player 2
        print(colored(("=" * 18) + (" " * 42) + ("=" * 18), "yellow"))
        print(colored("|| Line         ||" + (" " * 42) + "|| Player 2     ||", "yellow"))
        print(colored("=" * 78, "yellow"))
        line_row = "|| " + " | ".join(f"{card:<12}" for card in self.player_lines[1]) + " ||"
        print(colored(line_row, "yellow"))
        print(colored("=" * 78, "yellow"))
        
        if current_player == 2:
            print(colored("|| Hand         ||", "yellow"))
            print(colored("=" * 78, "yellow"))
            hand_row = "|| " + " | ".join(f"{card:<12}" for card in self.player_hands[1]) + " ||"
            print(colored(hand_row, "yellow"))
            print(colored("=" * 78, "yellow"))
        
        print("\n")
        print(f'DEBUG : available_swaps : {self.available_swaps}')
        print(f'DEBUG : available_discards : {self.available_discards}')

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
        row = "|| " + " | ".join(f"{self.decks[i][0]:<12}" if self.decks[i] else (" "*12) for i in range(5)) + " ||"
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
            f"Player {player_index + 1}, to develop your territory, which card do you want to discard? (0-{len(line)+len(hand) - 1})\n",
            list(range(0, len(line)+len(hand)))
        )
    
        # Return a tuple: (source, index) -> 'line' or 'hand', index in that source
        if choice <= len(line):
            return ('line', choice)
        else:
            return ('hand', choice - len(line))
    
    def swap_cards(self, current_player, emissaries):
        if current_player == 0:
            color = 'magenta'
        elif current_player == 1:
            color = 'yellow'
        
        if 0 not in self.available_swaps:
            self.error_message = colored("\nThere's no swapping spots available for your emissary\n", 'red')
        else:
            emissaries -= 1
                
            where_choice = get_choice(
                f'Player {current_player + 1}, where do you want to swap cards ? (1-4)\n1. Hand\n2. Line\n3. Between Hand and Line\n4. River',
                [1, 2, 3, 4]
            )
                
            if where_choice == 1:
                print(colored("|| Hand         ||", color))
                print(colored("=" * 88, color))
                hand_row = "|| " + " | ".join(f"{str(i + 5)}.{card:<12}" for i, card in enumerate(self.player_hands[current_player])) + " ||"
                print(colored(hand_row, color))
                print(colored("=" * 88, color))
                print("\n")
                    
                while True:
                    swapping_choice = get_choice(
                        f'Player {current_player + 1}, pick your first card to swap with. (1-5)\n',
                        [1, 2, 3, 4, 5]
                    )
                    swapping_choice_2 = get_choice(
                        f'Player {current_player + 1}, pick the second card to swap with. (1-5)\n',
                        [1, 2, 3, 4, 5]
                        )
                        
                    if swapping_choice_2 != swapping_choice:
                        break
                    else:
                        print(colored("\nYou need to pick two different cards\n", 'red'))
                    
                card_1 = self.player_hands[current_player][swapping_choice - 1]
                card_2 = self.player_hands[current_player][swapping_choice_2 - 1]
                location = 'their Hand'
                self.player_hands[current_player][swapping_choice - 1], self.player_hands[current_player][swapping_choice_2 - 1] = self.player_hands[current_player][swapping_choice_2 - 1], self.player_hands[current_player][swapping_choice - 1]
                
            if where_choice == 2:
                print(colored("|| Line         ||", color))
                print(colored("=" * 88, color))
                line_row = "|| " + " | ".join(f"{str(i + 5)}.{card:<12}" for i, card in enumerate(self.player_lines[current_player])) + " ||"
                print(colored(line_row, color))
                print(colored("=" * 88, color))
                print("\n")
                    
                while True:
                    swapping_choice = get_choice(
                        f'Player {current_player + 1}, pick your first card to swap with. (1-5)\n',
                        [1, 2, 3, 4, 5]
                    )
                    swapping_choice_2 = get_choice(
                        f'Player {current_player + 1}, pick the second card to swap with. (1-5)\n',
                        [1, 2, 3, 4, 5]
                        )
                        
                    if swapping_choice_2 != swapping_choice:
                        break
                    else:
                        print(colored("\nYou need to pick two different cards\n", 'red'))
                    
                card_1 = self.player_lines[current_player][swapping_choice - 1]
                card_2 = self.player_lines[current_player][swapping_choice_2 - 1]
                location = 'their Line'
                self.player_lines[current_player][swapping_choice - 1], self.player_lines[current_player][swapping_choice_2 - 1] = self.player_lines[current_player][swapping_choice_2 - 1], self.player_lines[current_player][swapping_choice - 1]
                
            if where_choice == 3:
                print(colored("|| Hand         ||", "magenta"))
                print(colored("=" * 88, "magenta"))
                hand_row = "|| " + " | ".join(f"{str(i + 5)}.{card:<12}" for i, card in enumerate(self.player_hands[current_player])) + " ||"
                print(colored(hand_row, "magenta"))
                print(colored("=" * 88, "magenta"))
                print("\n")
                print(colored("|| Line         ||", color))
                print(colored("=" * 88, color))
                line_row = "|| " + " | ".join(f"{str(i + 5)}.{card:<12}" for i, card in enumerate(self.player_lines[current_player])) + " ||"
                print(colored(line_row, color))
                print(colored("=" * 88, color))
                print("\n")
                    
                swapping_choice = get_choice(
                    f'Player {current_player + 1}, pick the position in which you want your cards in your Hand and Line to be swapped. (1-5)\n',
                    [1, 2, 3, 4, 5]
                )
                        
                card_1 = self.player_hands[current_player][swapping_choice - 1]
                card_2 = self.player_lines[current_player][swapping_choice - 1]

                self.player_lines[current_player][swapping_choice - 1], self.player_hands[current_player][swapping_choice - 1] = self.player_hands[current_player][swapping_choice - 1], self.player_lines[current_player][swapping_choice - 1]
                
            if where_choice == 4:
                # Printing the River
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
                    
                while True:
                    swapping_choice = get_choice(
                        f'Player {current_player + 1}, pick a first deck to swap its top card.. (1-5)\n',
                        [1, 2, 3, 4, 5]
                    )
                    swapping_choice_2 = get_choice(
                        f'Player {current_player + 1}, pick the second deck to swap its top card with the first one. (1-5)\n',
                        [1, 2, 3, 4, 5]
                        )
                    if self.decks[swapping_choice - 1][0] and self.decks[swapping_choice_2 - 1][0]:
                        if swapping_choice_2 != swapping_choice:
                            break
                        else:
                            print(colored("\nYou need to pick two different cards\n", 'red'))
                    else:
                            print(colored("\nYou cannot pick and empty deck.\n", 'red'))
                    
                card_1 = self.decks[swapping_choice - 1][0]
                card_2 = self.decks[swapping_choice_2 - 1][0]
                location = 'the River'
                self.decks[swapping_choice - 1][0], self.decks[swapping_choice_2 - 1][0] = self.decks[swapping_choice_2 - 1][0], self.decks[swapping_choice - 1][0]
                
            if where_choice != 3:    
                self.game_message = colored(f"\nPlayer {current_player + 1} swapped {card_1} in position {swapping_choice} and {card_2} in position {swapping_choice_2} from {location}\n", 'green')
            else:
                self.game_message = colored(f"\nPlayer {current_player + 1} swapped {card_1} and {card_2} in position {swapping_choice} between their Line and Hand\n", 'green')
                
            for i, spot in enumerate(self.available_swaps):
                if spot == 0:
                    self.available_swaps[i] = current_player + 1
                    break           
    
    def discard_river(self, current_player, emissaries):
        if 0 not in self.available_discards:
            self.error_message = colored("\nThere's no discarding spots available for your emissary\n", 'red')
        else:
            emissaries -= 1
                
            # Printing the River
            print("\n")
            print(colored("=" * 18, "blue"))
            print(colored("|| River        ||", "blue"))
            print(colored("=" * 78, "blue"))
            row = "|| " + " | ".join(f"{self.decks[i][0]:<12}" if self.decks[i] else (" "*12) for i in range(5)) + " ||"
            print(colored(row, "blue"))
            print(colored("="*78, "blue"))
            row = "|| " + " | ".join(f"{str(self.cards_left[i])} left      " for i in range(5)) + " ||" 
            print(colored(row, "blue"))
            print(colored("="*78, "blue"))
            print("\n")
                
            while True:
                discard_choice = get_choice(
                    f'Player {current_player + 1}, which first card do you want to discard ? (1-5)\n',
                    [1, 2, 3, 4, 5]
                )
                discard_choice_2 = get_choice(
                f'Player {current_player + 1}, which second card do you want to discard ? (1-5)\n',
                [1, 2, 3, 4, 5]
                )
                if discard_choice_2 != discard_choice:
                    break
                else:
                    print(colored("\nYou need to pick two different cards\n", 'red'))
                
            index = discard_choice - 1
            index_2 = discard_choice_2 - 1
                
            self.game_message = colored(f"\nPlayer {current_player + 1} discarded {self.decks[index][0]} in position {index+1} and {self.decks[index_2][0]} in position {index_2+1} from the River.\n", 'green')
                
            self.decks[index].pop(0)
            self.decks[index_2].pop(0)
                
            for i, spot in enumerate(self.available_discards):
                if spot == 0:
                    self.available_discards[i] = current_player + 1
                    break 
    
    def recall_emissaries(self, current_player, emissaries):
        if self.decree_used[current_player] and emissaries != 1:
            emissaries = 1
            
            for i, spot in enumerate(self.available_swaps):
                if spot == current_player + 1:
                    self.available_swaps[i] = 0
            for i, spot in enumerate(self.available_discards):
                if spot == current_player + 1:
                    self.available_discards[i] = 0
                
            self.game_message = colored("\nYou recalled your emissary left (the second one is locked by the decree)\n", 'green')
            
        elif not self.decree_used[current_player] and emissaries != 2:
            emissaries = 2
            
            for i, spot in enumerate(self.available_swaps):
                if spot == current_player + 1:
                    self.available_swaps[i] = 0
            for i, spot in enumerate(self.available_discards):
                if spot == current_player + 1:
                    self.available_discards[i] = 0
            self.game_message = colored("\nYou recalled both your emissaries\n", 'green')
        else:
            self.error_message = colored("\nYou already have all your available emissaries\n", 'red')
    
    def impose_decree(self, current_player, emissaries):
        opponent = 1 - current_player
        if True not in self.decree_used and emissaries != 0:
            self.decree_used[current_player] = True
            emissaries -= 1
            
            if current_player == 0:
                # Player 1
                print(colored("=" * 18, "magenta"))
                print(colored(f"|| Player {current_player + 1}     ||", "magenta"))
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
                print(colored(f"|| Player {current_player + 1}     ||", "yellow"))
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
    
            decree_choice = get_choice(
                f'Player {current_player + 1}, which of your cards do you want to impose a decree on ? (0-9)\n',
                [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
            )
            
            if decree_choice < 5:
                index = decree_choice
                self.game_message = colored(f"\nPlayer {current_player + 1} swapped a {self.player_lines[current_player][index]} for a {self.player_lines[opponent][index]}.\n", 'green')
                self.player_lines[0][index], self.player_lines[1][index] = self.player_lines[1][index], self.player_lines[0][index]

            else:
                index = decree_choice - 5
                self.game_message = colored(f"\nPlayer {current_player + 1} swapped a {self.player_hands[current_player][index]} for a {self.player_hands[opponent][index]}.\n", 'green')
                self.player_hands[0][index], self.player_hands[1][index] = self.player_hands[1][index], self.player_hands[0][index]
            
        elif True not in self.decree_used and emissaries == 0:
            self.error_message = colored("\nYou don't have an available emissary\n", 'red')
            
        else:
            self.error_message = colored('\nThe decree has already been used\n', 'red') 
    
    def develop_territory(self, current_player):
        while True:
                try:
                    source, index = self.choose_discard(current_player)
                    if source == 'hand':
                        self.player_hands[current_player][index] = self.decks[index][0]
                        self.decks[index].pop(0)
                        self.game_message = colored(f"\nPlayer {current_player + 1} added {self.player_hands[current_player][index]} to the position {index+1} in their {source}.\n", 'green')
                    else:
                        self.player_lines[current_player][index] = self.decks[index][0]
                        self.decks[index].pop(0)
                        self.game_message = colored(f"\nPlayer {current_player + 1} added {self.player_lines[current_player][index]} to the position {index+1} in their {source}.\n", 'green')
                    break
                except IndexError:
                    print(colored('This deck is empty, please choose another one.', 'red'))

    # Playing a turn 
    def play(self):
        current_player = self.current_player
        opponent = 1 - current_player
        emissaries = self.emissaries[current_player]
        
        if self.error_message != '':
            print(self.error_message + '\n')
        
        if self.game_message != '':
            print(self.game_message + '\n')

        self.error_message = ''
        self.game_message = ''
        
        # Playing options
        choice = get_choice(
            f'Player {current_player + 1}, what do you want to do ?\n\n1. Develop your Territory\n2. Send an Emissary\n3. Recall your Emissaries\n4. Impose an Imperial Decree\n5. Declare the end of the game\n\n',
            [1, 2, 3, 4, 5]
        ) 
        
        # Developing the Territory
        if choice == 1:
            self.develop_territory(current_player)
            
            if emissaries != 0:
                emissary_choice = get_choice(
                    f'Player {current_player + 1}, do you also want to send an Emissary this turn ? (1-3)\n1. Swap two cards\n2. Discard two River cards\n3. No, thank you\n',
                    [1, 2, 3]
                )
                
                if emissary_choice == 1:
                    self.swap_cards(current_player, emissaries)
                elif emissary_choice == 2:
                    self.discard_river(current_player, emissaries)
        
        # Sending emissaries
        if choice == 2 and emissaries != 0:
            # Choice
            emissary_choice = get_choice(
                f'Player {current_player + 1}, what do you want to do with this Emissary ? (1-2)\n1. Swap two cards\n2. Discard two River cards\n\n',
                [1, 2]
            )
            if emissary_choice == 1:
                self.swap_cards(current_player, emissaries)
            else:
                self.discard_river(current_player, emissaries)
            
            print('You now need to develop your territory.')
            self.develop_territory(current_player)
            
        elif choice == 2 and emissaries == 0:
            self.error_message = colored("\nYou don't have an available emissary\n", 'red')

        # Recalling emissaries
        if choice == 3:
            self.recall_emissaries(current_player, emissaries)
        
        # Imposing an Imperial Decree
        if choice == 4:
            self.impose_decree(current_player, emissaries)     
        
        # Declaring the end of the game
        if choice == 5 and self.ending_available:
            return True    
        elif choice == 5:
            self.error_message = colored("\nYou can't end the game yet, no deck is empty\n", 'red')
        
        # Check if game should end due to empty decks
        if self.check_ending():
            return True
        
        self.update_state(current_player, emissaries)
        return False  # Continue the game

    def score(self):
        player_scores = {
            0 : {
                "Mountain" : 0,
                "Naishi" : 0, 
                "Councellor" : 0,  
                "Sentinel" : 0, 
                "Fort" : 0,  
                "Monk" : 0,  
                "Torii" : 0, 
                "Knight" : 0, 
                "Banner" : 0, 
                "Rice fields" : 0, 
                "Ronin" : 0, 
                "Ninja" : 0,
                "Total" : 0 
            },
            1 : {
                "Mountain" : 0,
                "Naishi" : 0, 
                "Councellor" : 0,  
                "Sentinel" : 0, 
                "Fort" : 0,  
                "Monk" : 0,  
                "Torii" : 0, 
                "Knight" : 0, 
                "Banner" : 0, 
                "Rice fields" : 0, 
                "Ronin" : 0, 
                "Ninja" : 0,
                "Total" : 0,
            }
        }
        
        for player, score_table in player_scores.items():
            # Init
            mountains = 0
            toriis = 0
            banners = 0
            ronins = 0
            rice_fields = []
            cards = self.player_lines[player] + self.player_hands[player]
            
            if player == 0:
                color = 'magenta'
            elif player == 1:
                color = 'yellow'
            
            # Ninja
            for i, card in enumerate(cards):
                if card == 'Ninja':
                    print(colored("|| Hand         ||", "magenta"))
                    print(colored("=" * 88, "magenta"))
                    hand_row = "|| " + " | ".join(f"{str(i + 5)}.{card:<12}" for i, card in enumerate(self.player_hands[player])) + " ||"
                    print(colored(hand_row, "magenta"))
                    print(colored("=" * 88, "magenta"))
                    print("\n")
                    print(colored("|| Line         ||", color))
                    print(colored("=" * 88, color))
                    line_row = "|| " + " | ".join(f"{str(i + 5)}.{card:<12}" for i, card in enumerate(self.player_lines[player])) + " ||"
                    print(colored(line_row, color))
                    print(colored("=" * 88, color))
                    print("\n")
                    
                    if self.error_message:
                        print(self.error_message + '\n')
                    
                    while True:
                        ninja_choice = get_choice(
                        f'Player {player + 1}, what card do you want to copy with the Ninja in position {i} ? (1-10)\n',
                            range(1, 11)
                        )
                        
                        copy = cards[ninja_choice]
                    
                        if copy == 'Ninja':
                            print(colored('\nYou need to pick a different card than the Ninja himself', 'red'))
                        elif copy not in self.characters:
                            print(colored('\nYou need to pick a character for the Ninja to copy', 'red'))
                        else: 
                            break
                    card = copy          
                
            # Ronin preparation
            filtered_cards = [card for card in set(cards) if card != 'Mountain']
            num_ronin = len(filtered_cards)
            
            for i, card in enumerate(cards):
                
                # Count based scoring preparation 
                if card == 'Mountain':
                    mountains += 1
                elif card == 'Torii':
                    toriis += 1
                elif card == 'Banner':
                    banners += 1
                elif card == 'Ronin':
                    ronins += 1
                
                # Absolute positional scoring
                elif card == 'Naishi':
                    if i == 2:
                        score_table['Naishi'] += 12
                    elif i == 7:
                        score_table['Naishi'] += 8
                elif card == 'Fort':
                    if i == 0 or i == 4 or i == 5 or i == 9:
                        score_table['Fort'] += 6
                
                # Relative positional scoring
                else:
                    adjacency = check_adjacency(i, cards)
                    
                    if card == 'Councellor':
                        if i == 1 or i == 6 or i == 3 or i == 8:
                            score_table['Councellor'] += 4
                        elif i == 2 or i == 7:
                            score_table['Councellor'] += 3
                        else:
                            score_table['Councellor'] += 2
                        
                        for adjacent_card in adjacency.values():
                            if adjacent_card['card'] == 'Naishi':
                                score_table['Councellor'] += 4
                    
                    elif card == 'Sentinel':
                        if 'Sentinel' not in adjacency.values():
                            score_table['Sentinel'] += 3
                        
                        for adjacent_card in adjacency.values():
                            if adjacent_card['card'] == 'Fort':
                                score_table['Sentinel'] += 4
                    
                    elif card == 'Monk':
                        if i > 4:
                            score_table['Monk'] += 5
                        
                        for adjacent_card in adjacency.values():
                            if adjacent_card['card'] == 'Torii':
                                score_table['Monk'] += 2
                    
                    elif card == 'Knight':
                        if i > 4:
                            score_table['Knight'] += 3
                        
                        if adjacency['up']['card'] == 'Banner':
                                score_table['Knight'] += 10

            fields_groups = []
            scoring_fields = []
            processed = set()

            for i, card in enumerate(cards):
                if card == 'Rice fields' and i not in processed:
                    # BFS/DFS to find all connected cards
                    group = []
                    stack = [i]
        
                    while stack:
                        current = stack.pop()
                        if current in processed:
                            continue
            
                        processed.add(current)
                        group.append(current)
            
                        adjacents = check_adjacency(current, cards)
                        for direction, info in adjacents.items():
                            adj_idx = info['position']
                            if info['card'] == 'Rice fields' and adj_idx not in processed:
                                stack.append(adj_idx)
        
                    group.sort()
                    scoring_fields.extend(group)
                    fields_groups.append(len(group))
            
            for group in fields_groups:
                score = 10 * (group - 1)
                if group == 5:
                    score = 40
                score_table['Rice fields'] += score
            
            # Count based scoring
            if mountains == 1:
                score_table['Mountain'] = 5
            elif mountains > 1:
                score_table['Mountain'] = -5
            
            if toriis == 1:
                score_table['Torii'] = -5
            elif toriis >= 3:
                score_table['Torii'] = 30
            
            if banners == 1:
                score_table['Banner'] = 3
            elif banners == 2:
                score_table['Banner'] = 8
            
            # Ronin scoring
            if num_ronin == 8:
                score_table['Ronin'] = ronins * 8
            elif num_ronin == 9:
                score_table['Ronin'] = ronins * 15
            elif num_ronin == 10:
                score_table['Ronin'] = 45
        # Calcul du total
        for player in player_scores.values():
            for name, value in player.items():
                if name != 'Total':
                    player['Total'] += value
        
        # Affichage            
        color1 = 'magenta'
        color2 = 'yellow'
        cards = self.cards
        cards.insert(0, 'Mountain')
        cards.append('Total')
        player1_data = list(zip(cards, player_scores[0].values()))
        player2_data = list(zip(cards, player_scores[1].values()))

        print(colored("|| Player 1       ||", color1) + "  " + colored("|| Player 2        ||", color2))
        print(colored("=" * 20, color1) + "  " + colored("=" * 20, color2))

        for (card1, score1), (card2, score2) in zip(player1_data, player2_data):
            print(colored(f"|| {card1:<12}   ||", color1) + "  " + colored(f"|| {card2:<12}   ||", color2))
            print(colored(f"|| {score1:<12}   ||", color1) + "  " + colored(f"|| {score2:<12}   ||", color2))
            print(colored("-" * 20, color1) + "  " + colored("-" * 20, color2))

        print("\n")
        score_p1 = player_scores[0]['Total']
        score_p2 = player_scores[1]['Total']
        
        if score_p1 == score_p2:
            for player in self.current_player:
                cards = self.player_lines[player] + self.player_hands[player]
                filtered_cards = [card for card in set(cards) if card != 'Mountain' and card != 'Ninja']
                num_ronin = len(filtered_cards)
                if player == 0:
                    score_p1 = num_ronin
                if player == 1:
                    score_p2 = num_ronin     
        
        if score_p1 > score_p2:
            print(f'Player 1 Victory {score_p1} to {score_p2} !')
        elif score_p1 == score_p2:
            print(f'True equality, play again !')
        else:
            print(f'Player 2 Victory {score_p2} to {score_p1} !')
         
    def update_state(self, current_player, emissaries):
        ### State update ###
        for deck in self.decks:
            if not deck:
                self.ending_available = True
        
        if len(self.error_message) == 0:
            self.current_player = 1 - current_player
        
        self.emissaries[current_player] = emissaries
        
        for i, deck in enumerate(self.decks):
            self.cards_left[i] = len(deck)
    
    def check_ending(self):
        # When 2 decks are made empty by the first player
        if self.end_next_turn:
            return True
        
        # Checking if two decks are empty
        empty_decks_count = 0
        
        for deck in self.decks:
            if not deck:
                empty_decks_count += 1
            if empty_decks_count > 1:
                if self.current_player == 0:
                    self.end_next_turn = True
                    return False
                else:
                    return True
        
        return False

