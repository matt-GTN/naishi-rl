# naishi_pvp.py

import random as r
from termcolor import colored
from banner import print_banner
from naishi_core import (
    Player, River, Scorer,
    CARDS, CHARACTERS, CARDS_COUNT,
    NUM_DECKS, CARDS_PER_DECK, LINE_SIZE, HAND_SIZE,
    get_choice, MAX_SWAPS, MAX_DISCARDS
)


class GameState:
    """Manages game state for human PvP play"""
    
    def __init__(self, seed=None):
        if seed is not None:
            r.seed(seed)
        
        self.players = [Player(0), Player(1)]
        self.river = River()
        self.current_player_index = 0
        self.available_swaps = [0, 0, 0]
        self.available_discards = [0, 0]
        self.ending_available = False
        self.end_next_turn = False
        self.error_message = ''
        self.game_message = ''
        self.turn_count = 0
    
    @staticmethod
    def create_initial_state(seed=None, ai_player_index=None):
        """Initialize and set up a new game"""
        print("\n")
        print_banner()
        print("\n\n")
        
        game = GameState(seed)
        game._setup_game()
        return game
    
    def _setup_game(self, ai_player_index=None):
        """Set up initial game state"""
        # Create and shuffle all cards
        total_cards = []
        for card, count in zip(CARDS, CARDS_COUNT):
            total_cards.extend([card] * count)
        r.shuffle(total_cards)
        
        # Deal to river (5 decks of 6 cards)
        for i in range(NUM_DECKS):
            start = i * CARDS_PER_DECK
            end = (i + 1) * CARDS_PER_DECK
            self.river.decks[i] = total_cards[start:end]
        
        # Initial hands (2 cards each from end of deck)
        player_hands = [
            total_cards[-2:],
            total_cards[-4:-2]
        ]
        
        # Show river for drafting
        self._display_river_for_draft()
        
        if ai_player_index == 0:
            p1_choice = r.choice([1, 2])
            print(colored(f"Player 1 (AI) chooses to give card #{p1_choice}", "yellow"))
        else:
            p1_choice = get_choice(
                f'Player 1 - What card do you want to give to your opponent? (1/2)\n\n1. {player_hands[0][0]}\n2. {player_hands[0][1]}\n\n',
                [1, 2]
            )
            
        if ai_player_index == 1:
            p2_choice = r.choice([1, 2])
            print(colored(f"Player 2 (AI) chooses to give card #{p2_choice}", "yellow"))
        else:
            p2_choice = get_choice(
                f'Player 2 - What card do you want to give to your opponent? (1/2)\n\n1. {player_hands[1][0]}\n2. {player_hands[1][1]}\n\n',
                [1, 2]
            )
        
        # Perform exchanges
        p1_idx = p1_choice - 1
        p2_idx = p2_choice - 1
        player_hands[0][p1_idx], player_hands[1][p2_idx] = \
            player_hands[1][p2_idx], player_hands[0][p1_idx]
        
        # Add mountains and shuffle
        for hand in player_hands:
            hand.extend(['Mountain'] * 3)
            r.shuffle(hand)
        
        # Set up players
        for i, player in enumerate(self.players):
            player.hand = player_hands[i]
            player.line = ['Mountain'] * LINE_SIZE
    
    def _display_river_for_draft(self):
        """Display river during initial draft"""
        print("\n")
        print(colored("   River          ", "blue"))
        print(colored("=" * 78, "blue"))
        cards_left = self.river.cards_left()
        row = "|| " + " | ".join(
            f"{self.river.get_top_card(i):<12}" if cards_left[i] > 0 else (" "*12)
            for i in range(NUM_DECKS)
        ) + " ||"
        print(colored(row, "blue"))
        print(colored("="*78, "blue"))
        row = "|| " + " | ".join(f"{cards_left[i]} left      " for i in range(NUM_DECKS)) + " ||"
        print(colored(row, "blue"))
        print(colored("="*78, "blue"))
        print("\n")
    
    @property
    def current_player(self) -> Player:
        return self.players[self.current_player_index]
    
    @property
    def opponent(self) -> Player:
        return self.players[1 - self.current_player_index]
    
    def show(self):
        """Display full game state"""
        print("\n")
        self._show_river()
        self._show_emissary_status()
        print("\n")
        self._show_player(self.players[0], show_hand=(self.current_player_index == 0))
        print("\n")
        self._show_player(self.players[1], show_hand=(self.current_player_index == 1))
        print("\n")
    
    def _show_river(self):
        """Display river and emissary tracking"""
        print(colored("   River          ", "blue") + " " * 69 + colored("   Swaps            Discards    ", 'white'))
        print(colored("=" * 78, "blue") + " " * 9 + "=" * 15 + " " * 2 + "=" * 15)
        
        # River cards
        cards_left = self.river.cards_left()
        row = "|| " + " | ".join(
            f"{self.river.get_top_card(i) or '':<12}"
            for i in range(NUM_DECKS)
        ) + " ||"
        
        # Swap markers
        row += " "*9 + colored("|| ", 'white')
        for i, spot in enumerate(self.available_swaps):
            if spot == 1:
                row += colored("X", "magenta")
            elif spot == 2:
                row += colored("O", "yellow")
            else:
                row += " "
            row += colored(" | " if i != 2 else " ||  ||  ", 'white')
        
        # Discard markers
        for i, spot in enumerate(self.available_discards):
            if spot == 1:
                row += colored("X", "magenta")
            elif spot == 2:
                row += colored("O", "yellow")
            else:
                row += " "
            row += colored("  |  " if i != 1 else "  ||", 'white')
        
        print(colored(row, "blue"))
        print(colored("="*78, "blue") + " " * 9 + "=" * 32)
        
        # Cards left
        row = "|| " + " | ".join(f"{cards_left[i]} left      " for i in range(NUM_DECKS)) + " ||"
        row += " "*9 + colored("|| Imp. Decree  ||  ", 'white')
        if self.players[0].decree_used:
            row += colored("X", "magenta")
        elif self.players[1].decree_used:
            row += colored("O", "yellow")
        else:
            row += " "
        row += "  ||"
        print(colored(row, "blue"))
        print(colored("="*78, "blue") + " " * 9 + "=" * 25)
    
    def _show_emissary_status(self):
        """Show detailed emissary status"""
        pass  # Already shown in river display
    
    def _show_player(self, player: Player, show_hand: bool):
        """Display a player's state"""
        color = player.color
        player_num = player.index + 1
        
        print(colored("   Line           " + (" " * 42) + f"  Player {player_num}", color))
        print(colored("=" * 78, color))
        line_row = "|| " + " | ".join(f"{card:<12}" for card in player.line) + " ||"
        print(colored(line_row, color))
        print(colored("=" * 78, color))
        
        if show_hand:
            print("\n")
            print(colored("   Hand           ", color))
            print(colored("=" * 78, color))
            hand_row = "|| " + " | ".join(f"{card:<12}" for card in player.hand) + " ||"
            print(colored(hand_row, color))
            print(colored("=" * 78, color))
    
    def choose_discard(self, player: Player) -> tuple:
        """Display hand + line with numbers for discarding and returns the choice"""
        color = player.color
        player_num = player.index + 1
        
        # Show river
        print("\n")
        print(colored("   River          ", "blue"))
        print(colored("=" * 78, "blue"))
        row = "|| " + " | ".join(
            f"{self.river.get_top_card(i) or '':<12}"
            for i in range(NUM_DECKS)
        ) + " ||"
        print(colored(row, "blue"))
        print(colored("="*78, "blue"))
        cards_left = self.river.cards_left()
        row = "|| " + " | ".join(f"{cards_left[i]} left      " for i in range(NUM_DECKS)) + " ||"
        print(colored(row, "blue"))
        print(colored("="*78, "blue"))
        print("\n")
        
        # Show player cards with indices
        print(colored(f"  Player {player_num}       ", color))
        print(colored("   Line           ", color))
        print(colored("=" * 88, color))
        line_row = "|| " + " | ".join(f"{i}.{card:<12}" for i, card in enumerate(player.line)) + " ||"
        print(colored(line_row, color))
        print(colored("=" * 88, color))
        print(colored("   Hand           ", color))
        print(colored("=" * 88, color))
        hand_row = "|| " + " | ".join(f"{i + LINE_SIZE}.{card:<12}" for i, card in enumerate(player.hand)) + " ||"
        print(colored(hand_row, color))
        print(colored("=" * 88, color))
        print("\n")
        
        # Get choice
        choice = get_choice(
            f"Player {player_num}, to develop your territory, which card do you want to discard? (0-{LINE_SIZE + HAND_SIZE - 1})\n",
            list(range(0, LINE_SIZE + HAND_SIZE))
        )
        
        if choice < LINE_SIZE:
            return ('line', choice)
        else:
            return ('hand', choice - LINE_SIZE)
    
    def develop_territory(self, player: Player):
        """Develop territory by discarding a card and drawing from river"""
        while True:
            try:
                source, index = self.choose_discard(player)
                new_card = self.river.draw_card(index)
                player.replace_card(source, index, new_card)
                self.game_message = colored(
                    f"\nPlayer {player.index + 1} added {new_card} to position {index} in their {source}.\n",
                    'green'
                )
                break
            except IndexError:
                print(colored('This deck is empty, please choose another one.', 'red'))
    
    def swap_cards(self, player: Player):
        """Send emissary to swap cards"""
        if 0 not in self.available_swaps:
            self.error_message = colored("\nThere's no swapping spots available for your emissary\n", 'red')
            return
        
        player.use_emissary()
        color = player.color
        player_num = player.index + 1
        
        where_choice = get_choice(
            f'Player {player_num}, where do you want to swap cards? (1-4)\n1. Hand\n2. Line\n3. Between Hand and Line\n4. River\n',
            [1, 2, 3, 4]
        )
        
        if where_choice == 1:
            # Swap in hand
            print(colored("   Hand           ", color))
            print(colored("=" * 88, color))
            hand_row = "|| " + " | ".join(f"{i + 1}.{card:<12}" for i, card in enumerate(player.hand)) + " ||"
            print(colored(hand_row, color))
            print(colored("=" * 88, color))
            print("\n")
            
            while True:
                pos1 = get_choice(f'Player {player_num}, pick your first card to swap. (1-5)\n', [1, 2, 3, 4, 5]) - 1
                pos2 = get_choice(f'Player {player_num}, pick the second card to swap. (1-5)\n', [1, 2, 3, 4, 5]) - 1
                if pos1 != pos2:
                    break
                print(colored("\nYou need to pick two different cards\n", 'red'))
            
            card1, card2 = player.hand[pos1], player.hand[pos2]
            player.swap_in_hand(pos1, pos2)
            self.game_message = colored(
                f"\nPlayer {player_num} swapped {card1} in position {pos1+1} and {card2} in position {pos2+1} in their Hand\n",
                'green'
            )
        
        elif where_choice == 2:
            # Swap in line
            print(colored("   Line           ", color))
            print(colored("=" * 88, color))
            line_row = "|| " + " | ".join(f"{i + 1}.{card:<12}" for i, card in enumerate(player.line)) + " ||"
            print(colored(line_row, color))
            print(colored("=" * 88, color))
            print("\n")
            
            while True:
                pos1 = get_choice(f'Player {player_num}, pick your first card to swap. (1-5)\n', [1, 2, 3, 4, 5]) - 1
                pos2 = get_choice(f'Player {player_num}, pick the second card to swap. (1-5)\n', [1, 2, 3, 4, 5]) - 1
                if pos1 != pos2:
                    break
                print(colored("\nYou need to pick two different cards\n", 'red'))
            
            card1, card2 = player.line[pos1], player.line[pos2]
            player.swap_in_line(pos1, pos2)
            self.game_message = colored(
                f"\nPlayer {player_num} swapped {card1} in position {pos1+1} and {card2} in position {pos2+1} in their Line\n",
                'green'
            )
        
        elif where_choice == 3:
            # Swap between hand and line
            print(colored("   Hand           ", color))
            print(colored("=" * 88, color))
            hand_row = "|| " + " | ".join(f"{i + 1}.{card:<12}" for i, card in enumerate(player.hand)) + " ||"
            print(colored(hand_row, color))
            print(colored("=" * 88, color))
            print("\n")
            print(colored("   Line           ", color))
            print(colored("=" * 88, color))
            line_row = "|| " + " | ".join(f"{i + 1}.{card:<12}" for i, card in enumerate(player.line)) + " ||"
            print(colored(line_row, color))
            print(colored("=" * 88, color))
            print("\n")
            
            position = get_choice(
                f'Player {player_num}, pick the position to swap between Hand and Line. (1-5)\n',
                [1, 2, 3, 4, 5]
            ) - 1
            
            card1, card2 = player.hand[position], player.line[position]
            player.swap_between_line_and_hand(position)
            self.game_message = colored(
                f"\nPlayer {player_num} swapped {card1} and {card2} in position {position+1} between Hand and Line\n",
                'green'
            )
        
        elif where_choice == 4:
            # Swap in river
            print("\n")
            print(colored("   River          ", "blue"))
            print(colored("=" * 78, "blue"))
            cards_left = self.river.cards_left()
            row = "|| " + " | ".join(
                f"{self.river.get_top_card(i) or '':<12}"
                for i in range(NUM_DECKS)
            ) + " ||"
            print(colored(row, "blue"))
            print(colored("="*78, "blue"))
            row = "|| " + " | ".join(f"{cards_left[i]} left      " for i in range(NUM_DECKS)) + " ||"
            print(colored(row, "blue"))
            print(colored("="*78, "blue"))
            print("\n")
            
            while True:
                deck1 = get_choice(f'Player {player_num}, pick first deck to swap. (1-5)\n', [1, 2, 3, 4, 5]) - 1
                deck2 = get_choice(f'Player {player_num}, pick second deck to swap. (1-5)\n', [1, 2, 3, 4, 5]) - 1
                
                if not self.river.get_top_card(deck1) or not self.river.get_top_card(deck2):
                    print(colored("\nYou cannot pick an empty deck.\n", 'red'))
                elif deck1 == deck2:
                    print(colored("\nYou need to pick two different decks\n", 'red'))
                else:
                    break
            
            card1 = self.river.get_top_card(deck1)
            card2 = self.river.get_top_card(deck2)
            self.river.swap_top_cards(deck1, deck2)
            self.game_message = colored(
                f"\nPlayer {player_num} swapped {card1} in deck {deck1+1} and {card2} in deck {deck2+1} in the River\n",
                'green'
            )
        
        # Mark swap spot as used
        for i, spot in enumerate(self.available_swaps):
            if spot == 0:
                self.available_swaps[i] = player.index + 1
                break
    
    def discard_river(self, player: Player):
        """Send emissary to discard river cards"""
        if 0 not in self.available_discards:
            self.error_message = colored("\nThere's no discarding spots available for your emissary\n", 'red')
            return
        
        player.use_emissary()
        player_num = player.index + 1
        
        # Show river
        print("\n")
        print(colored("   River          ", "blue"))
        print(colored("=" * 78, "blue"))
        cards_left = self.river.cards_left()
        row = "|| " + " | ".join(
            f"{self.river.get_top_card(i) or '':<12}"
            for i in range(NUM_DECKS)
        ) + " ||"
        print(colored(row, "blue"))
        print(colored("="*78, "blue"))
        row = "|| " + " | ".join(f"{cards_left[i]} left      " for i in range(NUM_DECKS)) + " ||"
        print(colored(row, "blue"))
        print(colored("="*78, "blue"))
        print("\n")
        
        while True:
            deck1 = get_choice(f'Player {player_num}, which first card do you want to discard? (1-5)\n', [1, 2, 3, 4, 5]) - 1
            deck2 = get_choice(f'Player {player_num}, which second card do you want to discard? (1-5)\n', [1, 2, 3, 4, 5]) - 1
            if deck1 != deck2:
                break
            print(colored("\nYou need to pick two different cards\n", 'red'))
        
        card1 = self.river.get_top_card(deck1) or "Empty"
        card2 = self.river.get_top_card(deck2) or "Empty"
        self.river.discard_top_cards(deck1, deck2)
        
        self.game_message = colored(
            f"\nPlayer {player_num} discarded {card1} in deck {deck1+1} and {card2} in deck {deck2+1} from the River.\n",
            'green'
        )
        
        # Mark discard spot as used
        for i, spot in enumerate(self.available_discards):
            if spot == 0:
                self.available_discards[i] = player.index + 1
                break
    
    def recall_emissaries(self, player: Player):
        """Recall all available emissaries"""
        locked = player.decree_used
        max_available = 1 if locked else 2
        
        if player.emissaries == max_available:
            self.error_message = colored("\nYou already have all your available emissaries\n", 'red')
            return
        
        # Clear spots used by this player
        for i, spot in enumerate(self.available_swaps):
            if spot == player.index + 1:
                self.available_swaps[i] = 0
        for i, spot in enumerate(self.available_discards):
            if spot == player.index + 1:
                self.available_discards[i] = 0
        
        player.recall_emissaries(locked)
        
        if locked:
            self.game_message = colored("\nYou recalled your emissary (the second one is locked by the decree)\n", 'green')
        else:
            self.game_message = colored("\nYou recalled both your emissaries\n", 'green')
    
    def impose_decree(self, player: Player):
        """Impose imperial decree to swap cards with opponent"""
        if self.players[0].decree_used or self.players[1].decree_used:
            self.error_message = colored('\nThe decree has already been used\n', 'red')
            return
        
        if player.emissaries == 0:
            self.error_message = colored("\nYou don't have an available emissary\n", 'red')
            return
        
        player.decree_used = True
        player.use_emissary()
        
        color = player.color
        player_num = player.index + 1
        
        # Show current player's cards
        print(colored(f"  Player {player_num}", color))
        print(colored("=" * 18, color))
        print(colored("   Line           ", color))
        print(colored("=" * 88, color))
        line_row = "|| " + " | ".join(f"{i}.{card:<12}" for i, card in enumerate(player.line)) + " ||"
        print(colored(line_row, color))
        print(colored("=" * 88, color))
        print("\n")
        print(colored("   Hand           ", color))
        print(colored("=" * 88, color))
        hand_row = "|| " + " | ".join(f"{i + LINE_SIZE}.{card:<12}" for i, card in enumerate(player.hand)) + " ||"
        print(colored(hand_row, color))
        print(colored("=" * 88, color))
        print("\n")
        
        decree_choice = get_choice(
            f'Player {player_num}, which of your cards do you want to impose a decree on? (0-9)\n',
            list(range(0, 10))
        )
        
        opponent = self.opponent
        if decree_choice < LINE_SIZE:
            # Swap in line
            card1 = player.line[decree_choice]
            card2 = opponent.line[decree_choice]
            player.line[decree_choice], opponent.line[decree_choice] = card2, card1
            self.game_message = colored(
                f"\nPlayer {player_num} swapped {card1} for {card2} at line position {decree_choice}.\n",
                'green'
            )
        else:
            # Swap in hand
            hand_pos = decree_choice - LINE_SIZE
            card1 = player.hand[hand_pos]
            card2 = opponent.hand[hand_pos]
            player.hand[hand_pos], opponent.hand[hand_pos] = card2, card1
            self.game_message = colored(
                f"\nPlayer {player_num} swapped {card1} for {card2} at hand position {hand_pos}.\n",
                'green'
            )
    
    def play(self) -> bool:
        """Execute one turn, return True if game ended"""
        player = self.current_player
        player_num = player.index + 1
        
        # Display messages
        if self.error_message:
            print(self.error_message + '\n')
        if self.game_message:
            print(self.game_message + '\n')
        self.error_message = ''
        self.game_message = ''
        
        # Get action choice
        choice = get_choice(
            f'Player {player_num}, what do you want to do?\n\n'
            '1. Develop your Territory\n'
            '2. Send an Emissary\n'
            '3. Recall your Emissaries\n'
            '4. Impose an Imperial Decree\n'
            '5. Declare the end of the game\n\n',
            [1, 2, 3, 4, 5]
        )
        
        if choice == 1:
            # Develop territory
            self.develop_territory(player)
            
            # Optional emissary action
            if player.emissaries > 0:
                emissary_choice = get_choice(
                    f'Player {player_num}, do you also want to send an Emissary this turn? (1-3)\n'
                    '1. Swap two cards\n'
                    '2. Discard two River cards\n'
                    '3. No, thank you\n',
                    [1, 2, 3]
                )
                
                if emissary_choice == 1:
                    self.swap_cards(player)
                elif emissary_choice == 2:
                    self.discard_river(player)
        
        elif choice == 2:
            # Send emissary
            if player.emissaries == 0:
                self.error_message = colored("\nYou don't have an available emissary\n", 'red')
            else:
                emissary_choice = get_choice(
                    f'Player {player_num}, what do you want to do with this Emissary? (1-2)\n'
                    '1. Swap two cards\n'
                    '2. Discard two River cards\n\n',
                    [1, 2]
                )
                
                if emissary_choice == 1:
                    self.swap_cards(player)
                else:
                    self.discard_river(player)
                
                print('You now need to develop your territory.')
                self.develop_territory(player)
        
        elif choice == 3:
            # Recall emissaries
            self.recall_emissaries(player)
        
        elif choice == 4:
            # Impose decree
            self.impose_decree(player)
        
        elif choice == 5:
            # Declare end
            if self.ending_available:
                self.end_next_turn = True
                self.game_message = colored(f"\nPlayer {player_num} declared the end of the game. Opponent gets one final turn.\n", 'green')
            else:
                self.error_message = colored("\nYou can't end the game yet, no deck is empty\n", 'red')
        
        # Check if game should end
        if self.check_ending():
            return True
        
        # Update state
        self.update_state()
        return False
    
    def check_ending(self) -> bool:
        """Check if game should end"""
        if self.end_next_turn:
            return True
        
        empty_count = self.river.count_empty_decks()
        
        if empty_count >= 1:
            self.ending_available = True
        
        if empty_count >= 2:
            if self.current_player_index == 0:
                self.end_next_turn = True
                return False
            else:
                return True
        
        return False
    
    def update_state(self):
        """Update game state after turn"""
        # Check for ending
        for deck in self.river.decks:
            if not deck:
                self.ending_available = True
        
        # Switch player if no error
        if not self.error_message:
            self.current_player_index = 1 - self.current_player_index
            self.turn_count += 1
    
    def score(self):
        """Calculate and display final scores"""
        player_scores = {}
        
        for player in self.players:
            # Handle ninjas
            def get_ninja_choice(position, cards):
                color = player.color
                print(colored(f"|| Ninja at position {position} ||", color))
                print(colored("   Hand           ", color))
                print(colored("=" * 88, color))
                hand_row = "|| " + " | ".join(f"{j}.{c:<12}" for j, c in enumerate(player.hand)) + " ||"
                print(colored(hand_row, color))
                print(colored("=" * 88, color))
                print("\n")
                print(colored("   Line           ", color))
                print(colored("=" * 88, color))
                line_row = "|| " + " | ".join(f"{j}.{c:<12}" for j, c in enumerate(player.line)) + " ||"
                print(colored(line_row, color))
                print(colored("=" * 88, color))
                print("\n")
                
                return get_choice(
                    f'Player {player.index + 1}, what card do you want the Ninja at position {position} to copy? (0-9)\n',
                    range(0, 10)
                )
            
            cards = player.get_all_cards()
            working_cards = Scorer.handle_ninjas(cards, CHARACTERS, get_ninja_choice)
            score_breakdown = Scorer.calculate_score(working_cards)
            player_scores[player.index] = {
                'breakdown': score_breakdown,
                'cards': working_cards
            }
        
        # Display scores
        self._display_scores(player_scores)
        
        # Determine winner
        score1 = player_scores[0]['breakdown']['Total']
        score2 = player_scores[1]['breakdown']['Total']
        cards1 = player_scores[0]['cards']
        cards2 = player_scores[1]['cards']
        
        winner = Scorer.determine_winner(score1, score2, cards1, cards2)
        
        if winner == 0:
            print(f'\nPlayer 1 Victory {score1} to {score2}!')
        elif winner == 1:
            print(f'\nPlayer 2 Victory {score2} to {score1}!')
        else:
            unique1 = len(set(cards1) - {'Mountain', 'Ninja'})
            unique2 = len(set(cards2) - {'Mountain', 'Ninja'})
            print(f'\nTrue equality, play again! Both players have {score1} points and {unique1} unique cards.')
    
    def _display_scores(self, player_scores):
        """Display score table"""
        color1, color2 = 'magenta', 'yellow'
        
        # Build card list with scores
        card_names = ['Mountain'] + CARDS + ['Total']
        p1_data = [(name, player_scores[0]['breakdown'].get(name, 0)) for name in card_names]
        p2_data = [(name, player_scores[1]['breakdown'].get(name, 0)) for name in card_names]
        
        print(colored("  Player 1       ||", color1) + "  " + colored("  Player 2        ||", color2))
        print(colored("=" * 20, color1) + "  " + colored("=" * 20, color2))
        
        for (card1, score1), (card2, score2) in zip(p1_data, p2_data):
            print(colored(f"|| {card1:<12}   ||", color1) + "  " + colored(f"|| {card2:<12}   ||", color2))
            print(colored(f"|| {score1:<12}   ||", color1) + "  " + colored(f"|| {score2:<12}   ||", color2))
            print(colored("-" * 20, color1) + "  " + colored("-" * 20, color2))
        
        print("\n")