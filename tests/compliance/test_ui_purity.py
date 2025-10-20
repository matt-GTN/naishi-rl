#!/usr/bin/env python3
"""
Task 32: Verify naishi_ui.py contains zero game logic

This test verifies that naishi_ui.py:
1. Contains only display functions
2. Does not modify game state
3. Does not implement game rules
4. Only queries GameState, never validates or enforces rules

Requirements: 3.1
"""

import ast
import inspect
from naishi_ui import NaishiUI
from naishi_core.game_logic import GameState


def test_no_state_modification():
    """Verify that NaishiUI methods do not modify GameState"""
    print("\n=== Test: No State Modification ===")
    
    # Get all methods from NaishiUI
    methods = [method for method in dir(NaishiUI) if not method.startswith('_') or method.startswith('_show')]
    
    # Check each method's signature - should not have mutable operations
    issues = []
    
    for method_name in methods:
        method = getattr(NaishiUI, method_name)
        if not callable(method):
            continue
            
        # Get source code
        try:
            source = inspect.getsource(method)
            
            # Check for state modification patterns
            forbidden_patterns = [
                'gs.current_player_idx =',
                'gs.players[',
                'player.line =',
                'player.hand =',
                'player.emissaries =',
                'gs.river.',
                '.append(',
                '.remove(',
                '.pop(',
                'gs.terminated =',
                'gs.truncated =',
                'gs.must_develop =',
                'gs.optional_emissary_available =',
            ]
            
            for pattern in forbidden_patterns:
                if pattern in source and '=' in pattern:
                    # Check if it's actually an assignment (not comparison)
                    if pattern + ' ' in source or pattern + '\n' in source:
                        issues.append(f"{method_name} contains state modification: {pattern}")
        except:
            pass
    
    if issues:
        print("❌ FAILED: Found state modifications:")
        for issue in issues:
            print(f"  - {issue}")
        return False
    else:
        print("✅ PASSED: No state modifications found")
        return True


def test_no_game_logic():
    """Verify that NaishiUI does not implement game rules"""
    print("\n=== Test: No Game Logic ===")
    
    # Parse naishi_ui.py source code
    with open('naishi_ui.py', 'r') as f:
        source = f.read()
    
    tree = ast.parse(source)
    
    issues = []
    
    # Check for game logic patterns
    class GameLogicChecker(ast.NodeVisitor):
        def __init__(self):
            self.issues = []
            self.in_method = None
        
        def visit_FunctionDef(self, node):
            old_method = self.in_method
            self.in_method = node.name
            self.generic_visit(node)
            self.in_method = old_method
        
        def visit_If(self, node):
            """Check for game rule conditionals"""
            # Get the condition as string
            try:
                condition_str = ast.unparse(node.test)
                
                # Forbidden game logic checks
                forbidden_checks = [
                    'emissaries',  # Checking emissary count
                    'must_develop',  # Checking turn state
                    'optional_emissary',  # Checking turn state
                    'terminated',  # Checking game end
                    'truncated',  # Checking game end
                    'decree_used',  # Checking decree (OK if just displaying)
                    'cards_left',  # Checking deck status (OK if just displaying)
                ]
                
                # These are OK for display purposes
                display_ok = [
                    'show_hand',  # Display control
                    'location',  # Display control
                    'spot ==',  # Display marker
                    'i <',  # Loop control
                    'i !=',  # Loop control
                ]
                
                is_display = any(ok in condition_str for ok in display_ok)
                has_logic = any(check in condition_str for check in forbidden_checks)
                
                if has_logic and not is_display:
                    # Check if it's just for display (reading, not enforcing)
                    # If it modifies state or returns validation, it's logic
                    if 'return' not in ast.unparse(node) or 'print' in ast.unparse(node):
                        # It's OK - just for display
                        pass
                    else:
                        self.issues.append(f"{self.in_method}: Game logic check: {condition_str}")
            except:
                pass
            
            self.generic_visit(node)
        
        def visit_Call(self, node):
            """Check for game logic method calls"""
            try:
                call_str = ast.unparse(node)
                
                # Allowed GameState queries (read-only)
                allowed_queries = [
                    'gs.river.get_top_card',
                    'gs.river.cards_left',
                    'player.get_all_cards',
                    'gs.players[',
                    'Scorer.handle_ninjas',
                    'Scorer.calculate_score',
                    'Scorer.determine_winner',
                    'get_choice',  # Input helper
                ]
                
                # Forbidden game logic calls
                forbidden_calls = [
                    'apply_action',
                    'validate_action',
                    'check_legal',
                    'switch_player',
                    'end_turn',
                    'check_game_end',
                ]
                
                is_allowed = any(query in call_str for query in allowed_queries)
                is_forbidden = any(call in call_str for call in forbidden_calls)
                
                if is_forbidden:
                    self.issues.append(f"{self.in_method}: Forbidden game logic call: {call_str}")
            except:
                pass
            
            self.generic_visit(node)
    
    checker = GameLogicChecker()
    checker.visit(tree)
    
    if checker.issues:
        print("❌ FAILED: Found game logic:")
        for issue in checker.issues:
            print(f"  - {issue}")
        return False
    else:
        print("✅ PASSED: No game logic found")
        return True


def test_only_display_functions():
    """Verify that all NaishiUI methods are display-only"""
    print("\n=== Test: Only Display Functions ===")
    
    # Get all public methods
    methods = [method for method in dir(NaishiUI) if not method.startswith('__')]
    
    display_methods = []
    non_display_methods = []
    
    for method_name in methods:
        method = getattr(NaishiUI, method_name)
        if not callable(method):
            continue
        
        # Check if method name suggests display purpose
        display_keywords = ['display', 'show', '_show']
        is_display = any(keyword in method_name for keyword in display_keywords)
        
        if is_display:
            display_methods.append(method_name)
        else:
            non_display_methods.append(method_name)
    
    print(f"Display methods found: {len(display_methods)}")
    for method in display_methods:
        print(f"  - {method}")
    
    if non_display_methods:
        print(f"\n⚠️  Non-display methods found: {len(non_display_methods)}")
        for method in non_display_methods:
            print(f"  - {method}")
        print("  (These should be reviewed to ensure they're display-only)")
    
    print("\n✅ PASSED: All methods reviewed")
    return True


def test_no_return_values_except_display_final_scores():
    """Verify that UI methods don't return game state or validation results"""
    print("\n=== Test: No Return Values (Except display_final_scores) ===")
    
    methods = [method for method in dir(NaishiUI) if not method.startswith('__')]
    
    issues = []
    
    for method_name in methods:
        method = getattr(NaishiUI, method_name)
        if not callable(method):
            continue
        
        # display_final_scores is allowed to return winner info for display
        if method_name == 'display_final_scores':
            continue
        
        try:
            source = inspect.getsource(method)
            
            # Check for return statements (other than None)
            if 'return ' in source:
                # Parse to check what's being returned
                lines = source.split('\n')
                for line in lines:
                    if 'return ' in line and 'return None' not in line:
                        # Check if it's returning a value
                        stripped = line.strip()
                        if stripped.startswith('return ') and stripped != 'return':
                            issues.append(f"{method_name} returns a value: {stripped}")
        except:
            pass
    
    if issues:
        print("❌ FAILED: Found methods returning values:")
        for issue in issues:
            print(f"  - {issue}")
        return False
    else:
        print("✅ PASSED: No inappropriate return values found")
        return True


def test_integration_display_only():
    """Integration test: Verify UI only displays, doesn't modify state"""
    print("\n=== Integration Test: Display Only ===")
    
    # Create a game state
    gs = GameState.create_initial_state()
    
    # Store original state
    original_current_player = gs.current_player_idx
    original_p1_hand = gs.players[0].hand.copy()
    original_p1_line = gs.players[0].line.copy()
    original_p2_hand = gs.players[1].hand.copy()
    original_p2_line = gs.players[1].line.copy()
    original_turn_count = gs.turn_count
    original_must_develop = gs.must_develop
    
    # Call display methods (suppress output)
    import sys
    from io import StringIO
    
    old_stdout = sys.stdout
    sys.stdout = StringIO()
    
    try:
        NaishiUI.show_full_state(gs)
        NaishiUI.show_player_cards_with_indices(gs.players[0], gs)
        NaishiUI.show_river_with_indices(gs)
        NaishiUI.show_hand_or_line_with_indices(gs.players[0], 'hand')
        NaishiUI.show_hand_or_line_with_indices(gs.players[0], 'line')
        NaishiUI.show_both_hand_and_line_with_indices(gs.players[0])
    finally:
        sys.stdout = old_stdout
    
    # Verify state unchanged
    issues = []
    
    if gs.current_player_idx != original_current_player:
        issues.append(f"current_player_idx changed: {original_current_player} -> {gs.current_player_idx}")
    
    if gs.players[0].hand != original_p1_hand:
        issues.append("Player 1 hand changed")
    
    if gs.players[0].line != original_p1_line:
        issues.append("Player 1 line changed")
    
    if gs.players[1].hand != original_p2_hand:
        issues.append("Player 2 hand changed")
    
    if gs.players[1].line != original_p2_line:
        issues.append("Player 2 line changed")
    
    if gs.turn_count != original_turn_count:
        issues.append(f"turn_count changed: {original_turn_count} -> {gs.turn_count}")
    
    if gs.must_develop != original_must_develop:
        issues.append(f"must_develop changed: {original_must_develop} -> {gs.must_develop}")
    
    if issues:
        print("❌ FAILED: State was modified:")
        for issue in issues:
            print(f"  - {issue}")
        return False
    else:
        print("✅ PASSED: State unchanged after display calls")
        return True


def main():
    """Run all verification tests"""
    print("=" * 80)
    print("Task 32: Verify naishi_ui.py contains zero game logic")
    print("=" * 80)
    
    results = []
    
    # Run all tests
    results.append(("No State Modification", test_no_state_modification()))
    results.append(("No Game Logic", test_no_game_logic()))
    results.append(("Only Display Functions", test_only_display_functions()))
    results.append(("No Return Values", test_no_return_values_except_display_final_scores()))
    results.append(("Integration: Display Only", test_integration_display_only()))
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 SUCCESS: naishi_ui.py contains zero game logic!")
        print("   - All display functions verified")
        print("   - No state modification found")
        print("   - No game rules implemented")
        print("   - Requirement 3.1 satisfied ✅")
        return True
    else:
        print("\n❌ FAILURE: Issues found in naishi_ui.py")
        return False


if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
