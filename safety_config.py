#!/usr/bin/env python3
"""
Safety Configuration - Enhanced Controls for Full-Auto Mode

Multi-layer safety system:
1. Fit Score Threshold (80+)
2. Confidence Score (85+)
3. Rate Limiting (3/hour, 10/day)
4. Company Blacklist
5. Keyword Verification
6. Email Preview Logging
7. Kill Switch
8. Daily Summaries
"""

import os
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()

# ============================================================================
# SAFETY THRESHOLDS
# ============================================================================

# Fit Score: NEXUS rating of job match (0-100)
MIN_FIT_SCORE = int(os.getenv("MIN_FIT_SCORE_AUTO", 80))

# Confidence Score: Combined analysis certainty (0-100)
MIN_CONFIDENCE_SCORE = int(os.getenv("MIN_CONFIDENCE_SCORE", 85))

# Rate Limits
MAX_DAILY_APPLICATIONS = int(os.getenv("MAX_DAILY_APPLICATIONS", 10))
MAX_HOURLY_APPLICATIONS = int(os.getenv("MAX_APPLICATIONS_PER_HOUR", 3))

# Duplicate Prevention
DUPLICATE_COOLDOWN_DAYS = int(os.getenv("DUPLICATE_COOLDOWN_DAYS", 90))

# ============================================================================
# COMPANY BLACKLIST
# ============================================================================

BLACKLIST_FILE = Path(__file__).parent / "job_logs" / "blacklist.json"

def load_blacklist() -> List[str]:
    """Load company blacklist"""
    if BLACKLIST_FILE.exists():
        with open(BLACKLIST_FILE) as f:
            return json.load(f).get("companies", [])
    return []

def add_to_blacklist(company: str, reason: str = ""):
    """Add company to blacklist"""
    blacklist = load_blacklist()
    if company.lower() not in [c.lower() for c in blacklist]:
        blacklist.append(company)

        BLACKLIST_FILE.parent.mkdir(exist_ok=True)
        with open(BLACKLIST_FILE, 'w') as f:
            json.dump({
                "companies": blacklist,
                "updated": datetime.now().isoformat(),
                "reasons": {company: reason}
            }, f, indent=2)

def is_blacklisted(company: str) -> bool:
    """Check if company is blacklisted"""
    blacklist = load_blacklist()
    return company.lower() in [c.lower() for c in blacklist]

# ============================================================================
# REQUIRED KEYWORDS (Must have at least one)
# ============================================================================

REQUIRED_KEYWORDS = [
    "front desk", "concierge", "guest services",
    "hotel", "inn", "hospitality", "operations",
    "receptionist", "office", "facilities"
]

# ============================================================================
# FORBIDDEN KEYWORDS (Instant rejection)
# ============================================================================

FORBIDDEN_KEYWORDS = [
    "night audit", "overnight", "graveyard", "third shift",
    "11pm", "12am", "midnight", "late night", "all-nighter",
    "commission only", "unpaid", "volunteer", "internship",
    "mlm", "multi-level", "pyramid", "work from home"
]

# ============================================================================
# SUSPICIOUS PATTERNS (High scrutiny)
# ============================================================================

SUSPICIOUS_PATTERNS = [
    "make money fast", "unlimited income", "be your own boss",
    "no experience required", "easy money", "guaranteed income"
]

# ============================================================================
# RATE LIMITING
# ============================================================================

RATE_LIMIT_FILE = Path(__file__).parent / "job_logs" / "rate_limits.json"

def check_rate_limit() -> Dict:
    """
    Check if rate limits are exceeded.

    Returns:
        dict with 'allowed', 'hourly_count', 'daily_count'
    """
    now = datetime.now()

    # Load rate limit data
    if RATE_LIMIT_FILE.exists():
        with open(RATE_LIMIT_FILE) as f:
            data = json.load(f)
    else:
        data = {"applications": []}

    # Filter to recent applications
    one_hour_ago = now - timedelta(hours=1)
    today = now.date()

    applications = [
        datetime.fromisoformat(ts)
        for ts in data.get("applications", [])
    ]

    hourly_applications = [ts for ts in applications if ts > one_hour_ago]
    daily_applications = [ts for ts in applications if ts.date() == today]

    hourly_count = len(hourly_applications)
    daily_count = len(daily_applications)

    # Check limits
    if hourly_count >= MAX_HOURLY_APPLICATIONS:
        return {
            "allowed": False,
            "reason": f"Hourly limit reached ({hourly_count}/{MAX_HOURLY_APPLICATIONS})",
            "hourly_count": hourly_count,
            "daily_count": daily_count
        }

    if daily_count >= MAX_DAILY_APPLICATIONS:
        return {
            "allowed": False,
            "reason": f"Daily limit reached ({daily_count}/{MAX_DAILY_APPLICATIONS})",
            "hourly_count": hourly_count,
            "daily_count": daily_count
        }

    return {
        "allowed": True,
        "hourly_count": hourly_count,
        "daily_count": daily_count
    }

def record_application():
    """Record application timestamp for rate limiting"""
    now = datetime.now()

    # Load existing data
    if RATE_LIMIT_FILE.exists():
        with open(RATE_LIMIT_FILE) as f:
            data = json.load(f)
    else:
        data = {"applications": []}

    # Add new timestamp
    data["applications"].append(now.isoformat())

    # Keep only last 24 hours
    one_day_ago = now - timedelta(days=1)
    data["applications"] = [
        ts for ts in data["applications"]
        if datetime.fromisoformat(ts) > one_day_ago
    ]

    # Save
    RATE_LIMIT_FILE.parent.mkdir(exist_ok=True)
    with open(RATE_LIMIT_FILE, 'w') as f:
        json.dump(data, f, indent=2)

# ============================================================================
# KILL SWITCH
# ============================================================================

KILL_SWITCH_FILE = Path(__file__).parent / "job_logs" / "KILL_SWITCH"

def is_kill_switch_active() -> bool:
    """Check if kill switch has been activated"""
    return KILL_SWITCH_FILE.exists()

def activate_kill_switch(reason: str = "Manual activation"):
    """Activate emergency kill switch"""
    KILL_SWITCH_FILE.parent.mkdir(exist_ok=True)
    KILL_SWITCH_FILE.write_text(json.dumps({
        "activated": datetime.now().isoformat(),
        "reason": reason
    }, indent=2))

    # Send emergency notification
    try:
        import sys
        bot_factory = Path.home() / "Desktop" / "Bot-Factory"
        sys.path.insert(0, str(bot_factory))
        from notify import push_notification

        push_notification(
            "🚨 TRINITY KILL SWITCH ACTIVATED",
            f"All job applications stopped.\nReason: {reason}",
            priority=2,
            sound="siren"
        )
    except:
        pass

def deactivate_kill_switch():
    """Deactivate kill switch"""
    if KILL_SWITCH_FILE.exists():
        KILL_SWITCH_FILE.unlink()

# ============================================================================
# SAFETY VALIDATION
# ============================================================================

def validate_job_for_auto_apply(job_data: Dict) -> Dict:
    """
    Comprehensive safety validation for full-auto mode.

    Args:
        job_data: dict with 'company', 'position', 'job_text', 'fit_score', etc.

    Returns:
        dict with 'passed', 'reason', 'safety_score'
    """
    checks = []

    # Check 1: Kill Switch
    if is_kill_switch_active():
        return {
            "passed": False,
            "reason": "KILL SWITCH ACTIVE - All applications stopped",
            "safety_score": 0
        }

    # Check 2: Rate Limits
    rate_check = check_rate_limit()
    if not rate_check["allowed"]:
        return {
            "passed": False,
            "reason": rate_check["reason"],
            "safety_score": 30
        }
    checks.append(("Rate Limit", True))

    # Check 3: Blacklist
    if is_blacklisted(job_data.get("company", "")):
        return {
            "passed": False,
            "reason": f"Company blacklisted: {job_data['company']}",
            "safety_score": 0
        }
    checks.append(("Blacklist", True))

    # Check 4: Fit Score
    fit_score = job_data.get("fit_score", 0)
    if fit_score < MIN_FIT_SCORE:
        return {
            "passed": False,
            "reason": f"Fit score too low: {fit_score} < {MIN_FIT_SCORE}",
            "safety_score": 40
        }
    checks.append(("Fit Score", True))

    # Check 5: Forbidden Keywords
    job_text_lower = job_data.get("job_text", "").lower()
    forbidden_found = [kw for kw in FORBIDDEN_KEYWORDS if kw in job_text_lower]
    if forbidden_found:
        return {
            "passed": False,
            "reason": f"Forbidden keywords: {', '.join(forbidden_found[:3])}",
            "safety_score": 20
        }
    checks.append(("Forbidden Keywords", True))

    # Check 6: Required Keywords
    required_found = [kw for kw in REQUIRED_KEYWORDS if kw in job_text_lower]
    if not required_found:
        return {
            "passed": False,
            "reason": "No required hospitality keywords found",
            "safety_score": 50
        }
    checks.append(("Required Keywords", True))

    # Check 7: Suspicious Patterns
    suspicious_found = [p for p in SUSPICIOUS_PATTERNS if p in job_text_lower]
    if suspicious_found:
        return {
            "passed": False,
            "reason": f"Suspicious patterns detected: {', '.join(suspicious_found)}",
            "safety_score": 30
        }
    checks.append(("Suspicious Patterns", True))

    # ALL CHECKS PASSED
    return {
        "passed": True,
        "reason": "All safety checks passed",
        "safety_score": 100,
        "checks_passed": checks
    }


# Quick Test
if __name__ == "__main__":
    print("=" * 70)
    print("  SAFETY CONFIGURATION TEST")
    print("=" * 70)

    print(f"\n📊 Safety Thresholds:")
    print(f"  Min Fit Score: {MIN_FIT_SCORE}")
    print(f"  Min Confidence: {MIN_CONFIDENCE_SCORE}")
    print(f"  Max Daily: {MAX_DAILY_APPLICATIONS}")
    print(f"  Max Hourly: {MAX_HOURLY_APPLICATIONS}")

    print(f"\n🔒 Rate Limits:")
    rate = check_rate_limit()
    print(f"  Allowed: {rate['allowed']}")
    print(f"  Hourly: {rate['hourly_count']}/{MAX_HOURLY_APPLICATIONS}")
    print(f"  Daily: {rate['daily_count']}/{MAX_DAILY_APPLICATIONS}")

    print(f"\n🚨 Kill Switch: {'ACTIVE' if is_kill_switch_active() else 'Inactive'}")

    print("\n✅ Safety system test complete")
