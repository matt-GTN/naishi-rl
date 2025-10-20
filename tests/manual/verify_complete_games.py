#!/usr/bin/env python3
"""
Verification script for Task 39: Manual Testing

This script verifies that all manual testing tools are in place
and demonstrates that the games can be launched.
"""

import os
import sys

def verify_files_exist():
    """Verify all required files exist"""
    required_files = [
        "manual_test_guide.py",
        "manual_test_output.txt",
        "test_task39.py",
        ".kiro/specs/full-compliance-audit/task39_implementation_summary.md",
        "naishi_pvp.py",
        "play_vs_ai.py",
        "naishi_ui.py",
        "naishi_env.py",
        "naishi_core/game_logic.py",
        "naishi_core/scorer.py",
        "RULES.md"
    ]
    
    print("="*70)
    print("  TASK 39 VERIFICATION: Manual Testing Tools")
    print("="*70)
    print()
    
    all_exist = True
    for file_path in required_files:
        exists = os.path.exists(file_path)
        status = "✅" if exists else "❌"
        print(f"{status} {file_path}")
        if not exists:
            all_exist = False
    
    print()
    return all_exist

def verify_manual_test_guide():
    """Verify manual test guide can be imported and run"""
    print("="*70)
    print("  Verifying Manual Test Guide")
    print("="*70)
    print()
    
    try:
        # Try to import the manual test guide
        import manual_test_guide
        print("✅ Manual test guide can be imported")
        
        # Check that it has the required class
        assert hasattr(manual_test_guide, 'ManualTestGuide')
        print("✅ ManualTestGuide class exists")
        
        # Create an instance
        guide = manual_test_guide.ManualTestGuide()
        print("✅ ManualTestGuide can be instantiated")
        
        return True
    except Exception as e:
        print(f"❌ Error with manual test guide: {e}")
        return False

def verify_game_files():
    """Verify game files can be imported"""
    print()
    print("="*70)
    print("  Verifying Game Files")
    print("="*70)
    print()
    
    try:
        # Try to import game modules
        from naishi_core.game_logic import GameState
        print("✅ GameState can be imported")
        
        from naishi_core.scorer import Scorer
        print("✅ Scorer can be imported")
        
        from naishi_ui import NaishiUI
        print("✅ NaishiUI can be imported")
        
        from naishi_env import NaishiEnv
        print("✅ NaishiEnv can be imported")
        
        # Test creating a game state
        gs = GameState.create_initial_state()
        print("✅ GameState can be created")
        
        # Test creating an environment
        env = NaishiEnv()
        print("✅ NaishiEnv can be created")
        
        return True
    except Exception as e:
        print(f"❌ Error with game files: {e}")
        return False

def verify_test_documentation():
    """Verify test documentation is complete"""
    print()
    print("="*70)
    print("  Verifying Test Documentation")
    print("="*70)
    print()
    
    try:
        with open("manual_test_output.txt", "r") as f:
            content = f.read()
        
        required_sections = [
            "SETUP VERIFICATION",
            "CARD TYPES VERIFICATION",
            "ACTION TYPES VERIFICATION",
            "TURN STRUCTURE VERIFICATION",
            "EDGE CASES TO TEST",
            "SCORING VERIFICATION",
            "GAME ENDING VERIFICATION",
            "MANUAL TESTING INSTRUCTIONS",
            "Human vs Human Game",
            "Human vs AI Game",
            "Test All Card Types",
            "Test All Actions",
            "Test Edge Cases",
            "Verify Scoring",
            "Verify Ending"
        ]
        
        all_present = True
        for section in required_sections:
            if section in content:
                print(f"✅ Section present: {section}")
            else:
                print(f"❌ Section missing: {section}")
                all_present = False
        
        return all_present
    except Exception as e:
        print(f"❌ Error reading documentation: {e}")
        return False

def print_summary():
    """Print summary and instructions"""
    print()
    print("="*70)
    print("  TASK 39 VERIFICATION SUMMARY")
    print("="*70)
    print()
    print("All manual testing tools are in place and verified!")
    print()
    print("To perform manual testing:")
    print()
    print("1. Review the automated verification:")
    print("   $ python manual_test_guide.py")
    print()
    print("2. Play Human vs Human:")
    print("   $ python naishi_pvp.py")
    print()
    print("3. Play Human vs AI:")
    print("   $ python play_vs_ai.py")
    print()
    print("4. Follow the checklists in manual_test_output.txt")
    print()
    print("5. Document any issues found")
    print()
    print("="*70)
    print()

def main():
    """Run all verifications"""
    results = []
    
    results.append(("Files Exist", verify_files_exist()))
    results.append(("Manual Test Guide", verify_manual_test_guide()))
    results.append(("Game Files", verify_game_files()))
    results.append(("Test Documentation", verify_test_documentation()))
    
    print()
    print("="*70)
    print("  VERIFICATION RESULTS")
    print("="*70)
    print()
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
        if not passed:
            all_passed = False
    
    print()
    
    if all_passed:
        print_summary()
        return 0
    else:
        print("❌ Some verifications failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
