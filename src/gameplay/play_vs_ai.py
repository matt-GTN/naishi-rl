# play_vs_ai.py
"""Human vs AI play - delegates all logic to naishi_core.GameState"""

import random as r
from termcolor import colored
from src.ui.banner import print_banner
from src.ui.naishi_ui import NaishiUI
from naishi_core.game_logic import (
    GameState,
    ACTION_DRAFT, ACTION_DEVELOP, ACTION_SWAP, ACTION_DISCARD,
    ACTION_RECALL, ACTION_DECREE, ACTION_END_GAME
)
from naishi_core.constants import LINE_SIZE, NUM_DECKS
from naishi_core.utils import get_choice


class PlayVsAI:
    """CLI Human vs AI interface - pure UI wrapper around GameState"""

    def __init__(self, ai_policy=None, seed=None):
        print("\n")
        print_banner()
        print("\n\n")
        self.gs = GameState.create_initial_state(seed)
        self.ai_policy = ai_policy or self.random_policy
        
        # Handle draft phase
        self._handle_draft()

    def random_policy(self, obs, gs):
        """Random legal move."""
        legal = gs.get_legal_action_types()
        a_type = r.choice(legal)
        arr = [0] * 8
        arr[0] = a_type
        
        # Fill in random parameters
        if a_type == ACTION_DEVELOP:
            available_positions = [i for i in range(10) if not gs.river.is_empty(i % NUM_DECKS)]
            if available_positions:
                arr[1] = r.choice(available_positions)
        elif a_type == ACTION_SWAP:
            arr[3] = r.randint(0, 3)
            arr[4] = r.randint(0, 4)
            arr[5] = r.randint(0, 4)
        elif a_type == ACTION_DISCARD:
            arr[6] = r.randint(0, 4)
            arr[7] = r.randint(0, 4)
        elif a_type == ACTION_DECREE:
            arr[1] = r.randint(0, 9)
        
        return arr
    
    def _handle_draft(self):
        """Handle the draft phase"""
        NaishiUI.display_river_for_draft(self.gs)
        
        # Human player draft choice
        p1_hand = self.gs.draft_hands[0]
        p1_choice = get_choice(
            f'Player 1 (You) - What card do you want to give to your opponent? (1/2)\n\n1. {p1_hand[0]}\n2. {p1_hand[1]}\n\n',
            [1, 2]
        )
        
        # AI player draft choice
        p2_choice = r.choice([1, 2])
        print(colored(f"Player 2 (AI) chooses to give card #{p2_choice}", "yellow"))
        
        # Complete draft in GameState
        self.gs._complete_draft(p1_choice - 1, p2_choice - 1)

    def play(self):
        """Main game loop - delegates all logic to GameState"""
        while True:
            # Display game state
            NaishiUI.show_full_state(self.gs)
            
            player = self.gs.players[self.gs.current_player_idx]
            pidx = self.gs.current_player_idx
            
            if pidx == 0:
                # Human turn - get action from user
                action_array = self._get_human_action()
            else:
                # AI turn
                print(colored("\n🤖 AI is thinking...\n", "yellow"))
                action_array = self.ai_policy(self.gs.get_observation(), self.gs)
                
                action_names = ['Draft', 'Develop', 'Swap', 'Discard', 'Recall', 'Decree', 'End Game']
                action_name = action_names[action_array[0]] if action_array[0] < len(action_names) else 'Unknown'
                print(colored(f"AI chose: {action_name}", "yellow"))
            
            # Apply action through GameState (single source of truth!)
            obs, reward, terminated, truncated, info = self.gs.apply_action_array(action_array)
            
            # Check if game ended
            if terminated or truncated:
                break
            
            # RULES.md Section 4: Query GameState for turn state (Option A - optional emissary after develop)
            if self.gs.optional_emissary_available:
                if pidx == 0:
                    # Human player - ask if they want to use optional emissary
                    if self._offer_optional_emissary():
                        # Player chose to use emissary, get another action
                        emissary_action = self._get_human_action()
                        obs, reward, terminated, truncated, info = self.gs.apply_action_array(emissary_action)
                        if terminated or truncated:
                            break
                    else:
                        # Player declined optional emissary, skip and end turn
                        obs, reward, terminated, truncated, info = self.gs.skip_optional_emissary()
                        if terminated or truncated:
                            break
                else:
                    # AI player - let AI decide
                    print(colored("AI considers using an emissary...", "yellow"))
                    ai_action = self.ai_policy(self.gs.get_observation(), self.gs)
                    
                    # Check if AI chose an emissary action
                    if ai_action[0] in [ACTION_SWAP, ACTION_DISCARD]:
                        action_names = ['Draft', 'Develop', 'Swap', 'Discard', 'Recall', 'Decree', 'End Game']
                        action_name = action_names[ai_action[0]]
                        print(colored(f"AI chose: {action_name}", "yellow"))
                        obs, reward, terminated, truncated, info = self.gs.apply_action_array(ai_action)
                        if terminated or truncated:
                            break
                    else:
                        # AI declined optional emissary, skip and end turn
                        print(colored("AI chose not to use an emissary", "yellow"))
                        obs, reward, terminated, truncated, info = self.gs.skip_optional_emissary()
                        if terminated or truncated:
                            break
            
            # RULES.md Section 4: Query GameState for turn state (Option B - required develop after emissary)
            if self.gs.must_develop:
                if pidx == 0:
                    # Human player - require develop
                    print(colored("\nYou must develop your territory after using an emissary!", 'yellow', attrs=['bold']))
                    develop_action = self._get_human_action()
                    obs, reward, terminated, truncated, info = self.gs.apply_action_array(develop_action)
                    if terminated or truncated:
                        break
                else:
                    # AI player - require develop
                    print(colored("AI must develop after using an emissary...", "yellow"))
                    ai_action = self.ai_policy(self.gs.get_observation(), self.gs)
                    action_names = ['Draft', 'Develop', 'Swap', 'Discard', 'Recall', 'Decree', 'End Game']
                    action_name = action_names[ai_action[0]]
                    print(colored(f"AI chose: {action_name}", "yellow"))
                    obs, reward, terminated, truncated, info = self.gs.apply_action_array(ai_action)
                    if terminated or truncated:
                        break
        
        # Game over - show final scores
        NaishiUI.show_full_state(self.gs)
        print("\n" + colored("=" * 60, 'cyan'))
        print(colored("GAME OVER - Final Scoring", 'cyan', attrs=['bold']))
        print(colored("=" * 60, 'cyan') + "\n")
        
        # For AI ninja choices, use random
        def ai_ninja_choice(position, cards):
            import random
            valid_chars = [i for i, c in enumerate(cards) if c in ['Naishi', 'Councellor', 'Sentinel', 'Monk', 'Knight', 'Ronin'] and c != 'Ninja']
            return random.choice(valid_chars) if valid_chars else 0
        
        winner, score1, score2 = NaishiUI.display_final_scores(self.gs, get_ninja_choice_func=ai_ninja_choice)
        
        if winner == 0:
            print(colored("\n🎉 Congratulations! You won!", 'green', attrs=['bold']))
        elif winner == 1:
            print(colored("\n😔 The AI won this time. Better luck next time!", 'red', attrs=['bold']))
    
    def _offer_optional_emissary(self):
        """Ask if player wants to use an emissary after developing. Returns True if yes."""
        # Pure delegation - GameState already validated optional_emissary_available
        # No game logic checks here, just UI presentation
        choice = get_choice(
            "Do you want to use an Emissary this turn? (1-3)\n"
            "1. Yes - Swap Cards\n"
            "2. Yes - Discard River Cards\n"
            "3. No, end turn\n",
            [1, 2, 3]
        )
        
        return choice in [1, 2]
    
    def _get_human_action(self):
        """Get action from human player using UI helpers"""
        player = self.gs.players[0]
        
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
        menu_text = "Player 1 (You), what do you want to do?\n\n" + "\n".join(menu_options) + "\n\n"
        choice = get_choice(menu_text, list(menu_map.keys()))
        action_type = menu_map[choice]
        
        # Build action array based on type
        action_array = [0] * 8
        action_array[0] = action_type
        
        if action_type == ACTION_DEVELOP:
            NaishiUI.show_player_cards_with_indices(player, self.gs)
            pos = get_choice("Which card do you want to discard? (0-9)\n", list(range(10)))
            action_array[1] = pos
        
        elif action_type == ACTION_SWAP:
            swap_type = get_choice(
                "Where do you want to swap cards? (1-4)\n"
                "1. Hand\n2. Line\n3. Between Hand and Line\n4. River\n",
                [1, 2, 3, 4]
            ) - 1
            action_array[3] = swap_type
            
            if swap_type in [0, 1]:  # hand or line
                NaishiUI.show_hand_or_line_with_indices(player, 'hand' if swap_type == 0 else 'line')
                pos1 = get_choice("Pick first card (1-5)\n", [1, 2, 3, 4, 5]) - 1
                pos2 = get_choice("Pick second card (1-5)\n", [1, 2, 3, 4, 5]) - 1
                action_array[4] = pos1
                action_array[5] = pos2
            elif swap_type == 2:  # between
                NaishiUI.show_both_hand_and_line_with_indices(player)
                pos = get_choice("Pick position to swap (1-5)\n", [1, 2, 3, 4, 5]) - 1
                action_array[4] = pos
            elif swap_type == 3:  # river
                NaishiUI.show_river_with_indices(self.gs)
                deck1 = get_choice("Pick first deck (1-5)\n", [1, 2, 3, 4, 5]) - 1
                deck2 = get_choice("Pick second deck (1-5)\n", [1, 2, 3, 4, 5]) - 1
                action_array[4] = deck1
                action_array[5] = deck2
        
        elif action_type == ACTION_DISCARD:
            NaishiUI.show_river_with_indices(self.gs)
            deck1 = get_choice("Which first card to discard? (1-5)\n", [1, 2, 3, 4, 5]) - 1
            deck2 = get_choice("Which second card to discard? (1-5)\n", [1, 2, 3, 4, 5]) - 1
            action_array[6] = deck1
            action_array[7] = deck2
        
        elif action_type == ACTION_DECREE:
            NaishiUI.show_player_cards_with_indices(player, self.gs)
            pos = get_choice("Which card to impose decree on? (0-9)\n", list(range(10)))
            action_array[1] = pos
        
        # RECALL and END_GAME need no parameters
        
        return action_array


if __name__ == "__main__":
    import os
    
    # Try to load trained model if available
    model_path = "models/naishi_model.zip"
    ai_policy = None
    
    if os.path.exists(model_path):
        print(colored("Loading trained AI model...", "cyan"))
        try:
            from sb3_contrib import MaskablePPO
            model = MaskablePPO.load(model_path[:-4])
            
            class ModelPolicy:
                def __init__(self, model):
                    self.model = model
                
                def __call__(self, obs, gs):
                    from naishi_env import NaishiEnv
                    temp_env = NaishiEnv()
                    temp_env.gs = gs
                    action_mask = temp_env._get_action_mask()
                    action, _ = self.model.predict(obs, deterministic=False, action_masks=action_mask)
                    return action
            
            ai_policy = ModelPolicy(model)
            print(colored("✓ Trained AI loaded successfully!\n", "green"))
        except Exception as e:
            print(colored(f"⚠ Could not load model: {e}", "yellow"))
            print(colored("Using random AI instead...\n", "yellow"))
    else:
        print(colored("No trained model found. Using random AI...\n", "yellow"))
    
    game = PlayVsAI(ai_policy=ai_policy)
    game.play()
