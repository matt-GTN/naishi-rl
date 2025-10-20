# naishi_pvp.py
"""Human vs Human play - delegates all logic to naishi_core.GameState"""

from termcolor import colored
from src.ui.banner import print_banner
from src.ui.naishi_ui import NaishiUI
from naishi_core.game_logic import (
    GameState,
    ACTION_DRAFT, ACTION_DEVELOP, ACTION_SWAP,
    ACTION_DISCARD, ACTION_RECALL, ACTION_DECREE, ACTION_END_GAME,
)
from naishi_core.constants import LINE_SIZE, NUM_DECKS
from naishi_core.utils import get_choice


class NaishiPvP:
    """Console 2-player PvP - pure UI wrapper around GameState"""

    def __init__(self, seed=None):
        print("\n")
        print_banner()
        print("\n\n")
        self.gs = GameState.create_initial_state(seed)
        
        # Handle draft phase
        self._handle_draft()
    
    def _handle_draft(self):
        """Handle the draft phase"""
        NaishiUI.display_river_for_draft(self.gs)
        
        # Player 1 draft choice
        p1_hand = self.gs.draft_hands[0]
        p1_choice = get_choice(
            f'Player 1 - What card do you want to give to your opponent? (1/2)\n\n1. {p1_hand[0]}\n2. {p1_hand[1]}\n\n',
            [1, 2]
        )
        
        # Player 2 draft choice
        p2_hand = self.gs.draft_hands[1]
        p2_choice = get_choice(
            f'Player 2 - What card do you want to give to your opponent? (1/2)\n\n1. {p2_hand[0]}\n2. {p2_hand[1]}\n\n',
            [1, 2]
        )
        
        # Complete draft in GameState
        self.gs._complete_draft(p1_choice - 1, p2_choice - 1)

    def play(self):
        """Main game loop - delegates all logic to GameState"""
        while True:
            # Display game state
            NaishiUI.show_full_state(self.gs)
            
            # Get action from current player
            action_array = self._get_player_action()
            
            # Apply action through GameState (single source of truth!)
            obs, reward, terminated, truncated, info = self.gs.apply_action_array(action_array)
            
            # Check if game ended
            if terminated or truncated:
                break
            
            # RULES.md Section 4: Query GameState for turn state (Option A - optional emissary after develop)
            if self.gs.optional_emissary_available:
                if self._offer_optional_emissary():
                    # Player chose to use emissary, get another action
                    emissary_action = self._get_player_action()
                    obs, reward, terminated, truncated, info = self.gs.apply_action_array(emissary_action)
                    if terminated or truncated:
                        break
                else:
                    # Player declined optional emissary, skip and end turn
                    obs, reward, terminated, truncated, info = self.gs.skip_optional_emissary()
                    if terminated or truncated:
                        break
            
            # RULES.md Section 4: Query GameState for turn state (Option B - required develop after emissary)
            if self.gs.must_develop:
                print(colored("\nYou must develop your territory after using an emissary!", 'yellow', attrs=['bold']))
                develop_action = self._get_player_action()
                obs, reward, terminated, truncated, info = self.gs.apply_action_array(develop_action)
                if terminated or truncated:
                    break
        
        # Game over - show final scores
        NaishiUI.show_full_state(self.gs)
        print("\n" + colored("=" * 60, 'cyan'))
        print(colored("GAME OVER - Final Scoring", 'cyan', attrs=['bold']))
        print(colored("=" * 60, 'cyan') + "\n")
        NaishiUI.display_final_scores(self.gs)
    
    def _offer_optional_emissary(self):
        """Ask if player wants to use an emissary after developing. Returns True if yes."""
        player_num = self.gs.current_player_idx + 1
        
        # Pure UI: just ask the player, GameState already validated this is available
        choice = get_choice(
            f"Player {player_num}, do you want to use an Emissary this turn? (1-3)\n"
            "1. Yes - Swap Cards\n"
            "2. Yes - Discard River Cards\n"
            "3. No, end turn\n",
            [1, 2, 3]
        )
        
        return choice in [1, 2]
    
    def _get_player_action(self):
        """Get action from current player using UI helpers"""
        player = self.gs.players[self.gs.current_player_idx]
        player_num = player.index + 1
        
        # Show legal actions
        legal_types = self.gs.get_legal_action_types()
        
        # Build menu
        menu_options = []
        menu_map = {}
        option_num = 1
        
        if ACTION_DEVELOP in legal_types:
            menu_options.append(f"{option_num}. Develop your Territory")
            menu_map[option_num] = ACTION_DEVELOP
            option_num += 1
        
        if ACTION_SWAP in legal_types:
            menu_options.append(f"{option_num}. Swap Cards (Emissary)")
            menu_map[option_num] = ACTION_SWAP
            option_num += 1
        
        if ACTION_DISCARD in legal_types:
            menu_options.append(f"{option_num}. Discard River Cards (Emissary)")
            menu_map[option_num] = ACTION_DISCARD
            option_num += 1
        
        if ACTION_RECALL in legal_types:
            menu_options.append(f"{option_num}. Recall your Emissaries")
            menu_map[option_num] = ACTION_RECALL
            option_num += 1
        
        if ACTION_DECREE in legal_types:
            menu_options.append(f"{option_num}. Impose an Imperial Decree")
            menu_map[option_num] = ACTION_DECREE
            option_num += 1
        
        if ACTION_END_GAME in legal_types:
            menu_options.append(f"{option_num}. Declare the end of the game")
            menu_map[option_num] = ACTION_END_GAME
            option_num += 1
        
        # Get choice
        menu_text = f"Player {player_num}, what do you want to do?\n\n" + "\n".join(menu_options) + "\n\n"
        choice = get_choice(menu_text, list(menu_map.keys()))
        action_type = menu_map[choice]
        
        # Build action array based on type
        action_array = [0] * 8
        action_array[0] = action_type
        
        if action_type == ACTION_DEVELOP:
            NaishiUI.show_player_cards_with_indices(player, self.gs)
            pos = get_choice(f"Player {player_num}, which card do you want to discard? (0-9)\n", list(range(10)))
            action_array[1] = pos
        
        elif action_type == ACTION_SWAP:
            swap_type = get_choice(
                f"Player {player_num}, where do you want to swap cards? (1-4)\n"
                "1. Hand\n2. Line\n3. Between Hand and Line\n4. River\n",
                [1, 2, 3, 4]
            ) - 1
            action_array[3] = swap_type
            
            if swap_type in [0, 1]:  # hand or line
                NaishiUI.show_hand_or_line_with_indices(player, 'hand' if swap_type == 0 else 'line')
                pos1 = get_choice(f"Player {player_num}, pick first card (1-5)\n", [1, 2, 3, 4, 5]) - 1
                pos2 = get_choice(f"Player {player_num}, pick second card (1-5)\n", [1, 2, 3, 4, 5]) - 1
                action_array[4] = pos1
                action_array[5] = pos2
            elif swap_type == 2:  # between
                NaishiUI.show_both_hand_and_line_with_indices(player)
                pos = get_choice(f"Player {player_num}, pick position to swap (1-5)\n", [1, 2, 3, 4, 5]) - 1
                action_array[4] = pos
            elif swap_type == 3:  # river
                NaishiUI.show_river_with_indices(self.gs)
                deck1 = get_choice(f"Player {player_num}, pick first deck (1-5)\n", [1, 2, 3, 4, 5]) - 1
                deck2 = get_choice(f"Player {player_num}, pick second deck (1-5)\n", [1, 2, 3, 4, 5]) - 1
                action_array[4] = deck1
                action_array[5] = deck2
        
        elif action_type == ACTION_DISCARD:
            NaishiUI.show_river_with_indices(self.gs)
            deck1 = get_choice(f"Player {player_num}, which first card to discard? (1-5)\n", [1, 2, 3, 4, 5]) - 1
            deck2 = get_choice(f"Player {player_num}, which second card to discard? (1-5)\n", [1, 2, 3, 4, 5]) - 1
            action_array[6] = deck1
            action_array[7] = deck2
        
        elif action_type == ACTION_DECREE:
            NaishiUI.show_player_cards_with_indices(player, self.gs)
            pos = get_choice(f"Player {player_num}, which card to impose decree on? (0-9)\n", list(range(10)))
            action_array[1] = pos
        
        # RECALL and END_GAME need no parameters
        
        return action_array


if __name__ == "__main__":
    game = NaishiPvP()
    game.play()
