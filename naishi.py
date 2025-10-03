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
            f"Player {player_index + 1}, which card do you want to discard? (0-{len(line)+len(hand) - 1})\n",
            list(range(0, len(line)+len(hand)))
        )
    
        # Return a tuple: (source, index) -> 'line' or 'hand', index in that source
        if choice <= len(line):
            return ('line', choice)
        else:
            return ('hand', choice - len(line))


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
        
        # Developing a Territory
        if choice == 1:
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
        
        # Sending emissaries
        if choice == 2 and emissaries != 0:
            # Choice
            emissary_choice = get_choice(
                f'Player {current_player + 1}, what do you want to do with this Emissary ? (1-2)\n1. Swap two cards\n2. Discard two River cards\n\n',
                [1, 2]
            )
            
            # Swapping cards
            if emissary_choice == 1 and current_player == 0:
                color = 'magenta'
            elif emissary_choice == 1 and current_player == 1:
                color = 'yellow'
            if emissary_choice == 1 and 0 in self.available_swaps:
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
        
            elif emissary_choice == 1:
                self.error_message = colored("\nThere's no swapping spots available for your emissary\n", 'red')
            
            # Discarding the River
            elif emissary_choice == 2 and 0 in self.available_discards:
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
            
            elif emissary_choice == 2:
                self.error_message = colored("\nThere's no discarding spots available for your emissary\n", 'red')
            
        elif choice == 2 and emissaries == 0:
            self.error_message = colored("\nYou don't have an available emissary\n", 'red')
        
        
        # Recalling emissaries
        if choice == 3:
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
        
        # Imposing an Imperial Decree
        if choice == 4 and True not in self.decree_used and emissaries != 0:
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
            
        elif choice == 4 and True not in self.decree_used and emissaries == 0:
            self.error_message = colored("\nYou don't have an available emissary\n", 'red')
            
        elif choice == 4:
            self.error_message = colored('\nThe decree has already been used\n', 'red')      
        
        ### Ending the game ###
        # By choice
        if choice == 5 and self.ending_available:
            return True    
        elif choice == 5:
            self.error_message = colored("\nYou can't end the game yet, no deck is empty\n", 'red')
        
        # When 2 decks are made empty by the first player
        if self.end_next_turn:
            return True
        
        # Checking if two decks are empty
        empty_decks_count = 0
        
        for deck in self.decks:
            if not deck:
                count +=1
            if count > 1:
                if current_player == 0:
                    return True
                else:
                    self.end_next_turn = True
    
         
        ### State update ###
        if 0 in self.cards_left:
            self.ending_available = True
        
        if len(self.error_message) == 0:
            self.current_player = 1 - current_player
        
        self.emissaries[current_player] = emissaries
        
        for i, deck in enumerate(self.decks):
            self.cards_left[i] = len(deck)

        