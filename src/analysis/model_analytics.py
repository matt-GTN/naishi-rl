# model_analytics.py
"""
Comprehensive analytics system for Naishi RL models using Plotly for interactive visualizations.
"""
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from collections import defaultdict, Counter
from sb3_contrib import MaskablePPO
from src.training.naishi_env import NaishiEnv
from naishi_core import CARDS, CHARACTERS, CARD_TO_INT, Scorer
import json
import os
from datetime import datetime

class ModelAnalytics:
    """Comprehensive analytics tracker for Naishi models with interactive Plotly visualizations."""
    
    def __init__(self, model_path, num_games=100):
        self.model_path = model_path
        self.model = MaskablePPO.load(model_path)
        self.num_games = num_games
        self.stats = self._init_stats()
    
    def _init_stats(self):
        """Initialize statistics storage."""
        return {
            'wins': 0, 'losses': 0, 'draws': 0,
            'score_differences': [], 'final_scores': [], 'opponent_scores': [],
            'action_counts': defaultdict(int), 'action_by_turn': defaultdict(list),
            'draft_choices': [], 'draft_cards_kept': [], 'draft_cards_given': [],
            'cards_developed': Counter(), 'cards_in_final_line': Counter(),
            'cards_in_final_hand': Counter(), 'cards_swapped_away': Counter(),
            'cards_discarded_from_river': Counter(), 'decks_drawn_from': Counter(),
            'river_swaps_by_deck': Counter(), 'swap_types': Counter(),
            'swap_positions': [], 'emissary_usage_per_game': [],
            'recall_frequency': 0, 'decree_usage': 0, 'game_lengths': [],
            'actions_per_game': [], 'ending_initiated': 0,
            'line_positions_developed': Counter(), 'hand_positions_developed': Counter(),
            'develop_timing': [], 'character_combinations': Counter(),
            'winning_combinations': Counter(), 'empty_decks_at_end': [],
            'river_cards_remaining': [], 'turn_by_turn_scores': [],
        }
    
    def run_analysis(self):
        """Run comprehensive analysis over multiple games."""
        from tqdm import tqdm
        
        print(f"Running analysis on {self.model_path}")
        print(f"Playing {self.num_games} games...")
        
        for game_num in tqdm(range(self.num_games), desc="Analyzing games", unit="game"):
            self._play_and_analyze_game()
        
        print("Analysis complete!")
        return self.stats

    def _play_and_analyze_game(self):
        """Play a single game and collect statistics."""
        
        # Create a random opponent (model plays against random)
        env = NaishiEnv(opponent_policy=self.model)
        obs, info = env.reset()
        
        game_actions = 0
        done = False
        max_actions = 1000  # Safety limit to prevent infinite loops (self-play can be longer)
        
        action_type_counts = {}
        last_10_actions = []
        
        while not done and game_actions < max_actions:
            action_mask = info.get('action_mask')
            # MaskablePPO requires action_masks parameter
            action, _ = self.model.predict(obs, deterministic=True, action_masks=action_mask)
            
            # Track action types for debugging
            action_type = action[0]
            action_type_counts[action_type] = action_type_counts.get(action_type, 0) + 1
            last_10_actions.append(action_type)
            if len(last_10_actions) > 10:
                last_10_actions.pop(0)
            
            self._track_action(action, env, obs)
            game_actions += 1
            obs, reward, terminated, truncated, info = env.step(action)
            done = terminated or truncated
        
        if game_actions >= max_actions:
            empty_decks = env.gs.river.count_empty_decks()
            cards_left = env.gs.river.cards_left()
            print(f"\nWarning: Game exceeded {max_actions} actions")
            print(f"  Empty decks: {empty_decks}/5, Cards remaining: {cards_left}")
            print(f"  Turn count: {env.gs.turn_count}")
            print(f"  In draft phase: {env.gs.in_draft_phase}")
            print(f"  Action type counts: {action_type_counts}")
            print(f"  Last 10 actions: {last_10_actions}")
        
        self._collect_final_stats(env)
        self.stats['actions_per_game'].append(game_actions)
    
    def _track_action(self, action, env, obs):
        """Track detailed action statistics."""
        action_type = action[0]
        turn = env.gs.turn_count
        action_names = ['Draft', 'Develop', 'Swap', 'Discard', 'Recall', 'Decree', 'End Game']
        
        if action_type < len(action_names):
            action_name = action_names[action_type]
            self.stats['action_counts'][action_name] += 1
            self.stats['action_by_turn'][action_name].append(turn)
        
        player = env.gs.players[env.gs.current_player_idx]
        
        if action_type == 0 and env.gs.in_draft_phase:
            choice = action[1] % 2
            self.stats['draft_choices'].append(choice)
            draft_hand = env.gs.draft_hands[env.gs.current_player_idx]
            if len(draft_hand) >= 2:
                self.stats['draft_cards_given'].append(draft_hand[choice])
                self.stats['draft_cards_kept'].append(draft_hand[1 - choice])
        
        elif action_type == 1:  # Develop
            discard_pos, deck_idx = action[1], action[2]
            
            # Track which deck they draw from
            if 0 <= deck_idx < 5:
                self.stats['decks_drawn_from'][deck_idx] += 1
            
            # Track which position they develop (with bounds checking)
            if discard_pos < 5:
                self.stats['line_positions_developed'][discard_pos] += 1
                if discard_pos < len(player.line):
                    old_card = player.line[discard_pos]
                    self.stats['cards_developed'][old_card] += 1
            else:
                hand_pos = discard_pos - 5
                if hand_pos < 5:
                    self.stats['hand_positions_developed'][hand_pos] += 1
                if hand_pos < len(player.hand):
                    old_card = player.hand[hand_pos]
                    self.stats['cards_developed'][old_card] += 1
            
            self.stats['develop_timing'].append(turn)
        
        elif action_type == 2:  # Swap
            swap_type = action[3]
            swap_names = ['hand', 'line', 'between', 'river']
            if swap_type < len(swap_names):
                self.stats['swap_types'][swap_names[swap_type]] += 1
            
            if swap_type == 3:
                deck1, deck2 = action[4], action[5]
                self.stats['river_swaps_by_deck'][deck1] += 1
                self.stats['river_swaps_by_deck'][deck2] += 1
        
        elif action_type == 3:  # Discard
            deck1, deck2 = action[6], action[7]
            for deck in [deck1, deck2]:
                if not env.gs.river.is_empty(deck):
                    card = env.gs.river.get_top_card(deck)
                    if card:
                        self.stats['cards_discarded_from_river'][card] += 1
        
        elif action_type == 4:
            self.stats['recall_frequency'] += 1
        elif action_type == 5:
            self.stats['decree_usage'] += 1
        elif action_type == 6:
            self.stats['ending_initiated'] += 1
    
    def _collect_final_stats(self, env):
        """Collect statistics at the end of a game."""
        player = env.gs.players[0]
        opponent = env.gs.players[1]
        
        player_cards = player.get_all_cards()
        opponent_cards = opponent.get_all_cards()
        
        player_score = Scorer.calculate_score(player_cards)['Total']
        opponent_score = Scorer.calculate_score(opponent_cards)['Total']
        
        self.stats['final_scores'].append(player_score)
        self.stats['opponent_scores'].append(opponent_score)
        self.stats['score_differences'].append(player_score - opponent_score)
        
        if player_score > opponent_score:
            self.stats['wins'] += 1
        elif player_score < opponent_score:
            self.stats['losses'] += 1
        else:
            self.stats['draws'] += 1
        
        for card in player.line:
            self.stats['cards_in_final_line'][card] += 1
        for card in player.hand:
            self.stats['cards_in_final_hand'][card] += 1
        
        characters_in_line = [c for c in player.line if c in CHARACTERS]
        for i, char1 in enumerate(characters_in_line):
            for char2 in characters_in_line[i+1:]:
                combo = tuple(sorted([char1, char2]))
                self.stats['character_combinations'][combo] += 1
                if player_score > opponent_score:
                    self.stats['winning_combinations'][combo] += 1
        
        self.stats['game_lengths'].append(env.gs.turn_count)
        self.stats['empty_decks_at_end'].append(env.gs.river.count_empty_decks())
        self.stats['river_cards_remaining'].append(sum(env.gs.river.cards_left()))
        
        emissaries_used = 2 - player.emissaries
        self.stats['emissary_usage_per_game'].append(emissaries_used)

    def generate_report(self, output_dir="analytics_reports"):
        """Generate comprehensive interactive HTML report."""
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_name = os.path.basename(self.model_path)
        report_dir = os.path.join(output_dir, f"{model_name}_{timestamp}")
        os.makedirs(report_dir, exist_ok=True)
        
        print(f"\nGenerating comprehensive interactive report in {report_dir}/")
        
        figures = []
        figures.append(('01_win_rate', self._create_win_rate_charts()))
        figures.append(('02_score_analysis', self._create_score_analysis()))
        figures.append(('03_action_distribution', self._create_action_distribution()))
        figures.append(('04_draft_analysis', self._create_draft_analysis()))
        figures.append(('05_card_preferences', self._create_card_preferences()))
        figures.append(('06_deck_preferences', self._create_deck_preferences()))
        figures.append(('07_swap_analysis', self._create_swap_analysis()))
        figures.append(('08_emissary_usage', self._create_emissary_usage()))
        figures.append(('09_timing_analysis', self._create_timing_analysis()))
        figures.append(('10_position_heatmap', self._create_position_heatmap()))
        figures.append(('11_character_synergies', self._create_character_synergies()))
        figures.append(('12_strategic_overview', self._create_strategic_overview()))
        
        # Save all figures
        for name, fig in figures:
            if fig:
                fig.write_html(os.path.join(report_dir, f"{name}.html"))
        
        # Create index page
        self._create_index_page(report_dir, figures)
        
        # Save raw data
        self._save_raw_data(report_dir)
        
        print(f"✓ Report generated successfully!")
        print(f"  Open {report_dir}/index.html to view")
        
        return report_dir
    
    def _create_win_rate_charts(self):
        """Create win rate visualization."""
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=('Win/Loss/Draw Distribution', 'Score Difference Distribution'),
            specs=[[{'type': 'pie'}, {'type': 'histogram'}]]
        )
        
        # Pie chart
        fig.add_trace(go.Pie(
            labels=['Wins', 'Losses', 'Draws'],
            values=[self.stats['wins'], self.stats['losses'], self.stats['draws']],
            marker=dict(colors=['#2ecc71', '#e74c3c', '#95a5a6']),
            hole=0.3
        ), row=1, col=1)
        
        # Score difference histogram
        fig.add_trace(go.Histogram(
            x=self.stats['score_differences'],
            nbinsx=30,
            marker=dict(color='#3498db', line=dict(color='black', width=1)),
            name='Score Diff'
        ), row=1, col=2)
        
        # Add vertical line at x=0 using shapes instead of add_vline
        fig.add_shape(
            type="line",
            x0=0, x1=0, y0=0, y1=1,
            yref="paper",
            line=dict(color="red", width=2, dash="dash"),
            row=1, col=2
        )
        fig.add_annotation(
            x=0, y=1, yref="paper",
            text="Even",
            showarrow=False,
            row=1, col=2
        )
        
        fig.update_layout(
            title_text=f"Win Rate Analysis - {self.num_games} Games",
            height=500,
            showlegend=False
        )
        
        return fig

    def _create_score_analysis(self):
        """Create detailed score analysis."""
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Model Score Distribution', 'Opponent Score Distribution',
                          'Score Comparison Scatter', 'Score Statistics'),
            specs=[[{'type': 'histogram'}, {'type': 'histogram'}],
                   [{'type': 'scatter'}, {'type': 'table'}]]
        )
        
        # Model scores
        fig.add_trace(go.Histogram(
            x=self.stats['final_scores'],
            nbinsx=20,
            marker=dict(color='#3498db', line=dict(color='black', width=1)),
            name='Model'
        ), row=1, col=1)
        
        # Add mean line
        mean_score = np.mean(self.stats['final_scores'])
        fig.add_shape(
            type="line",
            x0=mean_score, x1=mean_score, y0=0, y1=1,
            yref="paper",
            line=dict(color="red", width=2, dash="dash"),
            row=1, col=1
        )
        
        # Opponent scores
        fig.add_trace(go.Histogram(
            x=self.stats['opponent_scores'],
            nbinsx=20,
            marker=dict(color='#e74c3c', line=dict(color='black', width=1)),
            name='Opponent'
        ), row=1, col=2)
        
        # Add mean line
        mean_opp_score = np.mean(self.stats['opponent_scores'])
        fig.add_shape(
            type="line",
            x0=mean_opp_score, x1=mean_opp_score, y0=0, y1=1,
            yref="paper",
            line=dict(color="blue", width=2, dash="dash"),
            row=1, col=2
        )
        
        # Scatter plot
        fig.add_trace(go.Scatter(
            x=self.stats['final_scores'],
            y=self.stats['opponent_scores'],
            mode='markers',
            marker=dict(color='#9b59b6', size=8, opacity=0.6),
            name='Games'
        ), row=2, col=1)
        
        max_score = max(max(self.stats['final_scores']), max(self.stats['opponent_scores']))
        fig.add_trace(go.Scatter(
            x=[0, max_score],
            y=[0, max_score],
            mode='lines',
            line=dict(color='red', dash='dash'),
            name='Equal'
        ), row=2, col=1)
        
        # Statistics table
        fig.add_trace(go.Table(
            header=dict(values=['Metric', 'Model', 'Opponent'],
                       fill_color='paleturquoise',
                       align='left'),
            cells=dict(values=[
                ['Mean', 'Median', 'Std Dev', 'Min', 'Max'],
                [f"{np.mean(self.stats['final_scores']):.2f}",
                 f"{np.median(self.stats['final_scores']):.2f}",
                 f"{np.std(self.stats['final_scores']):.2f}",
                 f"{min(self.stats['final_scores'])}",
                 f"{max(self.stats['final_scores'])}"],
                [f"{np.mean(self.stats['opponent_scores']):.2f}",
                 f"{np.median(self.stats['opponent_scores']):.2f}",
                 f"{np.std(self.stats['opponent_scores']):.2f}",
                 f"{min(self.stats['opponent_scores'])}",
                 f"{max(self.stats['opponent_scores'])}"]
            ], fill_color='lavender', align='left')
        ), row=2, col=2)
        
        fig.update_layout(height=800, showlegend=True, title_text="Score Analysis")
        return fig
    
    def _create_action_distribution(self):
        """Create action distribution charts."""
        actions = list(self.stats['action_counts'].keys())
        counts = list(self.stats['action_counts'].values())
        total = sum(counts)
        percentages = [c/total*100 for c in counts]
        
        colors_map = {'Draft': '#3498db', 'Develop': '#2ecc71', 'Swap': '#f39c12',
                     'Discard': '#e74c3c', 'Recall': '#9b59b6', 'Decree': '#1abc9c',
                     'End Game': '#34495e'}
        colors = [colors_map.get(a, '#95a5a6') for a in actions]
        
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Action Frequency', 'Action Percentage',
                          'Action Timing', 'Actions per Game'),
            specs=[[{'type': 'bar'}, {'type': 'bar'}],
                   [{'type': 'histogram'}, {'type': 'histogram'}]]
        )
        
        # Action counts
        fig.add_trace(go.Bar(
            x=actions, y=counts,
            marker=dict(color=colors, line=dict(color='black', width=1)),
            name='Count'
        ), row=1, col=1)
        
        # Action percentages
        fig.add_trace(go.Bar(
            y=actions, x=percentages,
            orientation='h',
            marker=dict(color=colors, line=dict(color='black', width=1)),
            name='Percentage'
        ), row=1, col=2)
        
        # Action timing
        for action_name in ['Develop', 'Swap', 'Discard', 'Recall']:
            if action_name in self.stats['action_by_turn'] and self.stats['action_by_turn'][action_name]:
                fig.add_trace(go.Histogram(
                    x=self.stats['action_by_turn'][action_name],
                    nbinsx=20,
                    name=action_name,
                    opacity=0.7
                ), row=2, col=1)
        
        # Actions per game
        fig.add_trace(go.Histogram(
            x=self.stats['actions_per_game'],
            nbinsx=20,
            marker=dict(color='#16a085', line=dict(color='black', width=1)),
            name='Actions/Game'
        ), row=2, col=2)
        
        # Add mean line
        mean_actions = np.mean(self.stats['actions_per_game'])
        fig.add_shape(
            type="line",
            x0=mean_actions, x1=mean_actions, y0=0, y1=1,
            yref="paper",
            line=dict(color="red", width=2, dash="dash"),
            row=2, col=2
        )
        
        fig.update_layout(height=800, title_text="Action Distribution Analysis")
        return fig

    def _create_draft_analysis(self):
        """Create draft phase analysis."""
        if not self.stats['draft_choices']:
            return None
        
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Draft Choice Distribution', 'Cards Kept (Top 10)',
                          'Cards Given Away (Top 10)', 'Draft Strategy'),
            specs=[[{'type': 'pie'}, {'type': 'bar'}],
                   [{'type': 'bar'}, {'type': 'indicator'}]]
        )
        
        # Choice distribution
        choice_counts = Counter(self.stats['draft_choices'])
        fig.add_trace(go.Pie(
            labels=['First Card', 'Second Card'],
            values=[choice_counts.get(0, 0), choice_counts.get(1, 0)],
            marker=dict(colors=['#3498db', '#e74c3c']),
            hole=0.3
        ), row=1, col=1)
        
        # Cards kept
        kept_counter = Counter(self.stats['draft_cards_kept'])
        top_kept = kept_counter.most_common(10)
        if top_kept:
            fig.add_trace(go.Bar(
                x=[card for card, _ in top_kept],
                y=[count for _, count in top_kept],
                marker=dict(color='#2ecc71', line=dict(color='black', width=1)),
                name='Kept'
            ), row=1, col=2)
        
        # Cards given away
        given_counter = Counter(self.stats['draft_cards_given'])
        top_given = given_counter.most_common(10)
        if top_given:
            fig.add_trace(go.Bar(
                x=[card for card, _ in top_given],
                y=[count for _, count in top_given],
                marker=dict(color='#e74c3c', line=dict(color='black', width=1)),
                name='Given'
            ), row=2, col=1)
        
        # Strategy indicator
        total_choices = len(self.stats['draft_choices'])
        first_card_pct = (choice_counts.get(0, 0) / total_choices * 100) if total_choices > 0 else 0
        
        fig.add_trace(go.Indicator(
            mode="gauge+number+delta",
            value=first_card_pct,
            title={'text': "First Card Selection %"},
            delta={'reference': 50},
            gauge={'axis': {'range': [None, 100]},
                  'bar': {'color': "#3498db"},
                  'steps': [
                      {'range': [0, 40], 'color': "#e74c3c"},
                      {'range': [40, 60], 'color': "#f39c12"},
                      {'range': [60, 100], 'color': "#2ecc71"}],
                  'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 50}}
        ), row=2, col=2)
        
        fig.update_layout(height=800, title_text="Draft Phase Analysis")
        return fig
    
    def _create_card_preferences(self):
        """Create card preference analysis."""
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Cards in Final Line (Top 15)', 'Cards in Final Hand (Top 15)',
                          'Cards Developed (Top 15)', 'Cards Discarded from River (Top 15)'),
            specs=[[{'type': 'bar'}, {'type': 'bar'}],
                   [{'type': 'bar'}, {'type': 'bar'}]]
        )
        
        # Final line
        top_line = self.stats['cards_in_final_line'].most_common(15)
        if top_line:
            fig.add_trace(go.Bar(
                y=[card for card, _ in top_line],
                x=[count for _, count in top_line],
                orientation='h',
                marker=dict(color='#3498db', line=dict(color='black', width=1)),
                name='Line'
            ), row=1, col=1)
        
        # Final hand
        top_hand = self.stats['cards_in_final_hand'].most_common(15)
        if top_hand:
            fig.add_trace(go.Bar(
                y=[card for card, _ in top_hand],
                x=[count for _, count in top_hand],
                orientation='h',
                marker=dict(color='#2ecc71', line=dict(color='black', width=1)),
                name='Hand'
            ), row=1, col=2)
        
        # Developed
        top_dev = self.stats['cards_developed'].most_common(15)
        if top_dev:
            fig.add_trace(go.Bar(
                y=[card for card, _ in top_dev],
                x=[count for _, count in top_dev],
                orientation='h',
                marker=dict(color='#f39c12', line=dict(color='black', width=1)),
                name='Developed'
            ), row=2, col=1)
        
        # Discarded
        top_disc = self.stats['cards_discarded_from_river'].most_common(15)
        if top_disc:
            fig.add_trace(go.Bar(
                y=[card for card, _ in top_disc],
                x=[count for _, count in top_disc],
                orientation='h',
                marker=dict(color='#e74c3c', line=dict(color='black', width=1)),
                name='Discarded'
            ), row=2, col=2)
        
        fig.update_layout(height=900, title_text="Card Preference Analysis", showlegend=False)
        return fig

    def _create_deck_preferences(self):
        """Create deck preference analysis."""
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=('Decks Drawn From', 'River Swaps by Deck'),
            specs=[[{'type': 'bar'}, {'type': 'bar'}]]
        )
        
        # Decks drawn from
        decks = list(range(5))
        draw_counts = [self.stats['decks_drawn_from'].get(i, 0) for i in decks]
        
        fig.add_trace(go.Bar(
            x=[f"Deck {i}" for i in decks],
            y=draw_counts,
            marker=dict(color=['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6'],
                       line=dict(color='black', width=1)),
            name='Draws'
        ), row=1, col=1)
        
        # River swaps
        swap_counts = [self.stats['river_swaps_by_deck'].get(i, 0) for i in decks]
        
        fig.add_trace(go.Bar(
            x=[f"Deck {i}" for i in decks],
            y=swap_counts,
            marker=dict(color=['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6'],
                       line=dict(color='black', width=1)),
            name='Swaps'
        ), row=1, col=2)
        
        fig.update_layout(height=500, title_text="Deck Preference Analysis", showlegend=False)
        return fig
    
    def _create_swap_analysis(self):
        """Create swap behavior analysis."""
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=('Swap Type Distribution', 'Swap Type Breakdown'),
            specs=[[{'type': 'pie'}, {'type': 'bar'}]]
        )
        
        swap_types = list(self.stats['swap_types'].keys())
        swap_counts = list(self.stats['swap_types'].values())
        
        if swap_types:
            # Pie chart
            fig.add_trace(go.Pie(
                labels=swap_types,
                values=swap_counts,
                marker=dict(colors=['#3498db', '#2ecc71', '#f39c12', '#e74c3c']),
                hole=0.3
            ), row=1, col=1)
            
            # Bar chart
            fig.add_trace(go.Bar(
                x=swap_types,
                y=swap_counts,
                marker=dict(color=['#3498db', '#2ecc71', '#f39c12', '#e74c3c'],
                           line=dict(color='black', width=1)),
                name='Swaps'
            ), row=1, col=2)
        
        fig.update_layout(height=500, title_text="Swap Behavior Analysis")
        return fig
    
    def _create_emissary_usage(self):
        """Create emissary usage analysis."""
        fig = make_subplots(
            rows=1, cols=3,
            subplot_titles=('Emissaries Used per Game', 'Recall Frequency', 'Decree Usage'),
            specs=[[{'type': 'histogram'}, {'type': 'indicator'}, {'type': 'indicator'}]]
        )
        
        # Emissaries per game
        fig.add_trace(go.Histogram(
            x=self.stats['emissary_usage_per_game'],
            nbinsx=3,
            marker=dict(color='#9b59b6', line=dict(color='black', width=1)),
            name='Emissaries'
        ), row=1, col=1)
        
        # Recall frequency
        total_actions = sum(self.stats['action_counts'].values())
        recall_pct = (self.stats['recall_frequency'] / total_actions * 100) if total_actions > 0 else 0
        
        fig.add_trace(go.Indicator(
            mode="number+gauge",
            value=recall_pct,
            title={'text': "Recall %"},
            gauge={'axis': {'range': [None, 10]},
                  'bar': {'color': "#9b59b6"}},
            domain={'x': [0, 1], 'y': [0, 1]}
        ), row=1, col=2)
        
        # Decree usage
        decree_pct = (self.stats['decree_usage'] / total_actions * 100) if total_actions > 0 else 0
        
        fig.add_trace(go.Indicator(
            mode="number+gauge",
            value=decree_pct,
            title={'text': "Decree %"},
            gauge={'axis': {'range': [None, 5]},
                  'bar': {'color': "#1abc9c"}},
            domain={'x': [0, 1], 'y': [0, 1]}
        ), row=1, col=3)
        
        fig.update_layout(height=500, title_text="Emissary Usage Analysis")
        return fig

    def _create_timing_analysis(self):
        """Create timing and game flow analysis."""
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Game Length Distribution', 'Develop Action Timing',
                          'Empty Decks at Game End', 'River Cards Remaining'),
            specs=[[{'type': 'histogram'}, {'type': 'histogram'}],
                   [{'type': 'histogram'}, {'type': 'histogram'}]]
        )
        
        # Game length
        fig.add_trace(go.Histogram(
            x=self.stats['game_lengths'],
            nbinsx=20,
            marker=dict(color='#3498db', line=dict(color='black', width=1)),
            name='Length'
        ), row=1, col=1)
        
        if self.stats['game_lengths']:
            mean_length = np.mean(self.stats['game_lengths'])
            fig.add_shape(
                type="line",
                x0=mean_length, x1=mean_length, y0=0, y1=1,
                yref="paper",
                line=dict(color="red", width=2, dash="dash"),
                row=1, col=1
            )
        
        # Develop timing
        if self.stats['develop_timing']:
            fig.add_trace(go.Histogram(
                x=self.stats['develop_timing'],
                nbinsx=30,
                marker=dict(color='#2ecc71', line=dict(color='black', width=1)),
                name='Timing'
            ), row=1, col=2)
        
        # Empty decks
        fig.add_trace(go.Histogram(
            x=self.stats['empty_decks_at_end'],
            nbinsx=6,
            marker=dict(color='#e74c3c', line=dict(color='black', width=1)),
            name='Empty'
        ), row=2, col=1)
        
        # River cards remaining
        fig.add_trace(go.Histogram(
            x=self.stats['river_cards_remaining'],
            nbinsx=20,
            marker=dict(color='#f39c12', line=dict(color='black', width=1)),
            name='Remaining'
        ), row=2, col=2)
        
        fig.update_layout(height=800, title_text="Timing and Game Flow Analysis")
        return fig
    
    def _create_position_heatmap(self):
        """Create position preference heatmap."""
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=('Line Position Development', 'Hand Position Development'),
            specs=[[{'type': 'bar'}, {'type': 'bar'}]]
        )
        
        # Line positions
        line_positions = list(range(5))
        line_counts = [self.stats['line_positions_developed'].get(i, 0) for i in line_positions]
        
        fig.add_trace(go.Bar(
            x=[f"Pos {i}" for i in line_positions],
            y=line_counts,
            marker=dict(color=line_counts, colorscale='Blues',
                       line=dict(color='black', width=1)),
            name='Line'
        ), row=1, col=1)
        
        # Hand positions
        hand_positions = list(range(5))
        hand_counts = [self.stats['hand_positions_developed'].get(i, 0) for i in hand_positions]
        
        fig.add_trace(go.Bar(
            x=[f"Pos {i}" for i in hand_positions],
            y=hand_counts,
            marker=dict(color=hand_counts, colorscale='Greens',
                       line=dict(color='black', width=1)),
            name='Hand'
        ), row=1, col=2)
        
        fig.update_layout(height=500, title_text="Position Development Preferences", showlegend=False)
        return fig
    
    def _create_character_synergies(self):
        """Create character synergy analysis."""
        if not self.stats['character_combinations']:
            return None
        
        top_combos = self.stats['character_combinations'].most_common(15)
        
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=('Most Common Character Pairs', 'Winning Character Pairs'),
            specs=[[{'type': 'bar'}, {'type': 'bar'}]]
        )
        
        # All combinations
        combo_labels = [f"{c1}+{c2}" for (c1, c2), _ in top_combos]
        combo_counts = [count for _, count in top_combos]
        
        fig.add_trace(go.Bar(
            y=combo_labels,
            x=combo_counts,
            orientation='h',
            marker=dict(color='#3498db', line=dict(color='black', width=1)),
            name='All'
        ), row=1, col=1)
        
        # Winning combinations
        winning_combos = [(combo, self.stats['winning_combinations'].get(combo, 0)) 
                         for combo, _ in top_combos]
        winning_combos.sort(key=lambda x: x[1], reverse=True)
        
        win_labels = [f"{c1}+{c2}" for (c1, c2), _ in winning_combos[:15]]
        win_counts = [count for _, count in winning_combos[:15]]
        
        fig.add_trace(go.Bar(
            y=win_labels,
            x=win_counts,
            orientation='h',
            marker=dict(color='#2ecc71', line=dict(color='black', width=1)),
            name='Wins'
        ), row=1, col=2)
        
        fig.update_layout(height=600, title_text="Character Synergy Analysis", showlegend=False)
        return fig

    def _create_strategic_overview(self):
        """Create strategic overview dashboard."""
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=('Win Rate', 'Avg Score Difference', 'Avg Game Length',
                          'Emissary Efficiency', 'Action Diversity', 'Ending Control'),
            specs=[[{'type': 'indicator'}, {'type': 'indicator'}],
                   [{'type': 'indicator'}, {'type': 'indicator'}],
                   [{'type': 'indicator'}, {'type': 'indicator'}]]
        )
        
        total_games = self.stats['wins'] + self.stats['losses'] + self.stats['draws']
        win_rate = (self.stats['wins'] / total_games * 100) if total_games > 0 else 0
        
        # Win rate
        fig.add_trace(go.Indicator(
            mode="gauge+number+delta",
            value=win_rate,
            title={'text': "Win Rate %"},
            delta={'reference': 50},
            gauge={'axis': {'range': [None, 100]},
                  'bar': {'color': "#2ecc71"},
                  'steps': [
                      {'range': [0, 40], 'color': "#e74c3c"},
                      {'range': [40, 60], 'color': "#f39c12"},
                      {'range': [60, 100], 'color': "#2ecc71"}],
                  'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 50}}
        ), row=1, col=1)
        
        # Avg score difference
        avg_score_diff = np.mean(self.stats['score_differences']) if self.stats['score_differences'] else 0
        
        fig.add_trace(go.Indicator(
            mode="number+delta",
            value=avg_score_diff,
            title={'text': "Avg Score Diff"},
            delta={'reference': 0},
            number={'suffix': " pts"}
        ), row=1, col=2)
        
        # Avg game length
        avg_length = np.mean(self.stats['game_lengths']) if self.stats['game_lengths'] else 0
        
        fig.add_trace(go.Indicator(
            mode="number",
            value=avg_length,
            title={'text': "Avg Game Length"},
            number={'suffix': " turns"}
        ), row=2, col=1)
        
        # Emissary efficiency
        avg_emissaries = np.mean(self.stats['emissary_usage_per_game']) if self.stats['emissary_usage_per_game'] else 0
        
        fig.add_trace(go.Indicator(
            mode="gauge+number",
            value=avg_emissaries,
            title={'text': "Avg Emissaries Used"},
            gauge={'axis': {'range': [0, 2]},
                  'bar': {'color': "#9b59b6"}}
        ), row=2, col=2)
        
        # Action diversity (entropy)
        action_counts = list(self.stats['action_counts'].values())
        total_actions = sum(action_counts)
        if total_actions > 0:
            probs = [c/total_actions for c in action_counts]
            entropy = -sum(p * np.log2(p) for p in probs if p > 0)
            max_entropy = np.log2(len(action_counts))
            diversity = (entropy / max_entropy * 100) if max_entropy > 0 else 0
        else:
            diversity = 0
        
        fig.add_trace(go.Indicator(
            mode="gauge+number",
            value=diversity,
            title={'text': "Action Diversity %"},
            gauge={'axis': {'range': [0, 100]},
                  'bar': {'color': "#3498db"}}
        ), row=3, col=1)
        
        # Ending control
        ending_pct = (self.stats['ending_initiated'] / total_games * 100) if total_games > 0 else 0
        
        fig.add_trace(go.Indicator(
            mode="gauge+number",
            value=ending_pct,
            title={'text': "Games Ended by Model %"},
            gauge={'axis': {'range': [0, 100]},
                  'bar': {'color': "#e74c3c"}}
        ), row=3, col=2)
        
        fig.update_layout(height=1000, title_text="Strategic Overview Dashboard")
        return fig
    
    def _create_index_page(self, report_dir, figures):
        """Create HTML index page with all charts."""
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Naishi Model Analytics Report</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
        }}
        h1 {{
            color: #2c3e50;
            text-align: center;
            margin-bottom: 10px;
        }}
        .subtitle {{
            text-align: center;
            color: #7f8c8d;
            margin-bottom: 30px;
        }}
        .chart-grid {{
            display: grid;
            grid-template-columns: 1fr;
            gap: 20px;
        }}
        .chart-container {{
            border: 2px solid #ecf0f1;
            border-radius: 8px;
            padding: 15px;
            background: #f8f9fa;
        }}
        iframe {{
            width: 100%;
            height: 600px;
            border: none;
            border-radius: 5px;
        }}
        .stats-summary {{
            background: #3498db;
            color: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }}
        .stat-box {{
            background: rgba(255,255,255,0.2);
            padding: 15px;
            border-radius: 5px;
            text-align: center;
        }}
        .stat-value {{
            font-size: 2em;
            font-weight: bold;
        }}
        .stat-label {{
            font-size: 0.9em;
            opacity: 0.9;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🎮 Naishi Model Analytics Report</h1>
        <div class="subtitle">
            Model: {os.path.basename(self.model_path)}<br>
            Games Analyzed: {self.num_games}<br>
            Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        </div>
        
        <div class="stats-summary">
            <h2 style="margin-top: 0;">Quick Stats</h2>
            <div class="stats-grid">
                <div class="stat-box">
                    <div class="stat-value">{self.stats['wins']}</div>
                    <div class="stat-label">Wins</div>
                </div>
                <div class="stat-box">
                    <div class="stat-value">{self.stats['losses']}</div>
                    <div class="stat-label">Losses</div>
                </div>
                <div class="stat-box">
                    <div class="stat-value">{self.stats['draws']}</div>
                    <div class="stat-label">Draws</div>
                </div>
                <div class="stat-box">
                    <div class="stat-value">{np.mean(self.stats['final_scores']):.1f}</div>
                    <div class="stat-label">Avg Score</div>
                </div>
                <div class="stat-box">
                    <div class="stat-value">{np.mean(self.stats['game_lengths']):.1f}</div>
                    <div class="stat-label">Avg Game Length</div>
                </div>
            </div>
        </div>
        
        <div class="chart-grid">
"""
        
        for name, _ in figures:
            html_content += f"""
            <div class="chart-container">
                <iframe src="{name}.html"></iframe>
            </div>
"""
        
        html_content += """
        </div>
    </div>
</body>
</html>
"""
        
        with open(os.path.join(report_dir, 'index.html'), 'w') as f:
            f.write(html_content)
    
    def _save_raw_data(self, report_dir):
        """Save raw statistics as JSON."""
        def convert_to_json_serializable(obj):
            """Recursively convert numpy types and tuples to JSON-serializable types."""
            if isinstance(obj, (Counter, defaultdict)):
                # Convert dict with potentially tuple keys
                return {str(k) if isinstance(k, tuple) else convert_to_json_serializable(k): 
                       convert_to_json_serializable(v) 
                       for k, v in dict(obj).items()}
            elif isinstance(obj, dict):
                # Convert dict keys to strings if they're tuples
                return {str(k) if isinstance(k, tuple) else convert_to_json_serializable(k): 
                       convert_to_json_serializable(v) 
                       for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_to_json_serializable(item) for item in obj]
            elif isinstance(obj, tuple):
                # Convert tuples to lists for JSON
                return [convert_to_json_serializable(item) for item in obj]
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, (np.integer, np.int64, np.int32)):
                return int(obj)
            elif isinstance(obj, (np.floating, np.float64, np.float32)):
                return float(obj)
            else:
                return obj
        
        json_stats = convert_to_json_serializable(self.stats)
        
        with open(os.path.join(report_dir, 'raw_data.json'), 'w') as f:
            json.dump(json_stats, f, indent=2)


def analyze_model(model_path, num_games=100):
    """Convenience function to analyze a model and generate report."""
    analytics = ModelAnalytics(model_path, num_games)
    analytics.run_analysis()
    report_dir = analytics.generate_report()
    return report_dir


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python model_analytics.py <model_path> [num_games]")
        print("Example: python model_analytics.py models/naishi_model 100")
        sys.exit(1)
    
    model_path = sys.argv[1]
    num_games = int(sys.argv[2]) if len(sys.argv) > 2 else 100
    
    report_dir = analyze_model(model_path, num_games)
    print(f"\n✓ Analysis complete! Open {report_dir}/index.html in your browser.")
