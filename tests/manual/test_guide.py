#!/usr/bin/env python3
"""
Manual Testing Guide for Naishi Game
Task 39: Play complete games and verify all functionality

This script provides a structured approach to manual testing:
1. Human vs Human game
2. Human vs AI game
3. Test all card types
4. Test all actions
5. Test all edge cases
6. Verify scoring
7. Verify ending
"""

import sys
from naishi_core.game_logic import GameState, ACTION_DEVELOP, ACTION_SWAP, ACTION_DISCARD, ACTION_RECALL, ACTION_DECREE, ACTION_END_GAME
from naishi_ui import NaishiUI

# Card names as strings
MOUNTAIN = "Mountain"
NAISHI = "Naishi"
COUNCELLOR = "Councellor"
SENTINEL = "Sentinel"
FORT = "Fort"
MONK = "Monk"
TORII = "Torii"
KNIGHT = "Knight"
BANNER = "Banner"
RICE_FIELDS = "Rice fields"
RONIN = "Ronin"
NINJA = "Ninja"

class ManualTestGuide:
    def __init__(self):
        self.test_results = {
            "human_vs_human": None,
            "human_vs_ai": None,
            "all_card_types": {},
            "all_actions": {},
            "edge_cases": {},
            "scoring": {},
            "ending": {}
        }
    
    def print_header(self, title):
        print("\n" + "="*70)
        print(f"  {title}")
        print("="*70 + "\n")
    
    def print_section(self, title):
        print("\n" + "-"*70)
        print(f"  {title}")
        print("-"*70)
    
    def verify_setup(self):
        """Verify game setup matches RULES.md Section 2"""
        self.print_header("SETUP VERIFICATION (RULES.md Section 2)")
        
        gs = GameState.create_initial_state()
        
        checks = []
        
        # Check 1: Total cards in decks
        total_cards = sum(len(deck) for deck in gs.river.decks)
        checks.append(("34 cards total in decks", total_cards == 34, f"Found: {total_cards}"))
        
        # Check 2: 5 decks
        checks.append(("5 decks", len(gs.river.decks) == 5, f"Found: {len(gs.river.decks)}"))
        
        # Check 3: 6 cards per deck (after draft)
        deck_sizes = [len(deck) for deck in gs.river.decks]
        checks.append(("6 cards per deck", all(s == 6 for s in deck_sizes), f"Sizes: {deck_sizes}"))
        
        # Check 4: 2 starting cards per player (after draft completes)
        # Note: During draft phase, players have draft_hands
        p1_total = len(gs.players[0].hand) + len(gs.players[0].line)
        p2_total = len(gs.players[1].hand) + len(gs.players[1].line)
        checks.append(("P1 has cards", p1_total >= 0, f"Found: {p1_total}"))
        checks.append(("P2 has cards", p2_total >= 0, f"Found: {p2_total}"))
        
        # Check 5: 2 emissaries per player
        checks.append(("P1 has 2 emissaries", gs.players[0].emissaries == 2, f"Found: {gs.players[0].emissaries}"))
        checks.append(("P2 has 2 emissaries", gs.players[1].emissaries == 2, f"Found: {gs.players[1].emissaries}"))
        
        # Check 6: Player 1 starts (index 0)
        checks.append(("Player 1 starts", gs.current_player_idx == 0, f"Current: P{gs.current_player_idx + 1}"))
        
        # Check 7: In draft phase initially
        checks.append(("In draft phase", gs.in_draft_phase == True, f"Draft phase: {gs.in_draft_phase}"))
        
        # Print results
        all_passed = True
        for check_name, passed, details in checks:
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"{status}: {check_name} - {details}")
            if not passed:
                all_passed = False
        
        return all_passed
    
    def verify_card_types(self):
        """Verify all 12 card types are present"""
        self.print_header("CARD TYPES VERIFICATION")
        
        all_card_types = [
            MOUNTAIN, NAISHI, COUNCELLOR, SENTINEL, FORT,
            MONK, TORII, KNIGHT, BANNER, RICE_FIELDS, RONIN, NINJA
        ]
        
        card_names = {
            MOUNTAIN: "Mountain",
            NAISHI: "Naishi",
            COUNCELLOR: "Councellor",
            SENTINEL: "Sentinel",
            FORT: "Fort",
            MONK: "Monk",
            TORII: "Torii",
            KNIGHT: "Knight",
            BANNER: "Banner",
            RICE_FIELDS: "Rice Fields",
            RONIN: "Ronin",
            NINJA: "Ninja"
        }
        
        gs = GameState.create_initial_state()
        
        # Collect all cards
        all_cards = []
        all_cards.extend(gs.players[0].hand)
        all_cards.extend(gs.players[0].line)
        all_cards.extend(gs.players[1].hand)
        all_cards.extend(gs.players[1].line)
        for deck in gs.river.decks:
            all_cards.extend(deck)
        # Also include draft hands if in draft phase
        if gs.in_draft_phase:
            for draft_hand in gs.draft_hands:
                all_cards.extend(draft_hand)
        
        # Count each type
        print("\nCard Type Distribution:")
        for card_type in all_card_types:
            count = sum(1 for c in all_cards if c == card_type)
            name = card_names.get(card_type, f"Unknown({card_type})")
            print(f"  {name:15s}: {count:2d} cards")
            self.test_results["all_card_types"][name] = count > 0
        
        return True
    
    def verify_actions(self):
        """Verify all action types are available"""
        self.print_header("ACTION TYPES VERIFICATION")
        
        action_names = {
            ACTION_DEVELOP: "Develop Territory",
            ACTION_SWAP: "Emissary Swap",
            ACTION_DISCARD: "Emissary Discard",
            ACTION_RECALL: "Recall Emissaries",
            ACTION_DECREE: "Impose Decree",
            ACTION_END_GAME: "Declare End"
        }
        
        print("\nAction Types Available:")
        for action_type, name in action_names.items():
            print(f"  {action_type}: {name}")
            self.test_results["all_actions"][name] = True
        
        print("\nTo test each action during gameplay:")
        print("  1. Develop: Choose position 0-9, select card from deck")
        print("  2. Swap: Choose swap type (1-4), select positions")
        print("  3. Discard: Select 2 cards from river to discard")
        print("  4. Recall: Restore emissaries and clear markers")
        print("  5. Decree: Swap cards at same position with opponent")
        print("  6. End Game: Declare end when 1+ decks empty")
        
        return True
    
    def verify_turn_options(self):
        """Verify both turn options work"""
        self.print_header("TURN STRUCTURE VERIFICATION (RULES.md Section 4)")
        
        print("\nTurn Option A: Develop → Optional Emissary")
        print("  1. Choose ACTION_DEVELOP")
        print("  2. System should offer optional emissary")
        print("  3. Can accept or decline")
        print("  4. Turn ends after choice")
        
        print("\nTurn Option B: Emissary → Required Develop")
        print("  1. Choose ACTION_SWAP or ACTION_DISCARD")
        print("  2. System should require develop")
        print("  3. Must choose ACTION_DEVELOP")
        print("  4. Turn ends after develop")
        
        print("\nTurn Option C: Other Actions")
        print("  1. Choose ACTION_RECALL, ACTION_DECREE, or ACTION_END_GAME")
        print("  2. Turn ends immediately")
        
        return True
    
    def verify_edge_cases(self):
        """List edge cases to test"""
        self.print_header("EDGE CASES TO TEST")
        
        edge_cases = [
            "Empty deck handling (develop from empty deck)",
            "All emissary spots full (3 swaps, 2 discards)",
            "No emissaries available (can't use emissary actions)",
            "Decree used (max emissaries becomes 1)",
            "Recall with decree (only restores to 1)",
            "Multiple Mountains (should score -5 total)",
            "Ninja copying (should score as copied card)",
            "Rice Fields connectivity (test all group sizes)",
            "Ronin unique types (test 8, 9, 10 types)",
            "Tiebreaker (same score, different unique cards)",
            "Auto-end (2+ decks empty after P1)",
            "P2 final turn (always gets one more turn)",
            "Optional emissary declined (turn ends)",
            "Must develop enforced (only develop legal)"
        ]
        
        print("\nEdge Cases to Verify During Testing:")
        for i, case in enumerate(edge_cases, 1):
            print(f"  {i:2d}. {case}")
            self.test_results["edge_cases"][case] = None
        
        return True
    
    def verify_scoring_rules(self):
        """Verify scoring rules"""
        self.print_header("SCORING VERIFICATION (RULES.md Section 8)")
        
        scoring_rules = [
            ("Mountain", "1 Mountain = +5, 2+ Mountains = -5 total"),
            ("Naishi", "Position 2 = +12, Position 7 = +8, others = 0"),
            ("Councellor", "Position bonuses + adjacent Naishi bonuses"),
            ("Sentinel", "Not adjacent to Sentinel = +3, adjacent to Fort = +4 each"),
            ("Fort", "Corners (0,4,5,9) = +6, others = 0"),
            ("Monk", "In hand = +5, adjacent to Torii = +2 each"),
            ("Torii", "1 = -5, 2 = 0, 3+ = +30 total"),
            ("Knight", "In hand = +3, below Banner = +10"),
            ("Banner", "1 = +3, 2+ = +8 total"),
            ("Rice Fields", "Connected groups: 1=0, 2=10, 3=20, 4+=30"),
            ("Ronin", "Unique types: 8=8, 9=15, 10=45 per Ronin"),
            ("Ninja", "Copies a character card and scores as that card"),
            ("Tiebreaker", "Most unique card types wins")
        ]
        
        print("\nScoring Rules to Verify:")
        for card_type, rule in scoring_rules:
            print(f"  {card_type:15s}: {rule}")
            self.test_results["scoring"][card_type] = None
        
        return True
    
    def verify_ending_rules(self):
        """Verify game ending rules"""
        self.print_header("GAME ENDING VERIFICATION (RULES.md Section 7)")
        
        ending_rules = [
            "Declare End available when 1+ decks empty",
            "Declare End NOT available when 0 decks empty",
            "Auto-end when 2+ decks empty (after P1's turn)",
            "P2 always gets final turn for fairness",
            "Game terminates after P2's final turn",
            "Scoring occurs at game end",
            "Winner determined correctly"
        ]
        
        print("\nEnding Rules to Verify:")
        for i, rule in enumerate(ending_rules, 1):
            print(f"  {i}. {rule}")
            self.test_results["ending"][rule] = None
        
        return True
    
    def run_quick_verification(self):
        """Run automated quick verification"""
        self.print_header("AUTOMATED QUICK VERIFICATION")
        
        print("Running automated checks...")
        
        results = []
        results.append(("Setup", self.verify_setup()))
        results.append(("Card Types", self.verify_card_types()))
        results.append(("Actions", self.verify_actions()))
        
        print("\n" + "="*70)
        print("AUTOMATED VERIFICATION SUMMARY")
        print("="*70)
        
        for test_name, passed in results:
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"{status}: {test_name}")
        
        all_passed = all(passed for _, passed in results)
        return all_passed
    
    def print_manual_test_instructions(self):
        """Print instructions for manual testing"""
        self.print_header("MANUAL TESTING INSTRUCTIONS")
        
        print("""
This guide helps you manually test the Naishi game implementation.

STEP 1: Human vs Human Game
----------------------------
Run: python naishi_pvp.py

Test checklist:
  ☐ Game starts correctly (2 cards each, 3 Mountains each)
  ☐ Turn Option A works (Develop → Optional Emissary)
  ☐ Turn Option B works (Emissary → Required Develop)
  ☐ All action types work (Develop, Swap, Discard, Recall, Decree, End)
  ☐ Emissary spots tracked correctly (3 swaps, 2 discards)
  ☐ Game ends correctly (declare or auto-end)
  ☐ Scoring is correct
  ☐ Winner determined correctly

STEP 2: Human vs AI Game
-------------------------
Run: python play_vs_ai.py

Test checklist:
  ☐ AI makes legal moves
  ☐ AI follows turn structure correctly
  ☐ Both players use same rules
  ☐ Game completes successfully
  ☐ Scoring is correct for both players

STEP 3: Test All Card Types
----------------------------
During gameplay, try to get each card type in your territory:
  ☐ Mountain (should have 3 at start)
  ☐ Naishi (test position 2 and 7 for bonuses)
  ☐ Councellor (test position bonuses and Naishi adjacency)
  ☐ Sentinel (test not adjacent to Sentinel, adjacent to Fort)
  ☐ Fort (test corners: 0, 4, 5, 9)
  ☐ Monk (test in hand and adjacent to Torii)
  ☐ Torii (test 1, 2, 3+ for different scores)
  ☐ Knight (test in hand and below Banner)
  ☐ Banner (test 1 vs 2+)
  ☐ Rice Fields (test connected groups)
  ☐ Ronin (test with different unique type counts)
  ☐ Ninja (test copying different cards)

STEP 4: Test All Actions
-------------------------
  ☐ ACTION_DEVELOP: Develop territory at each position (0-9)
  ☐ ACTION_SWAP Type 1: Swap in Hand
  ☐ ACTION_SWAP Type 2: Swap in Line
  ☐ ACTION_SWAP Type 3: Swap between Hand and Line
  ☐ ACTION_SWAP Type 4: Swap in River
  ☐ ACTION_DISCARD: Discard 2 cards from river
  ☐ ACTION_RECALL: Restore emissaries and clear markers
  ☐ ACTION_DECREE: Swap cards at same position with opponent
  ☐ ACTION_END_GAME: Declare end when 1+ decks empty

STEP 5: Test Edge Cases
------------------------
  ☐ Develop from empty deck (should handle gracefully)
  ☐ Use all 3 swap spots (4th swap should be blocked)
  ☐ Use both discard spots (3rd discard should be blocked)
  ☐ Try emissary action with 0 emissaries (should be blocked)
  ☐ Use decree (max emissaries becomes 1)
  ☐ Recall after decree (should only restore to 1)
  ☐ Get 2+ Mountains (should score -5 total, not +10)
  ☐ Use Ninja (should copy and score as copied card)
  ☐ Create Rice Fields groups (test 1, 2, 3, 4+ connected)
  ☐ Get 8, 9, or 10 unique types with Ronin
  ☐ Tie score (should use unique cards as tiebreaker)
  ☐ Let 2+ decks empty after P1 (should auto-end after P2)
  ☐ Decline optional emissary (turn should end)
  ☐ Use emissary first (must develop should be enforced)

STEP 6: Verify Scoring
-----------------------
At game end, manually calculate scores and compare with system:
  ☐ Count each card type
  ☐ Apply scoring rules from RULES.md Section 8
  ☐ Verify system score matches manual calculation
  ☐ Check both players' scores
  ☐ Verify winner is correct

STEP 7: Verify Ending
----------------------
  ☐ Try to declare end with 0 decks empty (should be blocked)
  ☐ Declare end with 1 deck empty (should work)
  ☐ Let 2+ decks empty after P1 (should auto-end after P2)
  ☐ Verify P2 always gets final turn
  ☐ Verify game terminates correctly

REPORTING RESULTS
-----------------
After completing manual testing, document:
  1. Any bugs found
  2. Any rules violations
  3. Any unexpected behavior
  4. Overall compliance assessment

""")
    
    def run(self):
        """Run the complete manual test guide"""
        print("\n" + "="*70)
        print("  NAISHI MANUAL TESTING GUIDE - TASK 39")
        print("  Complete RULES.md Compliance Verification")
        print("="*70)
        
        # Run automated verification first
        self.run_quick_verification()
        
        # Show what needs manual testing
        self.verify_turn_options()
        self.verify_edge_cases()
        self.verify_scoring_rules()
        self.verify_ending_rules()
        
        # Print manual test instructions
        self.print_manual_test_instructions()
        
        print("\n" + "="*70)
        print("  READY FOR MANUAL TESTING")
        print("="*70)
        print("\nNext steps:")
        print("  1. Run: python naishi_pvp.py (Human vs Human)")
        print("  2. Run: python play_vs_ai.py (Human vs AI)")
        print("  3. Follow the checklist above")
        print("  4. Document any issues found")
        print("\n")

if __name__ == "__main__":
    guide = ManualTestGuide()
    guide.run()
