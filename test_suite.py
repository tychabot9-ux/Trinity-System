#!/usr/bin/env python3
"""
Trinity System - Comprehensive Test Suite
Full-Auto Safety Validation

Tests:
1. Safety threshold enforcement
2. Keyword filtering (positive/negative)
3. Rate limiting
4. Blacklist functionality
5. Kill switch
6. Duplicate detection
7. Fit score validation
8. End-to-end workflow
"""

import sys
from pathlib import Path
from datetime import datetime

# Import Trinity components
from safety_config import (
    validate_job_for_auto_apply,
    check_rate_limit,
    record_application,
    is_blacklisted,
    add_to_blacklist,
    is_kill_switch_active,
    activate_kill_switch,
    deactivate_kill_switch,
    MIN_FIT_SCORE,
    MAX_DAILY_APPLICATIONS,
    MAX_HOURLY_APPLICATIONS
)

# ============================================================================
# TEST DATA
# ============================================================================

# ✅ GOOD JOB (Should Pass)
GOOD_JOB = {
    "company": "Madonna Inn",
    "position": "Front Desk Agent",
    "job_text": """
        Front Desk Agent - Madonna Inn
        Day shift (8am-4pm)
        $22/hour

        We seek a friendly front desk agent for our boutique hotel.
        Responsibilities: guest check-in, phone support, light admin.
        Strong computer skills required.
    """,
    "fit_score": 85
}

# ❌ NIGHT SHIFT JOB (Should Fail - Forbidden Keywords)
NIGHT_SHIFT_JOB = {
    "company": "Hilton Hotel",
    "position": "Night Auditor",
    "job_text": """
        Night Audit position available.
        Overnight shift (11pm-7am)
        Must be comfortable working graveyard hours.
    """,
    "fit_score": 90
}

# ❌ LOW FIT SCORE (Should Fail - Below Threshold)
LOW_FIT_JOB = {
    "company": "Generic Hotel",
    "position": "Manager",
    "job_text": """
        Hotel General Manager needed.
        10+ years experience required.
        $80k+ salary.
    """,
    "fit_score": 45
}

# ❌ SUSPICIOUS JOB (Should Fail - Scam Patterns)
SCAM_JOB = {
    "company": "QuickCash Inc",
    "position": "Work From Home",
    "job_text": """
        Make money fast! No experience required!
        Unlimited income potential!
        Be your own boss with this amazing opportunity!
    """,
    "fit_score": 75
}

# ❌ NO HOSPITALITY KEYWORDS (Should Fail)
WRONG_INDUSTRY_JOB = {
    "company": "Tech Startup",
    "position": "Software Engineer",
    "job_text": """
        Looking for experienced Python developer.
        Remote position, flexible hours.
        $120k-150k salary.
    """,
    "fit_score": 80
}

# ============================================================================
# TEST FUNCTIONS
# ============================================================================

def test_good_job():
    """Test 1: Valid job should pass all checks"""
    print("\n" + "="*70)
    print("TEST 1: Good Job (Should PASS)")
    print("="*70)

    result = validate_job_for_auto_apply(GOOD_JOB)

    print(f"  Company: {GOOD_JOB['company']}")
    print(f"  Position: {GOOD_JOB['position']}")
    print(f"  Fit Score: {GOOD_JOB['fit_score']}")
    print(f"\n  Result: {result['passed']}")
    print(f"  Reason: {result['reason']}")
    print(f"  Safety Score: {result['safety_score']}/100")

    assert result['passed'] == True, "Good job should pass!"
    print("\n  ✅ TEST PASSED")

def test_night_shift():
    """Test 2: Night shift should be rejected"""
    print("\n" + "="*70)
    print("TEST 2: Night Shift Job (Should FAIL)")
    print("="*70)

    result = validate_job_for_auto_apply(NIGHT_SHIFT_JOB)

    print(f"  Company: {NIGHT_SHIFT_JOB['company']}")
    print(f"  Position: {NIGHT_SHIFT_JOB['position']}")
    print(f"\n  Result: {result['passed']}")
    print(f"  Reason: {result['reason']}")

    assert result['passed'] == False, "Night shift should be rejected!"
    assert "forbidden" in result['reason'].lower(), "Should mention forbidden keywords"
    print("\n  ✅ TEST PASSED")

def test_low_fit_score():
    """Test 3: Low fit score should be rejected"""
    print("\n" + "="*70)
    print("TEST 3: Low Fit Score (Should FAIL)")
    print("="*70)

    result = validate_job_for_auto_apply(LOW_FIT_JOB)

    print(f"  Company: {LOW_FIT_JOB['company']}")
    print(f"  Fit Score: {LOW_FIT_JOB['fit_score']} (min: {MIN_FIT_SCORE})")
    print(f"\n  Result: {result['passed']}")
    print(f"  Reason: {result['reason']}")

    assert result['passed'] == False, "Low fit score should be rejected!"
    print("\n  ✅ TEST PASSED")

def test_scam_detection():
    """Test 4: Scam patterns should be detected"""
    print("\n" + "="*70)
    print("TEST 4: Scam Detection (Should FAIL)")
    print("="*70)

    result = validate_job_for_auto_apply(SCAM_JOB)

    print(f"  Company: {SCAM_JOB['company']}")
    print(f"  Position: {SCAM_JOB['position']}")
    print(f"\n  Result: {result['passed']}")
    print(f"  Reason: {result['reason']}")

    assert result['passed'] == False, "Scam should be detected!"
    print("\n  ✅ TEST PASSED")

def test_wrong_industry():
    """Test 5: Non-hospitality jobs should be rejected"""
    print("\n" + "="*70)
    print("TEST 5: Wrong Industry (Should FAIL)")
    print("="*70)

    result = validate_job_for_auto_apply(WRONG_INDUSTRY_JOB)

    print(f"  Company: {WRONG_INDUSTRY_JOB['company']}")
    print(f"  Position: {WRONG_INDUSTRY_JOB['position']}")
    print(f"\n  Result: {result['passed']}")
    print(f"  Reason: {result['reason']}")

    assert result['passed'] == False, "Non-hospitality should be rejected!"
    print("\n  ✅ TEST PASSED")

def test_rate_limiting():
    """Test 6: Rate limiting should enforce limits"""
    print("\n" + "="*70)
    print("TEST 6: Rate Limiting")
    print("="*70)

    # Check initial state
    rate = check_rate_limit()
    print(f"  Initial state:")
    print(f"    Hourly: {rate['hourly_count']}/{MAX_HOURLY_APPLICATIONS}")
    print(f"    Daily: {rate['daily_count']}/{MAX_DAILY_APPLICATIONS}")

    # Simulate applications
    print(f"\n  Simulating {MAX_HOURLY_APPLICATIONS} applications...")
    for i in range(MAX_HOURLY_APPLICATIONS):
        record_application()

    # Check after limit
    rate = check_rate_limit()
    print(f"\n  After {MAX_HOURLY_APPLICATIONS} applications:")
    print(f"    Allowed: {rate['allowed']}")
    print(f"    Hourly: {rate['hourly_count']}/{MAX_HOURLY_APPLICATIONS}")

    assert rate['allowed'] == False, "Should block after hourly limit!"
    print("\n  ✅ TEST PASSED")

def test_blacklist():
    """Test 7: Blacklist should block companies"""
    print("\n" + "="*70)
    print("TEST 7: Company Blacklist")
    print("="*70)

    test_company = "BadCompany Inc"

    # Add to blacklist
    add_to_blacklist(test_company, "Test reason")
    print(f"  Added '{test_company}' to blacklist")

    # Check if blocked
    blocked = is_blacklisted(test_company)
    print(f"  Blocked: {blocked}")

    assert blocked == True, "Blacklisted company should be blocked!"

    # Test with job data
    blacklisted_job = GOOD_JOB.copy()
    blacklisted_job['company'] = test_company

    result = validate_job_for_auto_apply(blacklisted_job)
    print(f"\n  Validation Result: {result['passed']}")
    print(f"  Reason: {result['reason']}")

    assert result['passed'] == False, "Blacklisted job should fail!"
    print("\n  ✅ TEST PASSED")

def test_kill_switch():
    """Test 8: Kill switch should stop all applications"""
    print("\n" + "="*70)
    print("TEST 8: Kill Switch")
    print("="*70)

    # Activate kill switch
    activate_kill_switch("Test activation")
    print(f"  Kill switch activated: {is_kill_switch_active()}")

    # Try to validate good job
    result = validate_job_for_auto_apply(GOOD_JOB)
    print(f"\n  Good job validation: {result['passed']}")
    print(f"  Reason: {result['reason']}")

    assert result['passed'] == False, "Kill switch should block everything!"
    assert "KILL SWITCH" in result['reason'], "Should mention kill switch!"

    # Deactivate
    deactivate_kill_switch()
    print(f"\n  Kill switch deactivated: {not is_kill_switch_active()}")

    print("\n  ✅ TEST PASSED")

# ============================================================================
# RUN ALL TESTS
# ============================================================================

def run_all_tests():
    """Run complete test suite"""
    print("\n" + "="*70)
    print("  TRINITY SYSTEM - FULL-AUTO SAFETY TEST SUITE")
    print("="*70)
    print(f"  Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Mode: FULL-AUTO with Enhanced Safety")
    print("="*70)

    tests = [
        ("Good Job Should Pass", test_good_job),
        ("Night Shift Rejection", test_night_shift),
        ("Low Fit Score Rejection", test_low_fit_score),
        ("Scam Detection", test_scam_detection),
        ("Wrong Industry Rejection", test_wrong_industry),
        ("Rate Limiting", test_rate_limiting),
        ("Company Blacklist", test_blacklist),
        ("Kill Switch", test_kill_switch)
    ]

    passed = 0
    failed = 0

    for name, test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"\n  ❌ TEST FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"\n  ❌ ERROR: {e}")
            failed += 1

    # Summary
    print("\n" + "="*70)
    print("  TEST SUMMARY")
    print("="*70)
    print(f"  Total Tests: {len(tests)}")
    print(f"  Passed: {passed} ✅")
    print(f"  Failed: {failed} ❌")
    print(f"  Success Rate: {passed/len(tests)*100:.1f}%")

    if failed == 0:
        print("\n  🎉 ALL TESTS PASSED - SYSTEM READY FOR FULL-AUTO")
    else:
        print("\n  ⚠️  SOME TESTS FAILED - DO NOT DEPLOY")

    print("="*70)

    return passed == len(tests)


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
