#!/usr/bin/env python3
"""
Test for Task 42: Update README with compliance information

Validates that README.md contains all required compliance documentation:
- RULES.md compliance section
- Architecture (single source of truth) documentation
- UI purity documentation
- Complete RULES.md implementation details
"""

def test_readme_compliance_section():
    """Test that README contains RULES.md compliance section"""
    with open('README.md', 'r') as f:
        content = f.read()
    
    # Check for main compliance section
    assert '## RULES.md Compliance' in content, "Missing RULES.md Compliance section"
    
    # Check for architecture documentation
    assert '### Architecture: Single Source of Truth' in content, "Missing Architecture section"
    assert 'naishi_core/game_logic.py' in content, "Missing reference to game_logic.py"
    assert 'GameState' in content, "Missing reference to GameState"
    
    # Check for delegation documentation
    assert 'naishi_env.py' in content, "Missing naishi_env.py reference"
    assert 'naishi_pvp.py' in content, "Missing naishi_pvp.py reference"
    assert 'play_vs_ai.py' in content, "Missing play_vs_ai.py reference"
    assert 'delegates to GameState' in content or 'delegate to GameState' in content, \
        "Missing delegation documentation"
    
    # Check for UI purity documentation
    assert '### UI Layer Purity' in content, "Missing UI Layer Purity section"
    assert 'naishi_ui.py' in content, "Missing naishi_ui.py reference"
    assert 'zero game logic' in content, "Missing 'zero game logic' statement"
    
    # Check for RULES.md implementation documentation
    assert '### Complete RULES.md Implementation' in content, "Missing Complete RULES.md Implementation section"
    
    # Check for specific RULES.md sections
    rules_sections = [
        'Section 2 (Setup)',
        'Section 4 (Turn Structure)',
        'Section 5.1 (Develop)',
        'Section 5.2 (Emissary)',
        'Section 5.3 (Recall)',
        'Section 5.4 (Decree)',
        'Section 7 (Game End)',
        'Section 8 (Scoring)'
    ]
    
    for section in rules_sections:
        assert section in content, f"Missing documentation for {section}"
    
    # Check for validation documentation
    assert '### Validation' in content, "Missing Validation section"
    assert 'Unit tests' in content, "Missing unit tests reference"
    assert 'Integration tests' in content, "Missing integration tests reference"
    
    # Check for compliance audit reference
    assert '.kiro/specs/full-compliance-audit' in content, \
        "Missing reference to compliance audit documentation"
    
    print("✅ All compliance documentation checks passed!")


def test_readme_project_structure():
    """Test that project structure includes naishi_core details"""
    with open('README.md', 'r') as f:
        content = f.read()
    
    # Check for naishi_core directory documentation
    assert 'naishi_core/' in content, "Missing naishi_core directory in project structure"
    assert 'game_logic.py' in content, "Missing game_logic.py in project structure"
    assert 'Single source of truth' in content, "Missing 'Single source of truth' description"
    
    # Check for delegation comments in structure
    assert 'delegates to naishi_core' in content or 'delegates to GameState' in content, \
        "Missing delegation documentation in project structure"
    
    print("✅ Project structure documentation checks passed!")


def test_readme_architecture_benefits():
    """Test that README documents benefits of the architecture"""
    with open('README.md', 'r') as f:
        content = f.read()
    
    # Check for architecture benefits
    benefits = [
        'Consistent rule enforcement',
        'Single point of maintenance',
        'compliance with RULES.md'
    ]
    
    for benefit in benefits:
        assert benefit.lower() in content.lower(), f"Missing benefit: {benefit}"
    
    print("✅ Architecture benefits documentation checks passed!")


def test_readme_ui_purity_benefits():
    """Test that README documents benefits of UI purity"""
    with open('README.md', 'r') as f:
        content = f.read()
    
    # Check for UI purity benefits
    ui_benefits = [
        'UI changes never affect game rules',
        'separation of concerns'
    ]
    
    for benefit in ui_benefits:
        assert benefit.lower() in content.lower(), f"Missing UI benefit: {benefit}"
    
    print("✅ UI purity benefits documentation checks passed!")


def test_readme_completeness():
    """Test that README is comprehensive and well-structured"""
    with open('README.md', 'r') as f:
        content = f.read()
    
    # Check that compliance section comes before or after project structure
    compliance_pos = content.find('## RULES.md Compliance')
    structure_pos = content.find('## Project Structure')
    
    assert compliance_pos > 0, "RULES.md Compliance section not found"
    assert structure_pos > 0, "Project Structure section not found"
    
    # Check that all subsections exist
    subsections = [
        '### Architecture: Single Source of Truth',
        '### UI Layer Purity',
        '### Complete RULES.md Implementation',
        '### Validation'
    ]
    
    for subsection in subsections:
        assert subsection in content, f"Missing subsection: {subsection}"
    
    print("✅ README completeness checks passed!")


if __name__ == '__main__':
    print("Testing Task 42: README compliance documentation\n")
    
    try:
        test_readme_compliance_section()
        test_readme_project_structure()
        test_readme_architecture_benefits()
        test_readme_ui_purity_benefits()
        test_readme_completeness()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED - Task 42 Complete!")
        print("="*60)
        print("\nREADME.md has been successfully updated with:")
        print("  ✓ RULES.md compliance documentation")
        print("  ✓ Architecture (single source of truth) details")
        print("  ✓ UI purity documentation")
        print("  ✓ Complete RULES.md implementation mapping")
        print("  ✓ Validation strategy")
        print("  ✓ Reference to compliance audit documentation")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        exit(1)
