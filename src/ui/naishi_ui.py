# naishi_ui.py
"""Rich terminal UI for Naishi game - works with GameState from naishi_core"""

from termcolor import colored
from naishi_core.game_logic import GameState
from naishi_core.player import Player
from naishi_core.constants import NUM_DECKS, LINE_SIZE, HAND_SIZE, CHARACTERS
from naishi_core.scorer import Scorer
from naishi_core.utils import get_choice


class NaishiUI:
    """Terminal UI for displaying Naishi game state"""
    
    @staticmethod
    def display_river_for_draft(gs: GameState):
        """Display river during initial draft"""
        print("\n")
        print(colored("   River          ", "blue"))
        print(colored("=" * 78, "blue"))
        cards_left = gs.river.cards_left()
        row = "|| " + " | ".join(
            f"{gs.river_tops_at_draft[i] if i < len(gs.river_tops_at_draft) else '':<12}"
            for i in range(NUM_DECKS)
        ) + " ||"
        print(colored(row, "blue"))
        print(colored("="*78, "blue"))
        row = "|| " + " | ".join(f"{cards_left[i]} left      " for i in range(NUM_DECKS)) + " ||"
        print(colored(row, "blue"))
        print(colored("="*78, "blue"))
        print("\n")
    
    @staticmethod
    def show_full_state(gs: GameState):
        """Display full game state"""
        print("\n")
        NaishiUI._show_river(gs)
        print("\n")
        NaishiUI._show_player(gs.players[0], show_hand=(gs.current_player_idx == 0))
        print("\n")
        NaishiUI._show_player(gs.players[1], show_hand=(gs.current_player_idx == 1))
        print("\n")
    
    @staticmethod
    def _show_river(gs: GameState):
        """Display river and emissary tracking"""
        print(colored("   River          ", "blue") + " " * 69 + colored("   Swaps            Discards    ", 'white'))
        print(colored("=" * 78, "blue") + " " * 9 + "=" * 15 + " " * 2 + "=" * 15)
        
        # River cards
        cards_left = gs.river.cards_left()
        row = "|| " + " | ".join(
            f"{gs.river.get_top_card(i) or '':<12}"
            for i in range(NUM_DECKS)
        ) + " ||"
        
        # Swap markers
        row += " "*9 + colored("|| ", 'white')
        for i, spot in enumerate(gs.available_swaps):
            if spot == 1:
                row += colored("X", "magenta")
            elif spot == 2:
                row += colored("O", "yellow")
            else:
                row += " "
            row += colored(" | " if i != 2 else " ||  ||  ", 'white')
        
        # Discard markers
        for i, spot in enumerate(gs.available_discards):
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
        if gs.players[0].decree_used:
            row += colored("X", "magenta")
        elif gs.players[1].decree_used:
            row += colored("O", "yellow")
        else:
            row += " "
        row += "  ||"
        print(colored(row, "blue"))
        print(colored("="*78, "blue") + " " * 9 + "=" * 25)
    
    @staticmethod
    def _show_player(player: Player, show_hand: bool):
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
    
    @staticmethod
    def show_player_cards_with_indices(player: Player, gs: GameState):
        """Show player cards with position indices for selection"""
        color = player.color
        player_num = player.index + 1
        
        # Show river
        print("\n")
        print(colored("   River          ", "blue"))
        print(colored("=" * 78, "blue"))
        row = "|| " + " | ".join(
            f"{gs.river.get_top_card(i) or '':<12}"
            for i in range(NUM_DECKS)
        ) + " ||"
        print(colored(row, "blue"))
        print(colored("="*78, "blue"))
        cards_left = gs.river.cards_left()
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
    
    @staticmethod
    def show_river_with_indices(gs: GameState):
        """Show river with deck indices"""
        print("\n")
        print(colored("   River          ", "blue"))
        print(colored("=" * 78, "blue"))
        cards_left = gs.river.cards_left()
        row = "|| " + " | ".join(
            f"{gs.river.get_top_card(i) or '':<12}"
            for i in range(NUM_DECKS)
        ) + " ||"
        print(colored(row, "blue"))
        print(colored("="*78, "blue"))
        row = "|| " + " | ".join(f"{i+1}.{cards_left[i]} left   " for i in range(NUM_DECKS)) + " ||"
        print(colored(row, "blue"))
        print(colored("="*78, "blue"))
        print("\n")
    
    @staticmethod
    def show_hand_or_line_with_indices(player: Player, location: str):
        """Show just hand or line with indices"""
        color = player.color
        cards = player.hand if location == 'hand' else player.line
        title = "   Hand           " if location == 'hand' else "   Line           "
        
        print(colored(title, color))
        print(colored("=" * 88, color))
        if location == 'hand':
            row = "|| " + " | ".join(f"{i + 1}.{card:<12}" for i, card in enumerate(cards)) + " ||"
        else:
            row = "|| " + " | ".join(f"{i + 1}.{card:<12}" for i, card in enumerate(cards)) + " ||"
        print(colored(row, color))
        print(colored("=" * 88, color))
        print("\n")
    
    @staticmethod
    def show_both_hand_and_line_with_indices(player: Player):
        """Show both hand and line with indices"""
        color = player.color
        
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
    
    @staticmethod
    def display_final_scores(gs: GameState, get_ninja_choice_func=None):
        """Calculate and display final scores"""
        from naishi_core.constants import CARDS
        
        player_scores = {}
        
        for player in gs.players:
            # Handle ninjas
            def default_ninja_choice(position, cards):
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
            
            ninja_func = get_ninja_choice_func or default_ninja_choice
            cards = player.get_all_cards()
            working_cards = Scorer.handle_ninjas(cards, CHARACTERS, ninja_func)
            score_breakdown = Scorer.calculate_score(working_cards)
            player_scores[player.index] = {
                'breakdown': score_breakdown,
                'cards': working_cards
            }
        
        # Display scores
        NaishiUI._display_score_table(player_scores)
        
        # Determine winner
        score1 = player_scores[0]['breakdown']['Total']
        score2 = player_scores[1]['breakdown']['Total']
        cards1 = player_scores[0]['cards']
        cards2 = player_scores[1]['cards']
        
        winner = Scorer.determine_winner(score1, score2, cards1, cards2)
        
        if winner == 0:
            print(colored(f'\n🏆 Player 1 Victory {score1} to {score2}!', 'magenta', attrs=['bold']))
        elif winner == 1:
            print(colored(f'\n🏆 Player 2 Victory {score2} to {score1}!', 'yellow', attrs=['bold']))
        else:
            unique1 = len(set(cards1) - {'Mountain', 'Ninja'})
            unique2 = len(set(cards2) - {'Mountain', 'Ninja'})
            print(colored(f'\n🤝 True equality, play again! Both players have {score1} points and {unique1} unique cards.', 'cyan', attrs=['bold']))
        
        return winner, score1, score2
    
    @staticmethod
    def _display_score_table(player_scores):
        """Display score table"""
        from naishi_core.constants import CARDS
        
        color1, color2 = 'magenta', 'yellow'
        
        # Build card list with scores
        card_names = ['Mountain'] + CARDS + ['Total']
        p1_data = [(name, player_scores[0]['breakdown'].get(name, 0)) for name in card_names]
        p2_data = [(name, player_scores[1]['breakdown'].get(name, 0)) for name in card_names]
        
        print("\n")
        print(colored("  Player 1       ||", color1) + "  " + colored("  Player 2        ||", color2))
        print(colored("=" * 20, color1) + "  " + colored("=" * 20, color2))
        
        for (card1, score1), (card2, score2) in zip(p1_data, p2_data):
            print(colored(f"|| {card1:<12}   ||", color1) + "  " + colored(f"|| {card2:<12}   ||", color2))
            print(colored(f"|| {score1:<12}   ||", color1) + "  " + colored(f"|| {score2:<12}   ||", color2))
            print(colored("-" * 20, color1) + "  " + colored("-" * 20, color2))
        
        print("\n")
