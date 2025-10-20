"""
Task 36: Unit tests for GameState scoring
Tests each card type scoring, adjacency bonuses, Ninja copying, and tiebreaker
Requirements: 1.8, 7.1-7.12
"""

import pytest
from naishi_core.scorer import Scorer
from naishi_core.constants import CHARACTERS


class TestMountainScoring:
    """Test Mountain scoring rules (Req 7.1)"""
    
    def test_one_mountain_scores_5(self):
        """1 Mountain = +5 points"""
        cards = ['Mountain', 'Fort', 'Fort', 'Fort', 'Fort',
                 'Fort', 'Fort', 'Fort', 'Fort', 'Fort']
        score = Scorer.calculate_score(cards)
        assert score['Mountain'] == 5
    
    def test_two_mountains_scores_minus_5(self):
        """2+ Mountains = -5 points total"""
        cards = ['Mountain', 'Mountain', 'Fort', 'Fort', 'Fort',
                 'Fort', 'Fort', 'Fort', 'Fort', 'Fort']
        score = Scorer.calculate_score(cards)
        assert score['Mountain'] == -5
    
    def test_three_mountains_scores_minus_5(self):
        """3 Mountains = -5 points total"""
        cards = ['Mountain', 'Mountain', 'Mountain', 'Fort', 'Fort',
                 'Fort', 'Fort', 'Fort', 'Fort', 'Fort']
        score = Scorer.calculate_score(cards)
        assert score['Mountain'] == -5
    
    def test_no_mountains_scores_0(self):
        """0 Mountains = 0 points"""
        cards = ['Fort'] * 10
        score = Scorer.calculate_score(cards)
        assert score['Mountain'] == 0


class TestNaishiScoring:
    """Test Naishi scoring rules (Req 7.2)"""
    
    def test_naishi_at_position_2_scores_12(self):
        """Naishi at position 2 (Line center) = +12 points"""
        cards = ['Fort', 'Fort', 'Naishi', 'Fort', 'Fort',
                 'Fort', 'Fort', 'Fort', 'Fort', 'Fort']
        score = Scorer.calculate_score(cards)
        assert score['Naishi'] == 12
    
    def test_naishi_at_position_7_scores_8(self):
        """Naishi at position 7 (Hand center) = +8 points"""
        cards = ['Fort', 'Fort', 'Fort', 'Fort', 'Fort',
                 'Fort', 'Fort', 'Naishi', 'Fort', 'Fort']
        score = Scorer.calculate_score(cards)
        assert score['Naishi'] == 8
    
    def test_naishi_at_other_positions_scores_0(self):
        """Naishi at other positions = 0 points"""
        cards = ['Naishi', 'Fort', 'Fort', 'Fort', 'Fort',
                 'Fort', 'Fort', 'Fort', 'Fort', 'Fort']
        score = Scorer.calculate_score(cards)
        assert score['Naishi'] == 0
    
    def test_two_naishi_both_score(self):
        """Two Naishi cards both score independently"""
        cards = ['Fort', 'Fort', 'Naishi', 'Fort', 'Fort',
                 'Fort', 'Fort', 'Naishi', 'Fort', 'Fort']
        score = Scorer.calculate_score(cards)
        assert score['Naishi'] == 20  # 12 + 8


class TestCouncillorScoring:
    """Test Councellor scoring rules (Req 7.3)"""
    
    def test_councellor_at_positions_1_3_6_8_scores_4(self):
        """Councellor at positions 1, 3, 6, 8 = +4 points each"""
        cards = ['Fort', 'Councellor', 'Fort', 'Councellor', 'Fort',
                 'Fort', 'Councellor', 'Fort', 'Councellor', 'Fort']
        score = Scorer.calculate_score(cards)
        assert score['Councellor'] == 16  # 4 * 4
    
    def test_councellor_at_positions_2_7_scores_3(self):
        """Councellor at positions 2, 7 = +3 points each"""
        cards = ['Fort', 'Fort', 'Councellor', 'Fort', 'Fort',
                 'Fort', 'Fort', 'Councellor', 'Fort', 'Fort']
        score = Scorer.calculate_score(cards)
        assert score['Councellor'] == 6  # 3 * 2
    
    def test_councellor_at_positions_0_4_5_9_scores_2(self):
        """Councellor at positions 0, 4, 5, 9 = +2 points each"""
        cards = ['Councellor', 'Fort', 'Fort', 'Fort', 'Councellor',
                 'Councellor', 'Fort', 'Fort', 'Fort', 'Councellor']
        score = Scorer.calculate_score(cards)
        assert score['Councellor'] == 8  # 2 * 4

    def test_councellor_adjacent_to_naishi_bonus(self):
        """Councellor adjacent to Naishi = +4 bonus per Naishi"""
        # Councellor at pos 1, Naishi at pos 2 (adjacent right)
        cards = ['Fort', 'Councellor', 'Naishi', 'Fort', 'Fort',
                 'Fort', 'Fort', 'Fort', 'Fort', 'Fort']
        score = Scorer.calculate_score(cards)
        # Base: 4 (pos 1) + Bonus: 4 (adjacent to Naishi) = 8
        assert score['Councellor'] == 8
    
    def test_councellor_adjacent_to_two_naishi(self):
        """Councellor adjacent to 2 Naishi = +8 bonus"""
        # Councellor at pos 2, Naishi at pos 1 and 7 (adjacent left and down)
        cards = ['Fort', 'Naishi', 'Councellor', 'Fort', 'Fort',
                 'Fort', 'Fort', 'Naishi', 'Fort', 'Fort']
        score = Scorer.calculate_score(cards)
        # Base: 3 (pos 2) + Bonus: 4 + 4 (two Naishi) = 11
        assert score['Councellor'] == 11


class TestSentinelScoring:
    """Test Sentinel scoring rules (Req 7.4)"""
    
    def test_sentinel_not_adjacent_to_sentinel_scores_3(self):
        """Sentinel not adjacent to another Sentinel = +3 points"""
        cards = ['Sentinel', 'Fort', 'Fort', 'Fort', 'Sentinel',
                 'Fort', 'Fort', 'Fort', 'Fort', 'Fort']
        score = Scorer.calculate_score(cards)
        # Sentinel at pos 0: 3 (not adjacent to Sentinel) + 4 (adjacent to Fort at pos 1) + 4 (adjacent to Fort at pos 5) = 11
        # Sentinel at pos 4: 3 (not adjacent to Sentinel) + 4 (adjacent to Fort at pos 3) + 4 (adjacent to Fort at pos 9) = 11
        # Total: 22
        assert score['Sentinel'] == 22
    
    def test_sentinel_adjacent_to_sentinel_scores_0(self):
        """Sentinel adjacent to another Sentinel = 0 base points"""
        cards = ['Sentinel', 'Sentinel', 'Fort', 'Fort', 'Fort',
                 'Fort', 'Fort', 'Fort', 'Fort', 'Fort']
        score = Scorer.calculate_score(cards)
        # Sentinel at pos 0: 0 (adjacent to Sentinel) + 4 (adjacent to Fort at pos 5) = 4
        # Sentinel at pos 1: 0 (adjacent to Sentinel) + 4 (adjacent to Fort at pos 2) + 4 (adjacent to Fort at pos 6) = 8
        # Total: 12
        assert score['Sentinel'] == 12
    
    def test_sentinel_adjacent_to_fort_bonus(self):
        """Sentinel adjacent to Fort = +4 bonus per Fort"""
        # Sentinel at pos 0, Fort at pos 1 (adjacent right) and pos 5 (adjacent down)
        cards = ['Sentinel', 'Fort', 'Fort', 'Fort', 'Fort',
                 'Fort', 'Fort', 'Fort', 'Fort', 'Fort']
        score = Scorer.calculate_score(cards)
        # Base: 3 (not adjacent to Sentinel) + Bonus: 4 (Fort at pos 1) + 4 (Fort at pos 5) = 11
        assert score['Sentinel'] == 11
    
    def test_sentinel_adjacent_to_two_forts(self):
        """Sentinel adjacent to 3 Forts = +12 bonus"""
        # Sentinel at pos 1, Fort at pos 0, 2, and 6 (adjacent left, right, and down)
        cards = ['Fort', 'Sentinel', 'Fort', 'Fort', 'Fort',
                 'Fort', 'Fort', 'Fort', 'Fort', 'Fort']
        score = Scorer.calculate_score(cards)
        # Base: 3 + Bonus: 4 + 4 + 4 = 15
        assert score['Sentinel'] == 15


class TestFortScoring:
    """Test Fort scoring rules (Req 7.5)"""
    
    def test_fort_at_corners_scores_6(self):
        """Fort at corner positions (0, 4, 5, 9) = +6 points each"""
        cards = ['Fort', 'Mountain', 'Mountain', 'Mountain', 'Fort',
                 'Fort', 'Mountain', 'Mountain', 'Mountain', 'Fort']
        score = Scorer.calculate_score(cards)
        assert score['Fort'] == 24  # 6 * 4
    
    def test_fort_at_non_corners_scores_0(self):
        """Fort at non-corner positions = 0 points"""
        cards = ['Mountain', 'Fort', 'Fort', 'Fort', 'Mountain',
                 'Mountain', 'Fort', 'Fort', 'Fort', 'Mountain']
        score = Scorer.calculate_score(cards)
        assert score['Fort'] == 0


class TestMonkScoring:
    """Test Monk scoring rules (Req 7.6)"""
    
    def test_monk_in_hand_scores_5(self):
        """Monk in Hand (positions 5-9) = +5 points"""
        cards = ['Fort', 'Fort', 'Fort', 'Fort', 'Fort',
                 'Monk', 'Monk', 'Monk', 'Fort', 'Fort']
        score = Scorer.calculate_score(cards)
        assert score['Monk'] == 15  # 5 * 3
    
    def test_monk_in_line_scores_0(self):
        """Monk in Line (positions 0-4) = 0 points"""
        cards = ['Monk', 'Monk', 'Monk', 'Fort', 'Fort',
                 'Fort', 'Fort', 'Fort', 'Fort', 'Fort']
        score = Scorer.calculate_score(cards)
        assert score['Monk'] == 0
    
    def test_monk_adjacent_to_torii_bonus(self):
        """Monk adjacent to Torii = +2 bonus per Torii"""
        # Monk at pos 5, Torii at pos 0 (adjacent up)
        cards = ['Torii', 'Fort', 'Fort', 'Fort', 'Fort',
                 'Monk', 'Fort', 'Fort', 'Fort', 'Fort']
        score = Scorer.calculate_score(cards)
        # Base: 5 (in hand) + Bonus: 2 (adjacent to Torii) = 7
        assert score['Monk'] == 7
    
    def test_monk_adjacent_to_two_torii(self):
        """Monk adjacent to 2 Torii = +4 bonus"""
        # Monk at pos 6, Torii at pos 1 and 5 (adjacent up and left)
        cards = ['Fort', 'Torii', 'Fort', 'Fort', 'Fort',
                 'Torii', 'Monk', 'Fort', 'Fort', 'Fort']
        score = Scorer.calculate_score(cards)
        # Base: 5 + Bonus: 2 + 2 = 9
        assert score['Monk'] == 9


class TestToriiScoring:
    """Test Torii scoring rules (Req 7.7)"""
    
    def test_one_torii_scores_minus_5(self):
        """1 Torii = -5 points"""
        cards = ['Torii', 'Fort', 'Fort', 'Fort', 'Fort',
                 'Fort', 'Fort', 'Fort', 'Fort', 'Fort']
        score = Scorer.calculate_score(cards)
        assert score['Torii'] == -5
    
    def test_two_torii_scores_0(self):
        """2 Torii = 0 points"""
        cards = ['Torii', 'Torii', 'Fort', 'Fort', 'Fort',
                 'Fort', 'Fort', 'Fort', 'Fort', 'Fort']
        score = Scorer.calculate_score(cards)
        assert score['Torii'] == 0
    
    def test_three_torii_scores_30(self):
        """3+ Torii = +30 points total"""
        cards = ['Torii', 'Torii', 'Torii', 'Fort', 'Fort',
                 'Fort', 'Fort', 'Fort', 'Fort', 'Fort']
        score = Scorer.calculate_score(cards)
        assert score['Torii'] == 30
    
    def test_four_torii_scores_30(self):
        """4 Torii = +30 points total (no additional bonus)"""
        cards = ['Torii', 'Torii', 'Torii', 'Torii', 'Fort',
                 'Fort', 'Fort', 'Fort', 'Fort', 'Fort']
        score = Scorer.calculate_score(cards)
        assert score['Torii'] == 30


class TestKnightScoring:
    """Test Knight scoring rules (Req 7.8)"""
    
    def test_knight_in_hand_scores_3(self):
        """Knight in Hand (positions 5-9) = +3 points"""
        cards = ['Fort', 'Fort', 'Fort', 'Fort', 'Fort',
                 'Knight', 'Knight', 'Fort', 'Fort', 'Fort']
        score = Scorer.calculate_score(cards)
        assert score['Knight'] == 6  # 3 * 2
    
    def test_knight_in_line_scores_0(self):
        """Knight in Line (positions 0-4) = 0 points"""
        cards = ['Knight', 'Knight', 'Fort', 'Fort', 'Fort',
                 'Fort', 'Fort', 'Fort', 'Fort', 'Fort']
        score = Scorer.calculate_score(cards)
        assert score['Knight'] == 0
    
    def test_knight_directly_below_banner_bonus(self):
        """Knight directly below Banner = +10 bonus"""
        # Banner at pos 2 (Line), Knight at pos 7 (Hand, same column)
        cards = ['Fort', 'Fort', 'Banner', 'Fort', 'Fort',
                 'Fort', 'Fort', 'Knight', 'Fort', 'Fort']
        score = Scorer.calculate_score(cards)
        # Base: 3 (in hand) + Bonus: 10 (below Banner) = 13
        assert score['Knight'] == 13
    
    def test_knight_not_below_banner_no_bonus(self):
        """Knight not directly below Banner = no bonus"""
        # Banner at pos 2, Knight at pos 6 (different column)
        cards = ['Fort', 'Fort', 'Banner', 'Fort', 'Fort',
                 'Fort', 'Knight', 'Fort', 'Fort', 'Fort']
        score = Scorer.calculate_score(cards)
        assert score['Knight'] == 3  # Only base score


class TestBannerScoring:
    """Test Banner scoring rules (Req 7.9)"""
    
    def test_one_banner_scores_3(self):
        """1 Banner = +3 points"""
        cards = ['Banner', 'Fort', 'Fort', 'Fort', 'Fort',
                 'Fort', 'Fort', 'Fort', 'Fort', 'Fort']
        score = Scorer.calculate_score(cards)
        assert score['Banner'] == 3
    
    def test_two_banners_scores_8(self):
        """2 Banners = +8 points total"""
        cards = ['Banner', 'Banner', 'Fort', 'Fort', 'Fort',
                 'Fort', 'Fort', 'Fort', 'Fort', 'Fort']
        score = Scorer.calculate_score(cards)
        assert score['Banner'] == 8
    
    def test_three_banners_scores_8(self):
        """3+ Banners = +8 points total (no additional bonus)"""
        cards = ['Banner', 'Banner', 'Banner', 'Fort', 'Fort',
                 'Fort', 'Fort', 'Fort', 'Fort', 'Fort']
        score = Scorer.calculate_score(cards)
        assert score['Banner'] == 8


class TestRiceFieldsScoring:
    """Test Rice Fields scoring rules (Req 7.10)"""
    
    def test_one_rice_field_alone_scores_0(self):
        """1 Rice Field alone = 0 points"""
        cards = ['Rice fields', 'Fort', 'Fort', 'Fort', 'Fort',
                 'Fort', 'Fort', 'Fort', 'Fort', 'Fort']
        score = Scorer.calculate_score(cards)
        assert score['Rice fields'] == 0
    
    def test_two_connected_rice_fields_score_10(self):
        """2 connected Rice Fields = +10 points"""
        # Rice fields at pos 0 and 1 (adjacent)
        cards = ['Rice fields', 'Rice fields', 'Fort', 'Fort', 'Fort',
                 'Fort', 'Fort', 'Fort', 'Fort', 'Fort']
        score = Scorer.calculate_score(cards)
        assert score['Rice fields'] == 10
    
    def test_three_connected_rice_fields_score_20(self):
        """3 connected Rice Fields = +20 points"""
        # Rice fields at pos 0, 1, 2 (all adjacent)
        cards = ['Rice fields', 'Rice fields', 'Rice fields', 'Fort', 'Fort',
                 'Fort', 'Fort', 'Fort', 'Fort', 'Fort']
        score = Scorer.calculate_score(cards)
        assert score['Rice fields'] == 20
    
    def test_four_connected_rice_fields_score_30(self):
        """4+ connected Rice Fields = +30 points (maximum)"""
        # Rice fields at pos 0, 1, 2, 3 (all adjacent)
        cards = ['Rice fields', 'Rice fields', 'Rice fields', 'Rice fields', 'Fort',
                 'Fort', 'Fort', 'Fort', 'Fort', 'Fort']
        score = Scorer.calculate_score(cards)
        assert score['Rice fields'] == 30
    
    def test_five_connected_rice_fields_score_30(self):
        """5 connected Rice Fields = +30 points (still maximum)"""
        # Rice fields at pos 0, 1, 2, 5, 6 (all connected)
        cards = ['Rice fields', 'Rice fields', 'Rice fields', 'Fort', 'Fort',
                 'Rice fields', 'Rice fields', 'Fort', 'Fort', 'Fort']
        score = Scorer.calculate_score(cards)
        assert score['Rice fields'] == 30
    
    def test_two_separate_rice_field_groups(self):
        """Two separate groups score independently"""
        # Group 1: pos 0, 1 (2 connected = 10)
        # Group 2: pos 8, 9 (2 connected = 10)
        # Total: 20
        cards = ['Rice fields', 'Rice fields', 'Fort', 'Fort', 'Fort',
                 'Fort', 'Fort', 'Fort', 'Rice fields', 'Rice fields']
        score = Scorer.calculate_score(cards)
        assert score['Rice fields'] == 20
    
    def test_rice_fields_vertical_connection(self):
        """Rice Fields connect vertically (up/down)"""
        # Rice fields at pos 2 and 7 (vertically adjacent)
        cards = ['Fort', 'Fort', 'Rice fields', 'Fort', 'Fort',
                 'Fort', 'Fort', 'Rice fields', 'Fort', 'Fort']
        score = Scorer.calculate_score(cards)
        assert score['Rice fields'] == 10


class TestRoninScoring:
    """Test Ronin scoring rules (Req 7.11)"""
    
    def test_ronin_with_8_unique_types_scores_8_per_ronin(self):
        """Ronin with 8 unique types (excluding Mountain) = +8 per Ronin"""
        # 8 unique: Ronin, Fort, Torii, Banner, Naishi, Councellor, Sentinel, Monk
        cards = ['Ronin', 'Fort', 'Torii', 'Banner', 'Naishi',
                 'Councellor', 'Sentinel', 'Monk', 'Ronin', 'Mountain']
        score = Scorer.calculate_score(cards)
        assert score['Ronin'] == 16  # 8 * 2 Ronins
    
    def test_ronin_with_9_unique_types_scores_15_per_ronin(self):
        """Ronin with 9 unique types = +15 per Ronin"""
        # 9 unique: Ronin, Fort, Torii, Banner, Naishi, Councellor, Sentinel, Monk, Knight
        cards = ['Ronin', 'Fort', 'Torii', 'Banner', 'Naishi',
                 'Councellor', 'Sentinel', 'Monk', 'Knight', 'Ronin']
        score = Scorer.calculate_score(cards)
        assert score['Ronin'] == 30  # 15 * 2 Ronins
    
    def test_ronin_with_10_unique_types_scores_45_per_ronin(self):
        """Ronin with 10 unique types = +45 per Ronin"""
        # 10 unique: all cards except Mountain
        cards = ['Ronin', 'Fort', 'Torii', 'Banner', 'Naishi',
                 'Councellor', 'Sentinel', 'Monk', 'Knight', 'Rice fields']
        score = Scorer.calculate_score(cards)
        assert score['Ronin'] == 45  # 45 * 1 Ronin
    
    def test_ronin_with_fewer_than_8_unique_scores_0(self):
        """Ronin with fewer than 8 unique types = 0 points"""
        # Only 7 unique: Ronin, Fort, Torii, Banner, Naishi, Councellor, Sentinel
        cards = ['Ronin', 'Fort', 'Torii', 'Banner', 'Naishi',
                 'Councellor', 'Sentinel', 'Fort', 'Torii', 'Banner']
        score = Scorer.calculate_score(cards)
        assert score['Ronin'] == 0

    def test_ronin_mountain_not_counted_as_unique(self):
        """Mountain is not counted toward unique types for Ronin"""
        # 7 unique (excluding Mountain): Ronin, Fort, Torii, Banner, Naishi, Councellor, Sentinel
        cards = ['Ronin', 'Fort', 'Torii', 'Banner', 'Naishi',
                 'Councellor', 'Sentinel', 'Mountain', 'Mountain', 'Mountain']
        score = Scorer.calculate_score(cards)
        assert score['Ronin'] == 0  # Only 7 unique, need 8+


class TestNinjaHandling:
    """Test Ninja copying mechanics (Req 7.12)"""
    
    def test_ninja_copies_character_card(self):
        """Ninja can copy a character card"""
        cards = ['Ninja', 'Naishi', 'Fort', 'Fort', 'Fort',
                 'Fort', 'Fort', 'Fort', 'Fort', 'Fort']
        
        # Ninja at pos 0 copies Naishi at pos 1
        def ninja_choice(pos, cards_list):
            return 1  # Choose Naishi
        
        working_cards = Scorer.handle_ninjas(cards, CHARACTERS, ninja_choice)
        assert working_cards[0] == 'Naishi'
        assert working_cards[1] == 'Naishi'
    
    def test_ninja_cannot_copy_building(self):
        """Ninja cannot copy building cards"""
        cards = ['Ninja', 'Fort', 'Naishi', 'Fort', 'Fort',
                 'Fort', 'Fort', 'Fort', 'Fort', 'Fort']
        
        # Try to copy Fort (invalid), should retry and get Naishi
        attempts = [1, 2]  # First try Fort (invalid), then Naishi (valid)
        attempt_idx = [0]
        
        def ninja_choice(pos, cards_list):
            idx = attempts[attempt_idx[0]]
            attempt_idx[0] += 1
            return idx
        
        working_cards = Scorer.handle_ninjas(cards, CHARACTERS, ninja_choice)
        assert working_cards[0] == 'Naishi'
    
    def test_ninja_cannot_copy_another_ninja(self):
        """Ninja cannot copy another Ninja"""
        cards = ['Ninja', 'Ninja', 'Naishi', 'Fort', 'Fort',
                 'Fort', 'Fort', 'Fort', 'Fort', 'Fort']
        
        # Try to copy other Ninja (invalid), should retry and get Naishi
        # Both Ninjas will be processed, so we need 4 attempts total
        attempts = [1, 2, 0, 2]  # Ninja 0: try pos 1 (Ninja, invalid), then pos 2 (Naishi, valid)
                                  # Ninja 1: try pos 0 (Naishi now), then pos 2 (Naishi, valid)
        attempt_idx = [0]
        
        def ninja_choice(pos, cards_list):
            idx = attempts[attempt_idx[0]]
            attempt_idx[0] += 1
            return idx
        
        working_cards = Scorer.handle_ninjas(cards, CHARACTERS, ninja_choice)
        assert working_cards[0] == 'Naishi'
        assert working_cards[1] == 'Naishi'
    
    def test_ninja_with_no_valid_characters_stays_ninja(self):
        """Ninja with no valid characters to copy stays as Ninja (scores 0)"""
        cards = ['Ninja', 'Fort', 'Fort', 'Fort', 'Fort',
                 'Fort', 'Fort', 'Fort', 'Fort', 'Fort']
        
        def ninja_choice(pos, cards_list):
            return 1  # Doesn't matter, no valid characters
        
        working_cards = Scorer.handle_ninjas(cards, CHARACTERS, ninja_choice)
        assert working_cards[0] == 'Ninja'  # Stays as Ninja

    def test_ninja_scores_as_copied_card(self):
        """Ninja scores as the card it copies"""
        # Ninja copies Naishi at position 2 (should score 12)
        cards = ['Fort', 'Fort', 'Ninja', 'Fort', 'Fort',
                 'Fort', 'Fort', 'Naishi', 'Fort', 'Fort']
        
        def ninja_choice(pos, cards_list):
            return 7  # Copy Naishi
        
        working_cards = Scorer.handle_ninjas(cards, CHARACTERS, ninja_choice)
        score = Scorer.calculate_score(working_cards)
        # Ninja at pos 2 becomes Naishi, scores 12
        assert score['Naishi'] == 20  # 12 (copied) + 8 (original at pos 7)
    
    def test_two_ninjas_copy_independently(self):
        """Two Ninjas can copy different cards"""
        cards = ['Ninja', 'Naishi', 'Fort', 'Fort', 'Fort',
                 'Fort', 'Fort', 'Fort', 'Fort', 'Ninja']
        
        ninja_positions = []
        
        def ninja_choice(pos, cards_list):
            ninja_positions.append(pos)
            if pos == 0:
                return 1  # First Ninja copies Naishi
            else:  # pos == 9
                return 1  # Second Ninja also copies Naishi
        
        working_cards = Scorer.handle_ninjas(cards, CHARACTERS, ninja_choice)
        assert working_cards[0] == 'Naishi'
        assert working_cards[9] == 'Naishi'
        assert len(ninja_positions) == 2


class TestTiebreaker:
    """Test tiebreaker rules (Req 1.8)"""
    
    def test_higher_score_wins(self):
        """Player with higher score wins"""
        cards1 = ['Fort', 'Fort', 'Fort', 'Fort', 'Fort',
                  'Fort', 'Fort', 'Fort', 'Fort', 'Fort']
        cards2 = ['Mountain', 'Fort', 'Fort', 'Fort', 'Fort',
                  'Fort', 'Fort', 'Fort', 'Fort', 'Fort']
        
        score1 = Scorer.calculate_score(cards1)['Total']
        score2 = Scorer.calculate_score(cards2)['Total']
        
        winner = Scorer.determine_winner(score1, score2, cards1, cards2)
        # Player 1: 24 (4 Forts at corners), Player 2: 23 (3 Forts at corners + 5 Mountain - 6 for missing corner)
        assert winner == 0  # Player 1 wins (higher score)
    
    def test_tiebreaker_most_unique_cards(self):
        """On tie, player with most unique cards wins (excluding Mountain and Ninja)"""
        # Both score 1 point
        cards1 = ['Mountain', 'Mountain', 'Mountain', 'Mountain', 'Fort',
                  'Mountain', 'Mountain', 'Mountain', 'Mountain', 'Mountain']
        cards2 = ['Sentinel', 'Mountain', 'Mountain', 'Mountain', 'Mountain', 
                  'Knight', 'Mountain', 'Mountain', 'Mountain', 'Mountain']
        
        score1 = Scorer.calculate_score(cards1)['Total']
        score2 = Scorer.calculate_score(cards2)['Total']
        
        winner = Scorer.determine_winner(score1, score2, cards1, cards2)
        # Both score 1, Player 2 has 2 unique (Sentinel, Knight) vs Player 1 has 1 unique (Fort)
        assert winner == 1  # Player 2 has more unique
    
    def test_true_tie(self):
        """True tie when scores and unique counts are equal"""
        cards1 = ['Fort', 'Fort', 'Fort', 'Fort', 'Fort',
                  'Fort', 'Fort', 'Fort', 'Fort', 'Fort']
        cards2 = ['Fort', 'Fort', 'Fort', 'Fort', 'Fort',
                  'Fort', 'Fort', 'Fort', 'Fort', 'Fort']
        
        score1 = Scorer.calculate_score(cards1)['Total']
        score2 = Scorer.calculate_score(cards2)['Total']
        
        winner = Scorer.determine_winner(score1, score2, cards1, cards2)
        assert winner == -1  # True tie

    def test_tiebreaker_excludes_mountain(self):
        """Tiebreaker excludes Mountain from unique count"""
        # Both score 1 point, many Mountains
        cards1 = ['Mountain', 'Mountain', 'Mountain', 'Mountain', 'Fort',
                  'Mountain', 'Mountain', 'Mountain', 'Mountain', 'Mountain']
        cards2 = ['Sentinel', 'Mountain', 'Mountain', 'Mountain', 'Mountain', 
                  'Knight', 'Mountain', 'Mountain', 'Mountain', 'Mountain']
        
        score1 = Scorer.calculate_score(cards1)['Total']
        score2 = Scorer.calculate_score(cards2)['Total']
        
        winner = Scorer.determine_winner(score1, score2, cards1, cards2)
        # Player 1: 1 unique (Fort), Player 2: 2 unique (Sentinel, Knight)
        # Mountain is excluded from unique count
        assert winner == 1
    
    def test_tiebreaker_excludes_ninja(self):
        """Tiebreaker excludes Ninja from unique count"""
        # 3 Torii equals 4 rice fields, both have Ninja, no character cards
        cards1 = ['Mountain', 'Mountain', 'Ninja', 'Mountain', 'Mountain',
                  'Torii', 'Torii', 'Torii', 'Mountain', 'Mountain']
        cards2 = ['Mountain', 'Mountain', 'Ninja', 'Mountain', 'Mountain',
                  'Rice fields', 'Rice fields', 'Rice fields', 'Rice fields', 'Mountain']
        
        score1 = Scorer.calculate_score(cards1)['Total']
        score2 = Scorer.calculate_score(cards2)['Total']
        
        winner = Scorer.determine_winner(score1, score2, cards1, cards2)
        # Both score 25 (30 from Torii/Rice - 5 from Mountains)
        # Player 1: 1 unique (Torii), Player 2: 1 unique (Rice fields)
        # Ninja is excluded from unique count - true tie
        assert winner == -1  # True tie (same unique count)


class TestComplexScenarios:
    """Test complex scoring scenarios with multiple card interactions"""
    
    def test_full_game_scenario_1(self):
        """Test a realistic full game scenario"""
        # Player has: Naishi at pos 2, Councellor at pos 1 (adjacent to Naishi),
        # Fort at corners, Monk in hand adjacent to Torii
        cards = ['Fort', 'Councellor', 'Naishi', 'Fort', 'Fort',
                 'Torii', 'Monk', 'Fort', 'Fort', 'Fort']
        
        score = Scorer.calculate_score(cards)
        
        # Expected scores:
        # Naishi: 12 (pos 2)
        # Councellor: 4 (pos 1) + 4 (adjacent to Naishi) = 8
        # Fort: 6 (pos 0) + 6 (pos 4) + 6 (pos 9) = 18
        # Monk: 5 (in hand) + 2 (adjacent to Torii at pos 5) = 7
        # Torii: -5 (only 1)
        # Total: 12 + 8 + 18 + 7 - 5 = 40
        
        assert score['Naishi'] == 12
        assert score['Councellor'] == 8
        assert score['Fort'] == 18
        assert score['Monk'] == 7
        assert score['Torii'] == -5
        assert score['Total'] == 40
    
    def test_full_game_scenario_2(self):
        """Test another realistic scenario with Rice Fields"""
        # Connected Rice Fields group of 3, Knight below Banner, Sentinel adjacent to Fort
        cards = ['Rice fields', 'Rice fields', 'Banner', 'Fort', 'Sentinel',
                 'Rice fields', 'Fort', 'Knight', 'Fort', 'Fort']
        
        score = Scorer.calculate_score(cards)
        
        # Expected scores:
        # Rice fields: 20 (3 connected: pos 0, 1, 5)
        # Banner: 3 (only 1)
        # Fort: 6 (pos 9 corner)
        # Sentinel: 3 (not adjacent to Sentinel) + 4 (adjacent to Fort at pos 3) + 4 (adjacent to Fort at pos 9) = 11
        # Knight: 3 (in hand) + 10 (below Banner at pos 2, same column) = 13
        # Total: 20 + 3 + 6 + 11 + 13 = 53
        
        assert score['Rice fields'] == 20
        assert score['Banner'] == 3
        assert score['Fort'] == 6
        assert score['Sentinel'] == 11
        assert score['Knight'] == 13  # Gets bonus, IS below Banner
        assert score['Total'] == 53

    def test_maximum_score_scenario(self):
        """Test a high-scoring scenario"""
        # Optimized for high score: Naishi at pos 2, 3 Torii, 4 connected Rice Fields,
        # Knight in hand (not below Banner at pos 3)
        cards = ['Rice fields', 'Rice fields', 'Naishi', 'Banner', 'Torii',
                 'Rice fields', 'Rice fields', 'Knight', 'Torii', 'Torii']
        
        score = Scorer.calculate_score(cards)
        
        # Expected scores:
        # Naishi: 12 (pos 2)
        # Rice fields: 30 (4 connected: pos 0, 1, 5, 6)
        # Banner: 3 (only 1)
        # Torii: 30 (3 Torii)
        # Knight: 3 (in hand, not below Banner since Banner is at pos 3, Knight at pos 7)
        # Total: 12 + 30 + 3 + 30 + 3 = 78
        
        assert score['Naishi'] == 12
        assert score['Rice fields'] == 30
        assert score['Banner'] == 3
        assert score['Torii'] == 30
        assert score['Knight'] == 3
        assert score['Total'] == 78


class TestEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_all_mountains(self):
        """All cards are Mountains"""
        cards = ['Mountain'] * 10
        score = Scorer.calculate_score(cards)
        assert score['Mountain'] == -5
        assert score['Total'] == -5
    
    def test_all_same_building(self):
        """All cards are the same building"""
        cards = ['Fort'] * 10
        score = Scorer.calculate_score(cards)
        # Only corners score: 4 * 6 = 24
        assert score['Fort'] == 24
        assert score['Total'] == 24
    
    def test_sentinel_chain_all_adjacent(self):
        """Multiple Sentinels all adjacent to each other lose base score but keep Fort bonuses"""
        cards = ['Sentinel', 'Sentinel', 'Sentinel', 'Sentinel', 'Sentinel',
                 'Fort', 'Fort', 'Fort', 'Fort', 'Fort']
        score = Scorer.calculate_score(cards)
        # All Sentinels are adjacent to at least one other Sentinel (lose base 3)
        # But they still get Fort bonuses from adjacent Forts below
        # Each Sentinel at pos 0-4 is adjacent to Fort below = +4 each = 20 total
        assert score['Sentinel'] == 20
    
    def test_rice_fields_complex_pattern(self):
        """Complex Rice Fields pattern with multiple groups"""
        # Group 1: pos 0, 5 (2 connected = 10)
        # Group 2: pos 2, 3, 7, 8 (4 connected = 30)
        # Total: 40
        cards = ['Rice fields', 'Fort', 'Rice fields', 'Rice fields', 'Fort',
                 'Rice fields', 'Fort', 'Rice fields', 'Rice fields', 'Fort']
        score = Scorer.calculate_score(cards)
        assert score['Rice fields'] == 40
    
    def test_total_score_calculation(self):
        """Verify Total is sum of all card scores"""
        cards = ['Mountain', 'Naishi', 'Fort', 'Fort', 'Fort',
                 'Fort', 'Fort', 'Fort', 'Fort', 'Fort']
        score = Scorer.calculate_score(cards)
        
        # Calculate expected total
        expected_total = (score['Mountain'] + score['Naishi'] + score['Councellor'] +
                         score['Sentinel'] + score['Fort'] + score['Monk'] +
                         score['Torii'] + score['Knight'] + score['Banner'] +
                         score['Rice fields'] + score['Ronin'] + score['Ninja'])
        
        assert score['Total'] == expected_total


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
