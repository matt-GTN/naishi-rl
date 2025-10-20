"""
Test Task 40: Verify compliance matrix updates

This test verifies that the compliance matrix has been properly updated
with validation results from all completed tasks.
"""

import pytest


def test_compliance_matrix_exists():
    """WHEN compliance matrix file exists THEN it SHALL be readable"""
    import os
    assert os.path.exists('.kiro/specs/full-compliance-audit/compliance_matrix.md')


def test_compliance_matrix_has_validation_results():
    """WHEN compliance matrix is updated THEN it SHALL contain validation results section"""
    with open('.kiro/specs/full-compliance-audit/compliance_matrix.md', 'r') as f:
        content = f.read()
    
    # Check for validation results section
    assert '## Validation Results (Phase 4)' in content
    assert 'Task 34: Unit Tests for GameState Turn Structure' in content
    assert 'Task 35: Unit Tests for All GameState Actions' in content
    assert 'Task 37: Integration Tests for NaishiEnv' in content
    assert 'Task 38: Integration Tests for UI Files' in content
    assert 'Task 39: Manual Testing' in content


def test_compliance_matrix_shows_full_compliance():
    """WHEN all issues are resolved THEN compliance matrix SHALL show 100% compliance"""
    with open('.kiro/specs/full-compliance-audit/compliance_matrix.md', 'r') as f:
        content = f.read()
    
    # Check summary statistics
    assert '**Fully Compliant:** 11 (ALL SECTIONS)' in content
    assert '**Partially Compliant:** 0' in content
    assert '**Non-Compliant:** 0' in content
    assert '**Overall Compliance:** ✅ 100% FULLY COMPLIANT' in content


def test_section_4_marked_compliant():
    """WHEN Section 4 issues are resolved THEN it SHALL be marked as fully compliant"""
    with open('.kiro/specs/full-compliance-audit/compliance_matrix.md', 'r') as f:
        content = f.read()
    
    # Find Section 4
    section_4_start = content.find('## Section 4: Turn Structure')
    section_4_end = content.find('## Section 5.1:', section_4_start)
    section_4 = content[section_4_start:section_4_end]
    
    # Check that all components are marked as compliant
    assert '| Option A: Develop → Optional Emissary | ✅ |' in section_4
    assert '| Option B: Emissary → Required Develop | ✅ |' in section_4
    assert '| Turn state tracking | ✅ |' in section_4
    assert '| optional_emissary_available flag | ✅ |' in section_4
    
    # Check that issues are marked as resolved
    assert 'CRIT-001 RESOLVED' in section_4 or 'CRIT-001, CRIT-002 RESOLVED' in section_4
    assert 'HIGH-001 RESOLVED' in section_4
    
    # Check overall status
    assert '**Overall:** FULLY COMPLIANT' in section_4


def test_section_7_marked_compliant():
    """WHEN Section 7 issues are resolved THEN it SHALL be marked as fully compliant"""
    with open('.kiro/specs/full-compliance-audit/compliance_matrix.md', 'r') as f:
        content = f.read()
    
    # Find Section 7
    section_7_start = content.find('## Section 7: Game Ending')
    section_7_end = content.find('## Section 8:', section_7_start)
    section_7 = content[section_7_start:section_7_end]
    
    # Check that all components are marked as compliant
    assert '| ending_available flag | ✅ |' in section_7
    assert '| P2 gets final turn | ✅ |' in section_7
    assert '| Auto-end when 2+ decks empty (after P1) | ✅ |' in section_7
    
    # Check that issues are marked as resolved
    assert 'CRIT-003 RESOLVED' in section_7
    assert 'CRIT-004 RESOLVED' in section_7
    
    # Check overall status
    assert '**Overall:** FULLY COMPLIANT' in section_7


def test_architecture_marked_compliant():
    """WHEN architecture issues are resolved THEN it SHALL be marked as fully compliant"""
    with open('.kiro/specs/full-compliance-audit/compliance_matrix.md', 'r') as f:
        content = f.read()
    
    # Find Architecture section
    arch_start = content.find('## Architecture: Single Source of Truth')
    arch_end = content.find('## Architecture: UI Purity', arch_start)
    arch_section = content[arch_start:arch_end]
    
    # Check that all components are marked as compliant
    assert '| naishi_pvp.py delegates to GameState | ✅ |' in arch_section
    assert '| play_vs_ai.py delegates to GameState | ✅ |' in arch_section
    assert '| No logic duplication | ✅ |' in arch_section
    
    # Check that issues are marked as resolved
    assert 'ARCH-001, ARCH-002, ARCH-003 RESOLVED' in arch_section
    assert 'ARCH-004, ARCH-005, ARCH-006 RESOLVED' in arch_section


def test_resolved_issues_summary_exists():
    """WHEN issues are resolved THEN a resolved issues summary SHALL exist"""
    with open('.kiro/specs/full-compliance-audit/compliance_matrix.md', 'r') as f:
        content = f.read()
    
    # Check for resolved issues summary
    assert '## Resolved Issues Summary' in content
    assert '### Critical Issues (All Resolved)' in content
    assert '### High Priority Issues (All Resolved)' in content
    assert '### Medium Priority Issues (All Resolved)' in content
    assert '### Architecture Issues (All Resolved)' in content


def test_all_critical_issues_documented_as_resolved():
    """WHEN critical issues are resolved THEN they SHALL be documented in summary"""
    with open('.kiro/specs/full-compliance-audit/compliance_matrix.md', 'r') as f:
        content = f.read()
    
    # Find resolved issues section
    resolved_start = content.find('## Resolved Issues Summary')
    resolved_end = content.find('## Remaining Work', resolved_start)
    resolved_section = content[resolved_start:resolved_end]
    
    # Check all critical issues are documented
    assert 'CRIT-001' in resolved_section
    assert 'CRIT-002' in resolved_section
    assert 'CRIT-003' in resolved_section
    assert 'CRIT-004' in resolved_section
    
    # Check they're marked as resolved
    assert 'Tasks 16-17' in resolved_section  # CRIT-001
    assert 'Task 17' in resolved_section  # CRIT-002
    assert 'Task 24' in resolved_section  # CRIT-003, CRIT-004


def test_validation_test_counts_documented():
    """WHEN validation is complete THEN test counts SHALL be documented"""
    with open('.kiro/specs/full-compliance-audit/compliance_matrix.md', 'r') as f:
        content = f.read()
    
    # Check test counts are documented
    assert '26 unit tests' in content  # Task 34
    assert '51 unit tests' in content  # Task 35
    assert '19 integration tests' in content  # Task 37
    assert '16 integration tests' in content  # Task 38
    assert '112 automated tests' in content or '112 tests' in content  # Total


def test_issue_tracking_updated():
    """WHEN issues are resolved THEN issue tracking SHALL be updated"""
    with open('.kiro/specs/full-compliance-audit/issue_tracking.md', 'r') as f:
        content = f.read()
    
    # Check critical issues are marked as resolved
    crit_001_start = content.find('### CRIT-001:')
    crit_001_section = content[crit_001_start:crit_001_start + 2000]
    assert '**Status:** ✅ Resolved' in crit_001_section
    assert '**Resolution Date:** October 20, 2025' in crit_001_section
    assert '**Resolved By:** Tasks 16-17' in crit_001_section
    
    crit_002_start = content.find('### CRIT-002:')
    crit_002_section = content[crit_002_start:crit_002_start + 2000]
    assert '**Status:** ✅ Resolved' in crit_002_section
    
    crit_003_start = content.find('### CRIT-003:')
    crit_003_section = content[crit_003_start:crit_003_start + 2000]
    assert '**Status:** ✅ Resolved' in crit_003_section
    
    crit_004_start = content.find('### CRIT-004:')
    crit_004_section = content[crit_004_start:crit_004_start + 2000]
    assert '**Status:** ✅ Resolved' in crit_004_section


def test_implementation_summary_created():
    """WHEN task 40 is complete THEN implementation summary SHALL exist"""
    import os
    assert os.path.exists('.kiro/specs/full-compliance-audit/task40_implementation_summary.md')
    
    with open('.kiro/specs/full-compliance-audit/task40_implementation_summary.md', 'r') as f:
        content = f.read()
    
    # Check key sections exist
    assert '# Task 40 Implementation Summary' in content
    assert '## Overview' in content
    assert '## Requirements Addressed' in content
    assert '## Implementation Approach' in content
    assert '## Compliance Verification' in content
    assert '## Conclusion' in content
    assert '## Task Status: ✅ COMPLETE' in content


def test_all_phases_documented():
    """WHEN all phases are complete THEN they SHALL be documented in matrix"""
    with open('.kiro/specs/full-compliance-audit/compliance_matrix.md', 'r') as f:
        content = f.read()
    
    # Check all phases are documented
    assert 'Phase 1: Comprehensive Audit (Tasks 1-15)' in content
    assert 'Phase 2: naishi_core Compliance Fixes (Tasks 16-25)' in content
    assert 'Phase 3: Architecture Compliance Fixes (Tasks 26-33)' in content
    assert 'Phase 4: Comprehensive Validation (Tasks 34-39)' in content


def test_remaining_work_documented():
    """WHEN task 40 is complete THEN remaining work SHALL be documented"""
    with open('.kiro/specs/full-compliance-audit/compliance_matrix.md', 'r') as f:
        content = f.read()
    
    # Check remaining work section exists
    assert '## Remaining Work' in content
    assert 'Task 40: Update compliance matrix with validation results' in content
    assert 'Phase 5: Documentation and Reporting (Tasks 41-45)' in content
    assert 'Task 41: Update code documentation' in content
    assert 'Task 42: Update README' in content
    assert 'Task 43: Generate final compliance report' in content


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
