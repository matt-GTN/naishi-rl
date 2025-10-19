# play_vs_ai.py
"""
Play a game of Naishi against a fully-featured AI that uses a unified model
for both draft phase and main game decisions.
"""
import random as r
import numpy as np
from stable_baselines3 import PPO
from termcolor import colored

# --- Local Imports ---
from banner import print_banner
from naishi_pvp import GameState
from naishi_core import get_choice, LINE_SIZE, HAND_SIZE, CARD_TO_INT, NUM_DECKS, CARDS, CARDS_COUNT
from policies import MaskedRandomPolicy

# Action constants are only needed for logging the AI's moves
from naishi_env import ACTION_DRAFT, ACTION_DEVELOP, ACTION_SWAP, ACTION_DISCARD, ACTION_RECALL, ACTION_DECREE, ACTION_END_GAME

# --- AI Action Functions ---

def get_ai_draft_choice(model, hand: list, river_tops: list) -> int:
    """
    Uses the trained model to decide which card to give away during draft.
    Returns the choice (1 or 2).
    """
    print(colored("AI is analyzing the draft...", "yellow"))
    
    # Create draft phase observation
    encode = lambda card: CARD_TO_INT.get(card, CARD_TO_INT['Empty'])
    
    obs = [
        # Line (all Mountains during draft)
        *[encode('Mountain')] * LINE_SIZE,
        # Draft hand (2 cards, padded to 5)
        encode(hand[0]), encode(hand[1]),
        *[encode('Empty')] * 3,
        # Opponent line (all Mountains)
        *[encode('Mountain')] * LINE_SIZE,
        # Opponent hand (hidden)
        *[encode('Empty')] * HAND_SIZE,
        # River tops
        *[encode(card) for card in river_tops],
        # River counts (all 6)
        6, 6, 6, 6, 6,
        # Emissaries
        2, 2,
        # Decree flags
        0, 0,
        # Turn count
        0.0,
        # Flags
        0, 0, 1, 1,
        # In draft phase
        1,
    ]
    obs = np.array(obs, dtype=np.float32)
    
    # Get the model's prediction
    action, _ = model.predict(obs, deterministic=True)
    
    # Extract choice from action (use position parameter)
    choice = (action[1] % 2) + 1
    
    print(colored(f"AI decides to give away card #{choice}: '{hand[choice-1]}'", "yellow"))
    return choice


def get_ai_game_action(model, game_state: GameState):
    """
    Uses the trained model to decide the in-game turn action.
    """
    ai_player = game_state.players[1]
    human_player = game_state.players[0]
    encode = lambda card: CARD_TO_INT.get(card, CARD_TO_INT['Empty'])
    
    # Create the full observation for the main game (must match naishi_env.py observation)
    obs = [
        *[encode(c) for c in ai_player.line],
        *[encode(c) for c in ai_player.hand],
        *[encode(c) for c in human_player.line],
        *[encode('Empty')] * HAND_SIZE,  # Opponent hand (always hidden, padded for consistency)
        *[encode(game_state.river.get_top_card(i) or 'Empty') for i in range(NUM_DECKS)],
        *game_state.river.cards_left(),
        ai_player.emissaries,
        human_player.emissaries,
        int(ai_player.decree_used),
        int(human_player.decree_used),
        min(game_state.turn_count / 50.0, 1.0),
        int(False),  # must_develop
        int(game_state.ending_available),
        int(0 in game_state.available_swaps),  # swap spots available
        int(0 in game_state.available_discards),  # discard spots available
        0,  # not in draft phase
    ]
    obs = np.array(obs, dtype=np.float32)
    
    # Note: Standard PPO doesn't support action masks during prediction.
    # The model learns which actions are legal through reward penalties during training.
    # If the model attempts illegal actions, they are caught and penalized in the action
    # execution code below (e.g., "AI illegally tried to recall").
    # 
    # For a model that respects action masks at inference time, use MaskablePPO from
    # sb3-contrib instead of standard PPO.
    
    action, _ = model.predict(obs, deterministic=True)
    return action

# --- Main Game Execution ---

def main():
    """Main game loop for Human vs. the AI."""
    
    # Load the unified model
    print("Loading AI model...")
    try:
        model = PPO.load("models/naishi_model")
    except FileNotFoundError as e:
        print(colored(f"ERROR: Could not load model file: {e}", "red"))
        print(colored("Make sure you have trained the model first:", "yellow"))
        print(colored("  python train_main_agent.py", "yellow"))
        print(colored("Please ensure 'naishi_model.zip' is present.", "red"))
        return

    # 2. Manual Game Setup
    print_banner()
    game = GameState()
    human_player_idx = 0
    ai_player_idx = 1

    total_cards = []
    for card, count in zip(CARDS, CARDS_COUNT): total_cards.extend([card] * count)
    r.shuffle(total_cards)

    river_tops = []
    for i in range(NUM_DECKS):
        game.river.decks[i] = total_cards[i*6:(i+1)*6]
        river_tops.append(game.river.get_top_card(i))

    player_hands = [total_cards[-2:], total_cards[-4:-2]]
    game._display_river_for_draft()

    # 3. Perform the exchange using the unified model
    p1_choice = get_choice(
        f'Player 1 - What card do you want to give away? (1/2)\n\n1. {player_hands[0][0]}\n2. {player_hands[0][1]}\n\n', [1, 2]
    )
    p2_choice = get_ai_draft_choice(model, player_hands[ai_player_idx], river_tops)
    
    p1_idx, p2_idx = p1_choice - 1, p2_choice - 1
    player_hands[0][p1_idx], player_hands[1][p2_idx] = player_hands[1][p2_idx], player_hands[0][p1_idx]

    # 4. Finalize setup
    for hand in player_hands:
        hand.extend(['Mountain'] * 3)
        r.shuffle(hand)
    for i, player in enumerate(game.players):
        player.hand, player.line = player_hands[i], ['Mountain'] * LINE_SIZE

    print(colored("\nSetup complete. The game begins!", "green"))
    game.show()

    # 5. Main Game Loop
    end = False
    while not end:
        current_player_idx = game.current_player_index
        
        if current_player_idx == human_player_idx:
            print(colored("\nYour turn.", "cyan"))
            end = game.play()
        else:
            print(colored("\nAI is thinking...", "yellow"))
            ai_turn_done = False
            must_develop = False
            
            while not ai_turn_done and not end:
                # Use the unified model for in-game actions
                action = get_ai_game_action(model, game)
                action_type = action[0]

                # Validate action sequence: if must_develop, only DEVELOP is allowed
                if must_develop and action_type != ACTION_DEVELOP:
                    print(colored("AI made an invalid move sequence (must develop after emissary).", "red"))
                    ai_turn_done = True
                    continue
                
                # ACTION_DEVELOP: Replace a card with one from the river
                if action_type == ACTION_DEVELOP:
                    discard_pos, deck_idx = action[1], action[2]
                    location, pos = ('line', discard_pos) if discard_pos < LINE_SIZE else ('hand', discard_pos - LINE_SIZE)
                    
                    # Validate: River deck must not be empty
                    if not game.river.is_empty(deck_idx):
                        card_to_replace = getattr(game.players[ai_player_idx], location)[pos]
                        new_card = game.river.draw_card(deck_idx)
                        game.players[ai_player_idx].replace_card(location, pos, new_card)
                        print(colored(f"AI develops, replacing '{card_to_replace}' with '{new_card}'.", "yellow"))
                    else:
                        print(colored("AI illegally tried to develop from an empty deck.", "red"))
                    
                    ai_turn_done = True
                    must_develop = False
                
                # ACTION_SWAP: Send emissary to swap cards
                elif action_type == ACTION_SWAP:
                    # Validate: Must have at least 1 emissary AND swap spots must be available
                    if game.players[ai_player_idx].emissaries > 0 and 0 in game.available_swaps:
                        game.players[ai_player_idx].use_emissary()
                        print(colored("AI sends an emissary to SWAP.", "yellow"))
                        must_develop = True
                    else:
                        if game.players[ai_player_idx].emissaries == 0:
                            print(colored("AI illegally tried to swap (no emissaries).", "red"))
                        else:
                            print(colored("AI illegally tried to swap (no swap spots available).", "red"))
                        ai_turn_done = True
                
                # ACTION_DISCARD: Send emissary to discard river cards
                elif action_type == ACTION_DISCARD:
                    # Validate: Must have at least 1 emissary AND discard spots must be available
                    if game.players[ai_player_idx].emissaries > 0 and 0 in game.available_discards:
                        game.players[ai_player_idx].use_emissary()
                        deck1, deck2 = action[6], action[7]
                        
                        # Validate: Must choose 2 different decks
                        if deck1 != deck2:
                            game.river.discard_top_cards(deck1, deck2)
                            print(colored(f"AI sends emissary to DISCARD from decks {deck1+1} and {deck2+1}.", "yellow"))
                        else:
                            print(colored("AI illegally tried to discard from same deck twice.", "red"))
                        
                        must_develop = True
                    else:
                        if game.players[ai_player_idx].emissaries == 0:
                            print(colored("AI illegally tried to discard (no emissaries).", "red"))
                        else:
                            print(colored("AI illegally tried to discard (no discard spots available).", "red"))
                        ai_turn_done = True
                
                # ACTION_RECALL: Recall emissaries
                elif action_type == ACTION_RECALL:
                    # Validate: Can only recall if you have fewer than your maximum
                    max_emissaries = 1 if game.players[ai_player_idx].decree_used else 2
                    if game.players[ai_player_idx].emissaries < max_emissaries:
                        game.players[ai_player_idx].recall_emissaries(game.players[ai_player_idx].decree_used)
                        print(colored("AI recalls emissaries.", "yellow"))
                    else:
                        print(colored("AI illegally tried to recall (already at maximum).", "red"))
                    ai_turn_done = True
                
                # ACTION_DECREE: Impose Imperial Decree
                elif action_type == ACTION_DECREE:
                    # Validate: Requires 1 emissary AND can only be used once per game
                    if game.players[ai_player_idx].emissaries > 0 and not game.players[0].decree_used and not game.players[1].decree_used:
                        game.players[ai_player_idx].use_emissary()
                        game.players[ai_player_idx].decree_used = True
                        print(colored("AI imposes the Imperial Decree.", "yellow"))
                    else:
                        if game.players[ai_player_idx].emissaries == 0:
                            print(colored("AI illegally tried to use decree (no emissaries).", "red"))
                        else:
                            print(colored("AI illegally tried to use decree (already used).", "red"))
                    ai_turn_done = True
                
                # ACTION_END_GAME: Declare end of game
                elif action_type == ACTION_END_GAME:
                    # Validate: At least 1 river deck must be empty
                    if game.ending_available:
                        print(colored("AI declares the end of the game!", "green"))
                        end = True
                    else:
                        print(colored("AI illegally tried to end the game (no decks empty).", "red"))
                    ai_turn_done = True
                
                # Unknown action type
                else:
                    print(colored(f"AI attempted unknown action type: {action_type}", "red"))
                    ai_turn_done = True
            
            if not end: end = game.check_ending()
            game.update_state()

        if not end: game.show()

    print(colored("\n--- GAME OVER ---", "green"))
    
    # Custom scoring that handles AI's Ninja strategically
    from naishi_core import Scorer, CHARACTERS
    
    def get_ai_ninja_choice(position, cards, model, game_state):
        """
        AI uses its model to strategically choose which character to copy.
        Evaluates each valid option and picks the one that maximizes score.
        """
        valid_characters = [(i, c) for i, c in enumerate(cards) if c in CHARACTERS and c != 'Ninja']
        
        if not valid_characters:
            print(colored(f"AI's Ninja at position {position} has no valid characters to copy.", "yellow"))
            return 0
        
        print(colored(f"\nAI is deciding what to copy with Ninja at position {position}...", "yellow"))
        
        # Evaluate each option by calculating the resulting score
        best_choice = None
        best_score = float('-inf')
        
        for choice_idx, choice_card in valid_characters:
            # Create a test version with this ninja choice
            test_cards = cards.copy()
            test_cards[position] = choice_card
            
            # Calculate score with this choice
            test_score = Scorer.calculate_score(test_cards)['Total']
            
            if test_score > best_score:
                best_score = test_score
                best_choice = (choice_idx, choice_card)
        
        choice_idx, choice_card = best_choice
        print(colored(f"AI's Ninja at position {position} copies {choice_card} at position {choice_idx} (score: {best_score}).", "yellow"))
        return choice_idx
    
    player_scores = {}
    
    for player in game.players:
        # Handle ninjas
        if player.index == 0:  # Human player
            def get_ninja_choice(position, cards):
                color = player.color
                print(colored(f"|| Ninja at position {position} ||", color))
                print(colored("   Hand           ", color))
                print(colored("=" * 88, color))
                for i in range(5):
                    print(colored(f"|| {i}.{cards[i]:<14} ", color), end='')
                print(colored("||", color))
                print(colored("=" * 88, color))
                print(colored("   Line           ", color))
                print(colored("=" * 88, color))
                for i in range(5, 10):
                    print(colored(f"|| {i}.{cards[i]:<14} ", color), end='')
                print(colored("||", color))
                print(colored("=" * 88, color))
                
                return get_choice(
                    f'Player {player.index + 1}, what card do you want the Ninja at position {position} to copy? (0-9)\n',
                    range(0, 10)
                )
        else:  # AI player
            def get_ninja_choice(position, cards):
                return get_ai_ninja_choice(position, cards, model, game)
        
        cards = player.get_all_cards()
        working_cards = Scorer.handle_ninjas(cards, CHARACTERS, get_ninja_choice)
        score_breakdown = Scorer.calculate_score(working_cards)
        player_scores[player.index] = {
            'cards': working_cards,
            'breakdown': score_breakdown,
            'total': score_breakdown['Total']
        }
    
    # Display scores
    print(colored("\n=== FINAL SCORES ===", "green"))
    for idx, data in player_scores.items():
        player_name = "Player 1 (You)" if idx == 0 else "Player 2 (AI)"
        print(colored(f"\n{player_name}: {data['total']} points", game.players[idx].color))
        for card_type, points in data['breakdown'].items():
            if card_type != 'Total' and points != 0:
                print(f"  {card_type}: {points}")
    
    # Determine winner
    score1 = player_scores[0]['total']
    score2 = player_scores[1]['total']
    
    if score1 > score2:
        print(colored(f'\nPlayer 1 Victory! {score1} to {score2}!', 'green'))
    elif score2 > score1:
        print(colored(f'\nPlayer 2 (AI) Victory! {score2} to {score1}!', 'yellow'))
    else:
        cards1 = player_scores[0]['cards']
        cards2 = player_scores[1]['cards']
        unique1 = len(set(cards1) - {'Mountain', 'Ninja'})
        unique2 = len(set(cards2) - {'Mountain', 'Ninja'})
        
        if unique1 > unique2:
            print(colored(f'\nPlayer 1 Victory by tiebreaker! {score1} points, {unique1} unique cards!', 'green'))
        elif unique2 > unique1:
            print(colored(f'\nPlayer 2 (AI) Victory by tiebreaker! {score2} points, {unique2} unique cards!', 'yellow'))
        else:
            print(colored(f'\nTrue tie! Both players have {score1} points and {unique1} unique cards.', 'cyan'))

if __name__ == "__main__":
    main()