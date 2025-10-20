#!/usr/bin/env python3
"""Test for Task 41: Update code documentation

This test verifies that:
1. RULES.md section references are added to code comments
2. Turn state fields are documented
3. Action handling logic is documented
"""

import re
from pathlib import Path


def test_rules_md_references():
    """Verify RULES.md section references are present in game_logic.py"""
    game_logic_path = Path("naishi_core/game_logic.py")
    content = game_logic_path.read_text()
    
    # Check for RULES.md references in key sections
    rules_references = [
        "RULES.md Section 2",  # Setup
        "RULES.md Section 4",  # Turn Structure
        "RULES.md Section 5",  # Actions
        "RULES.md Section 6",  # Emissary System
        "RULES.md Section 7",  # Game End
    ]
    
    for ref in rules_references:
        assert ref in content, f"Missing reference to {ref}"
        print(f"✓ Found reference to {ref}")
    
    print("\n✓ All RULES.md section references present")


def test_turn_state_documentation():
    """Verify turn state fields are documented"""
    game_logic_path = Path("naishi_core/game_logic.py")
    content = game_logic_path.read_text()
    
    # Check for turn state field documentation
    turn_state_fields = [
        "optional_emissary_available",
        "must_develop",
        "last_action_type",
    ]
    
    for field in turn_state_fields:
        # Check that field is documented with RULES.md reference
        pattern = rf"{field}.*RULES\.md"
        assert re.search(pattern, content, re.DOTALL), \
            f"Field {field} not documented with RULES.md reference"
        print(f"✓ Field '{field}' is documented")
    
    print("\n✓ All turn state fields documented")


def test_action_handling_documentation():
    """Verify action handling logic is documented"""
    game_logic_path = Path("naishi_core/game_logic.py")
    content = game_logic_path.read_text()
    
    # Check for action type documentation
    action_types = [
        "ACTION_DEVELOP",
        "ACTION_SWAP",
        "ACTION_DISCARD",
        "ACTION_RECALL",
        "ACTION_DECREE",
        "ACTION_END_GAME",
    ]
    
    for action in action_types:
        # Check that action handling has RULES.md reference
        pattern = rf"elif a_type == {action}:.*?RULES\.md"
        assert re.search(pattern, content, re.DOTALL), \
            f"Action {action} handling not documented with RULES.md reference"
        print(f"✓ Action '{action}' handling is documented")
    
    print("\n✓ All action handling logic documented")


def test_class_documentation():
    """Verify GameState class has comprehensive documentation"""
    game_logic_path = Path("naishi_core/game_logic.py")
    content = game_logic_path.read_text()
    
    # Check for class-level documentation
    class_doc_patterns = [
        r"class GameState:.*?Turn State Fields.*?RULES\.md Section 4",
        r"class GameState:.*?Emissary State Fields.*?RULES\.md Section 6",
        r"class GameState:.*?Game End Fields.*?RULES\.md Section 7",
    ]
    
    for pattern in class_doc_patterns:
        assert re.search(pattern, content, re.DOTALL), \
            f"Missing class documentation pattern: {pattern}"
    
    print("✓ GameState class has comprehensive documentation")


def test_method_documentation():
    """Verify key methods have RULES.md references"""
    game_logic_path = Path("naishi_core/game_logic.py")
    content = game_logic_path.read_text()
    
    # Check for method documentation
    methods_to_check = [
        ("_setup_draft", "RULES.md Section 2"),
        ("_complete_draft", "RULES.md Section 2"),
        ("clear_turn_state", "RULES.md Section 4"),
        ("_can_use_optional_emissary", "RULES.md Section 4"),
        ("skip_optional_emissary", "RULES.md Section 4"),
        ("get_legal_action_types", "RULES.md Section 4"),
        ("apply_action", "RULES.md Section 4"),
    ]
    
    for method_name, expected_ref in methods_to_check:
        # Find method definition and check for RULES.md reference in docstring
        pattern = rf"def {method_name}\(.*?\):.*?{re.escape(expected_ref)}"
        assert re.search(pattern, content, re.DOTALL), \
            f"Method {method_name} missing reference to {expected_ref}"
        print(f"✓ Method '{method_name}' documented with {expected_ref}")
    
    print("\n✓ All key methods documented with RULES.md references")


def test_module_documentation():
    """Verify module-level documentation includes RULES.md compliance"""
    game_logic_path = Path("naishi_core/game_logic.py")
    content = game_logic_path.read_text()
    
    # Check module docstring has RULES.md compliance section
    assert "RULES.md Compliance:" in content, \
        "Module docstring missing RULES.md Compliance section"
    
    # Check for key sections mentioned
    compliance_sections = [
        "Section 2: Setup",
        "Section 4: Turn Structure",
        "Section 5: Actions",
        "Section 6: Emissary System",
        "Section 7: Game End",
    ]
    
    for section in compliance_sections:
        assert section in content[:2000], \
            f"Module docstring missing {section}"
        print(f"✓ Module docstring includes {section}")
    
    print("\n✓ Module documentation includes RULES.md compliance")


def test_inline_comments():
    """Verify inline comments reference RULES.md sections"""
    game_logic_path = Path("naishi_core/game_logic.py")
    content = game_logic_path.read_text()
    
    # Check for inline comments in action handling
    inline_comment_patterns = [
        r"# RULES\.md Section 5\.1: Develop Territory",
        r"# RULES\.md Section 5\.2: Emissary Actions - Swap Cards",
        r"# RULES\.md Section 5\.2: Emissary Actions - Discard River Cards",
        r"# RULES\.md Section 5\.3: Recall Emissaries",
        r"# RULES\.md Section 5\.4: Decree",
        r"# RULES\.md Section 7: Declare End of Game",
    ]
    
    for pattern in inline_comment_patterns:
        assert re.search(pattern, content), \
            f"Missing inline comment: {pattern}"
        print(f"✓ Found inline comment matching: {pattern}")
    
    print("\n✓ All inline comments with RULES.md references present")


def main():
    """Run all documentation tests"""
    print("=" * 60)
    print("Task 41: Code Documentation Verification")
    print("=" * 60)
    print()
    
    tests = [
        ("RULES.md References", test_rules_md_references),
        ("Turn State Documentation", test_turn_state_documentation),
        ("Action Handling Documentation", test_action_handling_documentation),
        ("Class Documentation", test_class_documentation),
        ("Method Documentation", test_method_documentation),
        ("Module Documentation", test_module_documentation),
        ("Inline Comments", test_inline_comments),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n{'=' * 60}")
        print(f"Testing: {test_name}")
        print(f"{'=' * 60}")
        try:
            test_func()
            passed += 1
            print(f"\n✅ {test_name} - PASSED")
        except AssertionError as e:
            failed += 1
            print(f"\n❌ {test_name} - FAILED")
            print(f"   Error: {e}")
        except Exception as e:
            failed += 1
            print(f"\n❌ {test_name} - ERROR")
            print(f"   Error: {e}")
    
    print(f"\n{'=' * 60}")
    print(f"Test Summary")
    print(f"{'=' * 60}")
    print(f"Passed: {passed}/{len(tests)}")
    print(f"Failed: {failed}/{len(tests)}")
    
    if failed == 0:
        print("\n✅ All documentation tests passed!")
        return 0
    else:
        print(f"\n❌ {failed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit(main())
