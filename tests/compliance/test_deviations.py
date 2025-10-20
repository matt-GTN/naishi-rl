#!/usr/bin/env python3
"""
Test Task 45: Document any deviations from RULES.md

This test verifies that the RULES_DEVIATIONS.md document:
1. Exists and is properly formatted
2. Lists all known deviations
3. Provides rationale for each deviation
4. Documents workarounds
5. References RULES.md sections correctly

Requirements: 9.4
"""

import os
import re


def test_deviations_document_exists():
    """Test that RULES_DEVIATIONS.md exists."""
    assert os.path.exists("RULES_DEVIATIONS.md"), "RULES_DEVIATIONS.md not found"
    print("✅ RULES_DEVIATIONS.md exists")


def test_deviations_document_structure():
    """Test that the document has proper structure."""
    with open("RULES_DEVIATIONS.md", "r") as f:
        content = f.read()
    
    # Check for required sections
    required_sections = [
        "# RULES.md Deviations Documentation",
        "## Executive Summary",
        "## Deviations List",
        "## Historical Deviations (Resolved)",
        "## Compliance Verification",
        "## Recommendations",
        "## References",
        "## Certification"
    ]
    
    for section in required_sections:
        assert section in content, f"Missing section: {section}"
    
    print("✅ Document has all required sections")


def test_deviations_list_format():
    """Test that deviations are properly formatted."""
    with open("RULES_DEVIATIONS.md", "r") as f:
        content = f.read()
    
    # Check for DEV-001 (the only current deviation)
    assert "DEV-001" in content, "DEV-001 deviation not documented"
    assert "is_legal_action()" in content, "DEV-001 description missing"
    assert "DEFERRED" in content, "DEV-001 status not marked as deferred"
    
    # Check for required fields in deviation
    dev_001_section = content[content.find("### DEV-001"):content.find("### CRIT-001")]
    
    required_fields = [
        "**Status:**",
        "**Priority:**",
        "**Component:**",
        "**RULES.md Section:**",
        "**Requirements:**",
        "#### Description",
        "#### Rationale for Deferral",
        "#### Impact Assessment",
        "#### Workaround",
        "#### Future Resolution"
    ]
    
    for field in required_fields:
        assert field in dev_001_section, f"Missing field in DEV-001: {field}"
    
    print("✅ DEV-001 deviation properly formatted with all required fields")


def test_rationale_provided():
    """Test that rationale is provided for the deviation."""
    with open("RULES_DEVIATIONS.md", "r") as f:
        content = f.read()
    
    # Extract DEV-001 section
    dev_001_section = content[content.find("### DEV-001"):content.find("### CRIT-001")]
    
    # Check for rationale points
    rationale_points = [
        "No Functional Impact",
        "Protected by Action Masks",
        "Graceful Degradation",
        "Low Priority"
    ]
    
    for point in rationale_points:
        assert point in dev_001_section, f"Missing rationale point: {point}"
    
    print("✅ Comprehensive rationale provided for deviation")


def test_workaround_documented():
    """Test that workarounds are documented."""
    with open("RULES_DEVIATIONS.md", "r") as f:
        content = f.read()
    
    # Extract DEV-001 section
    dev_001_section = content[content.find("### DEV-001"):content.find("### CRIT-001")]
    
    # Check for workaround sections
    assert "**For Developers:**" in dev_001_section, "Developer workaround missing"
    assert "**For Users:**" in dev_001_section, "User workaround missing"
    assert "get_legal_action_types()" in dev_001_section, "Workaround details missing"
    
    print("✅ Workarounds documented for developers and users")


def test_historical_deviations_documented():
    """Test that resolved deviations are documented."""
    with open("RULES_DEVIATIONS.md", "r") as f:
        content = f.read()
    
    # Check for resolved critical issues
    resolved_issues = [
        "CRIT-001",
        "CRIT-002",
        "CRIT-003",
        "CRIT-004",
        "HIGH-001",
        "MED-001",
        "MED-002",
        "ARCH-001 to ARCH-007",
        "UI-001"
    ]
    
    for issue in resolved_issues:
        assert issue in content, f"Resolved issue not documented: {issue}"
        # Verify it's marked as resolved
        issue_section = content[content.find(issue):content.find(issue) + 500]
        assert "✅ RESOLVED" in issue_section, f"{issue} not marked as resolved"
    
    print("✅ All historical deviations documented with resolution status")


def test_rules_md_references():
    """Test that RULES.md sections are referenced."""
    with open("RULES_DEVIATIONS.md", "r") as f:
        content = f.read()
    
    # Check for RULES.md section references
    assert "Section 5.1" in content, "RULES.md section reference missing"
    assert "Section 4" in content, "RULES.md section reference missing"
    assert "Section 7" in content, "RULES.md section reference missing"
    
    print("✅ RULES.md sections properly referenced")


def test_compliance_status():
    """Test that compliance status is documented."""
    with open("RULES_DEVIATIONS.md", "r") as f:
        content = f.read()
    
    # Check for compliance metrics
    assert "99.9% Compliant" in content, "Compliance percentage missing"
    assert "Total Deviations:** 1" in content, "Total deviations count missing"
    assert "Critical Deviations:** 0" in content, "Critical deviations count missing"
    assert "Non-Critical Deviations:** 1" in content, "Non-critical deviations count missing"
    
    print("✅ Compliance status clearly documented")


def test_validation_references():
    """Test that validation tools are referenced."""
    with open("RULES_DEVIATIONS.md", "r") as f:
        content = f.read()
    
    # Check for validation tool references
    validation_tools = [
        "test_task34.py",
        "test_task35.py",
        "test_task37.py",
        "test_task38.py",
        "test_task39.py",
        "verify_task39.py"
    ]
    
    for tool in validation_tools:
        assert tool in content, f"Validation tool not referenced: {tool}"
    
    print("✅ Validation tools properly referenced")


def test_recommendations_provided():
    """Test that recommendations are provided."""
    with open("RULES_DEVIATIONS.md", "r") as f:
        content = f.read()
    
    # Check for recommendation sections
    assert "### Immediate Actions" in content, "Immediate actions missing"
    assert "### Short-Term Actions" in content, "Short-term actions missing"
    assert "### Long-Term Actions" in content, "Long-term actions missing"
    
    # Check for specific recommendations
    assert "Monitor DEV-001" in content, "DEV-001 monitoring recommendation missing"
    assert "Retrain AI Models" in content, "Retraining recommendation missing"
    assert "Regular Audits" in content, "Regular audit recommendation missing"
    
    print("✅ Comprehensive recommendations provided")


def test_certification_section():
    """Test that certification section is complete."""
    with open("RULES_DEVIATIONS.md", "r") as f:
        content = f.read()
    
    # Check for certification details
    assert "Certification Date:" in content, "Certification date missing"
    assert "October 20, 2025" in content, "Certification date incorrect"
    assert "Audit Phase:** Complete" in content, "Audit phase status missing"
    
    print("✅ Certification section complete")


def test_document_completeness():
    """Test overall document completeness."""
    with open("RULES_DEVIATIONS.md", "r") as f:
        content = f.read()
    
    # Check document length (should be comprehensive)
    lines = content.split("\n")
    assert len(lines) > 200, f"Document too short ({len(lines)} lines), may be incomplete"
    
    # Check for code examples
    assert "```python" in content, "Code examples missing"
    
    # Check for impact assessment
    assert "Impact Assessment" in content, "Impact assessment missing"
    assert "Severity:" in content, "Severity rating missing"
    
    print(f"✅ Document is comprehensive ({len(lines)} lines)")


def run_all_tests():
    """Run all tests for Task 45."""
    print("\n" + "="*70)
    print("Task 45: Document any deviations from RULES.md")
    print("="*70 + "\n")
    
    tests = [
        ("Document Exists", test_deviations_document_exists),
        ("Document Structure", test_deviations_document_structure),
        ("Deviations List Format", test_deviations_list_format),
        ("Rationale Provided", test_rationale_provided),
        ("Workaround Documented", test_workaround_documented),
        ("Historical Deviations", test_historical_deviations_documented),
        ("RULES.md References", test_rules_md_references),
        ("Compliance Status", test_compliance_status),
        ("Validation References", test_validation_references),
        ("Recommendations", test_recommendations_provided),
        ("Certification Section", test_certification_section),
        ("Document Completeness", test_document_completeness)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            print(f"\nTest: {test_name}")
            print("-" * 70)
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"❌ FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"❌ ERROR: {e}")
            failed += 1
    
    print("\n" + "="*70)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("="*70 + "\n")
    
    if failed == 0:
        print("✅ All tests passed! Task 45 complete.")
        print("\nDeviations Summary:")
        print("- Total Deviations: 1 (DEV-001)")
        print("- Critical Deviations: 0")
        print("- Non-Critical Deviations: 1 (deferred)")
        print("- Compliance Status: 99.9%")
        print("\nThe RULES_DEVIATIONS.md document is complete and comprehensive.")
    else:
        print(f"❌ {failed} test(s) failed. Please review the document.")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
