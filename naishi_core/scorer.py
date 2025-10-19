# naishi_core/scorer.py

from typing import Dict, List, Set
from .constants import CHARACTERS, LINE_SIZE
from .utils import check_adjacency

class Scorer:
    """Handles all scoring logic"""
    
    @staticmethod
    def handle_ninjas(cards: List[str], characters: List[str], get_ninja_choice_func) -> List[str]:
        """
        Handle ninja card copying. Returns a new list with ninjas replaced.
        
        Args:
            cards: List of 10 cards (line + hand)
            characters: List of valid character cards
            get_ninja_choice_func: Function to get user's ninja choice
                                  Signature: (position: int, cards: List[str]) -> int
        
        Returns:
            New list with ninjas replaced by their copied cards
        """
        ninja_replacements = {}
        
        for i, card in enumerate(cards):
            if card == 'Ninja':
                # Check if there are any valid characters to copy (excluding other Ninjas)
                valid_characters = [c for c in cards if c in characters and c != 'Ninja']
                
                if not valid_characters:
                    # No valid characters to copy - Ninja scores 0 (leave as Ninja)
                    # This handles the edge case where all cards are buildings/mountains
                    continue
                
                while True:
                    choice_index = get_ninja_choice_func(i, cards)
                    copy = cards[choice_index]
                    
                    if copy == 'Ninja':
                        continue  # Invalid, will retry
                    elif copy not in characters:
                        continue  # Invalid, will retry
                    else:
                        ninja_replacements[i] = copy
                        break
        
        # Create working copy with ninjas replaced
        working_cards = cards.copy()
        for ninja_pos, replacement in ninja_replacements.items():
            working_cards[ninja_pos] = replacement
        
        return working_cards
    
    @staticmethod
    def calculate_score(cards: List[str]) -> Dict[str, int]:
        """
        Calculate score breakdown for a player.
        
        Args:
            cards: List of 10 cards (line + hand), with ninjas already resolved
        
        Returns:
            Dict mapping card names to their scores, plus 'Total'
        """
        score_table = {
            "Mountain": 0,
            "Naishi": 0, 
            "Councellor": 0,  
            "Sentinel": 0, 
            "Fort": 0,  
            "Monk": 0,  
            "Torii": 0, 
            "Knight": 0, 
            "Banner": 0, 
            "Rice fields": 0, 
            "Ronin": 0, 
            "Ninja": 0,
            "Total": 0 
        }
        
        # Count-based preparation
        mountains = cards.count('Mountain')
        toriis = cards.count('Torii')
        banners = cards.count('Banner')
        ronins = cards.count('Ronin')
        
        # Ronin preparation (count unique non-Mountain cards)
        unique_cards = set(cards) - {'Mountain'}
        num_unique = len(unique_cards)
        
        # Score each card
        for i, card in enumerate(cards):
            if card == 'Mountain':
                pass  # Scored at end
            
            elif card == 'Naishi':
                if i == 2:
                    score_table['Naishi'] += 12
                elif i == 7:
                    score_table['Naishi'] += 8
            
            elif card == 'Fort':
                if i in {0, 4, 5, 9}:
                    score_table['Fort'] += 6
            
            elif card == 'Councellor':
                if i in {1, 6, 3, 8}:
                    score_table['Councellor'] += 4
                elif i in {2, 7}:
                    score_table['Councellor'] += 3
                else:
                    score_table['Councellor'] += 2
                
                # Adjacent to Naishi bonus
                adjacents = check_adjacency(i, cards)
                for adjacent_info in adjacents.values():
                    if adjacent_info['card'] == 'Naishi':
                        score_table['Councellor'] += 4
            
            elif card == 'Sentinel':
                adjacents = check_adjacency(i, cards)
                
                # Not adjacent to another Sentinel
                has_adjacent_sentinel = any(
                    adj['card'] == 'Sentinel' for adj in adjacents.values()
                )
                if not has_adjacent_sentinel:
                    score_table['Sentinel'] += 3
                
                # Adjacent to Fort bonus
                for adjacent_info in adjacents.values():
                    if adjacent_info['card'] == 'Fort':
                        score_table['Sentinel'] += 4
            
            elif card == 'Monk':
                if i >= LINE_SIZE:  # In hand
                    score_table['Monk'] += 5
                
                # Adjacent to Torii bonus
                adjacents = check_adjacency(i, cards)
                for adjacent_info in adjacents.values():
                    if adjacent_info['card'] == 'Torii':
                        score_table['Monk'] += 2
            
            elif card == 'Knight':
                if i >= LINE_SIZE:  # In hand
                    score_table['Knight'] += 3
                
                # Directly above Banner bonus
                adjacents = check_adjacency(i, cards)
                if 'up' in adjacents and adjacents['up']['card'] == 'Banner':
                    score_table['Knight'] += 10
            
            elif card == 'Torii':
                pass  # Scored at end
            
            elif card == 'Banner':
                pass  # Scored at end
            
            elif card == 'Ronin':
                pass  # Scored at end
        
        # Rice fields - connected groups
        score_table['Rice fields'] = Scorer._score_rice_fields(cards)
        
        # Mountain scoring
        if mountains == 1:
            score_table['Mountain'] = 5
        elif mountains > 1:
            score_table['Mountain'] = -5
        
        # Torii scoring
        if toriis == 1:
            score_table['Torii'] = -5
        elif toriis >= 3:
            score_table['Torii'] = 30
        
        # Banner scoring
        if banners == 1:
            score_table['Banner'] = 3
        elif banners >= 2:
            score_table['Banner'] = 8
        
        # Ronin scoring
        if num_unique == 8:
            score_table['Ronin'] = ronins * 8
        elif num_unique == 9:
            score_table['Ronin'] = ronins * 15
        elif num_unique == 10:
            score_table['Ronin'] = ronins * 45
        
        # Calculate total
        score_table['Total'] = sum(v for k, v in score_table.items() if k != 'Total')
        
        return score_table
    
    @staticmethod
    def _score_rice_fields(cards: List[str]) -> int:
        """Score connected rice field groups using BFS"""
        processed = set()
        groups = []
        
        for i, card in enumerate(cards):
            if card == 'Rice fields' and i not in processed:
                # BFS to find connected group
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
                
                groups.append(len(group))
        
        # Score each group
        total_score = 0
        for group_size in groups:
            if group_size == 1:
                total_score += 0
            elif group_size == 2:
                total_score += 10
            elif group_size == 3:
                total_score += 20
            elif group_size >= 4:
                total_score += 30  # Maximum score for 4+ connected
        
        return total_score
    
    @staticmethod
    def determine_winner(score1: int, score2: int, cards1: List[str], cards2: List[str]) -> int:
        """
        Determine winner with tiebreaker.
        
        Returns:
            0 for player 1 win, 1 for player 2 win, -1 for true tie
        """
        if score1 > score2:
            return 0
        elif score2 > score1:
            return 1
        
        # Tiebreaker: most unique cards (excluding Mountain and Ninja)
        unique1 = set(cards1) - {'Mountain', 'Ninja'}
        unique2 = set(cards2) - {'Mountain', 'Ninja'}
        
        if len(unique1) > len(unique2):
            return 0
        elif len(unique2) > len(unique1):
            return 1
        else:
            return -1  # True tie