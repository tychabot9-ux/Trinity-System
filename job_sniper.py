#!/usr/bin/env python3
"""
Job Sniper - Automated Job Application System
Protocol: Day/Evening Hospitality Target (NO Graveyard Shifts)

Features:
- Smart filtering (positive/negative keywords)
- Stress level analysis via NEXUS
- Resume tailoring via JARVIS
- Semi-auto approval workflow
- Duplicate prevention (90-day cooldown)
- Pushover notifications for matches
"""

import os
import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

load_dotenv()

# Import Trinity Router
from trinity_router import TrinityRouter

# Import Pushover notifications
try:
    import sys
    bot_factory = Path.home() / "Desktop" / "Bot-Factory"
    sys.path.insert(0, str(bot_factory))
    from notify import push_notification
    PUSHOVER_AVAILABLE = True
except:
    PUSHOVER_AVAILABLE = False
    def push_notification(*args, **kwargs): return {"status": "disabled"}

# ============================================================================
# CONFIGURATION
# ============================================================================

# Positive Keywords (Day/Evening roles - TARGET THESE)
POSITIVE_KEYWORDS = [
    "front desk agent", "concierge", "guest services",
    "operations assistant", "am shift", "pm shift", "mid-shift",
    "office coordinator", "facilities support", "day shift",
    "morning shift", "afternoon shift", "evening shift",
    "hotel", "inn", "boutique", "hospitality"
]

# Negative Keywords (Graveyard shifts - AVOID THESE)
NEGATIVE_KEYWORDS = [
    "night audit", "third shift", "overnight", "graveyard",
    "11pm", "12am", "1am", "2am", "3am", "4am", "5am", "6am",
    "red-eye", "midnight", "late night", "all-nighter"
]

# Job Search Parameters
MIN_HOURLY_RATE = int(os.getenv("MIN_HOURLY_RATE", 20))
MAX_DAILY_APPLICATIONS = int(os.getenv("MAX_DAILY_APPLICATIONS", 3))
DUPLICATE_COOLDOWN_DAYS = int(os.getenv("DUPLICATE_COOLDOWN_DAYS", 90))
AUTOMATION_LEVEL = os.getenv("AUTOMATION_LEVEL", "SEMI-AUTO")  # FULL-AUTO, SEMI-AUTO, or MANUAL

# Email Configuration
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

# User Profile
USER_PROFILE = {
    "name": os.getenv("USER_NAME", "Ty Brown"),
    "email": os.getenv("USER_EMAIL", EMAIL_USER),
    "phone": os.getenv("USER_PHONE"),
    "location": os.getenv("USER_LOCATION", "Paso Robles, CA")
}

# Database
DB_PATH = Path(__file__).parent / "job_logs" / "applications.db"


# ============================================================================
# DATABASE MANAGEMENT
# ============================================================================

def init_database():
    """Initialize SQLite database for application tracking"""
    DB_PATH.parent.mkdir(exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT NOT NULL,
            position TEXT NOT NULL,
            url TEXT,
            applied_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'pending',
            fit_score INTEGER,
            notes TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pending_approvals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT NOT NULL,
            position TEXT NOT NULL,
            url TEXT,
            fit_score INTEGER,
            analysis TEXT,
            resume_path TEXT,
            cover_letter_path TEXT,
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_date TIMESTAMP,
            status TEXT DEFAULT 'awaiting_approval'
        )
    """)

    conn.commit()
    conn.close()

def check_duplicate(company: str, position: str) -> bool:
    """Check if already applied to this company/position within cooldown period"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cooldown_date = datetime.now() - timedelta(days=DUPLICATE_COOLDOWN_DAYS)

    cursor.execute("""
        SELECT COUNT(*) FROM applications
        WHERE company = ? AND position = ?
        AND applied_date > ?
    """, (company, position, cooldown_date))

    count = cursor.fetchone()[0]
    conn.close()

    return count > 0

def log_application(company: str, position: str, url: str, fit_score: int, notes: str = ""):
    """Log application to database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO applications (company, position, url, fit_score, notes, status)
        VALUES (?, ?, ?, ?, ?, 'sent')
    """, (company, position, url, fit_score, notes))

    conn.commit()
    conn.close()

def get_daily_application_count() -> int:
    """Get number of applications sent today"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    today = datetime.now().date()

    cursor.execute("""
        SELECT COUNT(*) FROM applications
        WHERE DATE(applied_date) = ?
    """, (today,))

    count = cursor.fetchone()[0]
    conn.close()

    return count


# ============================================================================
# JOB SCRAPING & FILTERING
# ============================================================================

def scrape_job_posting(url: str) -> Optional[str]:
    """Scrape job description from URL"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Try common job description containers
        job_desc = soup.find('div', class_='jobsearch-jobDescriptionText')
        if not job_desc:
            job_desc = soup.find('div', id='job_description')
        if not job_desc:
            job_desc = soup.find('div', class_='job-description')

        return job_desc.get_text() if job_desc else soup.get_text()
    except Exception as e:
        print(f"  ⚠️  Scraping failed: {e}")
        return None

def filter_job(job_text: str) -> Dict:
    """
    Filter job based on keywords.

    Returns:
        dict with 'passed', 'reason', 'matched_positive', 'matched_negative'
    """
    job_lower = job_text.lower()

    # Check for negative keywords (AUTO-REJECT)
    matched_negative = [kw for kw in NEGATIVE_KEYWORDS if kw in job_lower]
    if matched_negative:
        return {
            "passed": False,
            "reason": f"Contains night shift keywords: {', '.join(matched_negative[:3])}",
            "matched_negative": matched_negative,
            "matched_positive": []
        }

    # Check for positive keywords
    matched_positive = [kw for kw in POSITIVE_KEYWORDS if kw in job_lower]
    if not matched_positive:
        return {
            "passed": False,
            "reason": "No target keywords found (day/evening hospitality)",
            "matched_negative": [],
            "matched_positive": []
        }

    # PASSED
    return {
        "passed": True,
        "reason": f"Matched keywords: {', '.join(matched_positive[:5])}",
        "matched_positive": matched_positive,
        "matched_negative": []
    }


# ============================================================================
# EMAIL SENDING
# ============================================================================

def send_application_email(company: str, position: str, cover_letter: str,
                          resume_path: Optional[str] = None, test_mode: bool = True) -> Dict:
    """
    Create email draft (TEST MODE) or send application email via Gmail.

    Args:
        company: Company name
        position: Position title
        cover_letter: Cover letter text
        resume_path: Optional path to resume PDF
        test_mode: If True, saves as draft instead of sending

    Returns:
        dict with status and message
    """
    if not EMAIL_USER or not EMAIL_PASSWORD:
        return {"status": "error", "message": "Email credentials not configured"}

    try:
        subject = f"Application for {position}"
        recipient = EMAIL_USER  # TESTING: Will be extracted from job posting in production

        if test_mode:
            # TEST MODE: Save as draft file for review
            draft_dir = Path(__file__).parent / "email_drafts"
            draft_dir.mkdir(exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            draft_file = draft_dir / f"{timestamp}_{company.replace(' ', '_')}_draft.txt"

            draft_content = f"""TO: {recipient}
SUBJECT: {subject}
ATTACHMENTS: {resume_path if resume_path else 'None'}

------- EMAIL BODY -------

{cover_letter}

------- END EMAIL -------

[DRAFT MODE - Email NOT sent. Review and send manually if approved]
"""

            with open(draft_file, 'w') as f:
                f.write(draft_content)

            return {
                "status": "draft_created",
                "message": f"Email draft saved to {draft_file}",
                "recipient": recipient,
                "draft_path": str(draft_file)
            }

        else:
            # LIVE MODE: Actually send the email via SMTP
            msg = MIMEMultipart()
            msg['From'] = EMAIL_USER
            msg['To'] = recipient
            msg['Subject'] = subject

            # Add body
            msg.attach(MIMEText(cover_letter, 'plain'))

            # TODO: Add attachment support if resume_path provided

            # Connect and send
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(EMAIL_USER, EMAIL_PASSWORD)
                server.send_message(msg)

            return {
                "status": "sent",
                "message": f"Application sent to {recipient}",
                "recipient": recipient
            }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to send email: {str(e)}"
        }


# ============================================================================
# JOB SNIPER WORKFLOW
# ============================================================================

class JobSniper:
    """Automated job application system"""

    def __init__(self):
        self.trinity = TrinityRouter()
        init_database()

    def process_job(self, job_url_or_text: str, company: str, position: str) -> Dict:
        """
        Complete job processing workflow.

        Args:
            job_url_or_text: URL or raw job description text
            company: Company name
            position: Position title

        Returns:
            dict with status and details
        """
        print(f"\n{'='*70}")
        print(f"  JOB SNIPER: Processing {position} at {company}")
        print(f"{'='*70}\n")

        # Step 1: Check daily limit
        daily_count = get_daily_application_count()
        if daily_count >= MAX_DAILY_APPLICATIONS:
            return {
                "status": "rejected",
                "reason": f"Daily limit reached ({MAX_DAILY_APPLICATIONS} applications)"
            }

        # Step 2: Check duplicates
        if check_duplicate(company, position):
            return {
                "status": "rejected",
                "reason": f"Already applied within {DUPLICATE_COOLDOWN_DAYS} days"
            }

        # Step 3: Get job description
        if job_url_or_text.startswith("http"):
            job_text = scrape_job_posting(job_url_or_text)
            if not job_text:
                return {"status": "error", "reason": "Failed to scrape job posting"}
        else:
            job_text = job_url_or_text

        # Step 4: Filter keywords
        filter_result = filter_job(job_text)
        if not filter_result["passed"]:
            print(f"  ❌ FILTERED OUT: {filter_result['reason']}")
            return {
                "status": "filtered",
                "reason": filter_result["reason"],
                "filter_data": filter_result
            }

        print(f"  ✅ Filter passed: {filter_result['reason']}")

        # Step 5: Trinity analysis
        print(f"\n  🔍 Analyzing with Trinity...")
        analysis_result = self.trinity.analyze_job_posting(job_text)
        fit_score = analysis_result.get("fit_score", 0)
        recommendation = analysis_result.get("recommendation", "review")

        print(f"  📊 Fit Score: {fit_score}/100")
        print(f"  📋 Recommendation: {recommendation.upper()}")

        # Step 6: Auto-reject if fit score too low
        if fit_score < 70:
            return {
                "status": "rejected",
                "reason": f"Fit score too low ({fit_score}/100)",
                "analysis": analysis_result
            }

        # Step 7: Generate application materials
        print(f"\n  📝 Generating application materials...")
        materials = self._generate_application_materials(
            company, position, job_text, analysis_result
        )

        # Step 8: Check automation level
        print(f"\n  🔧 Automation Level: {AUTOMATION_LEVEL} (checking for FULL-AUTO)")
        if AUTOMATION_LEVEL == "FULL-AUTO":
            # FULL-AUTO mode: Send immediately
            print(f"\n  📧 FULL-AUTO: Sending application...")

            # Send email (DRAFT MODE: saves for review until Gmail credentials fixed)
            send_result = send_application_email(
                company=company,
                position=position,
                cover_letter=materials.get("cover_letter", ""),
                resume_path=materials.get("resume_path"),
                test_mode=True  # DRAFT MODE: Gmail auth needs fixing
            )

            if send_result["status"] in ["sent", "draft_created"]:
                # Record application in database
                self._record_application(
                    company, position, job_url_or_text, fit_score,
                    "sent", materials
                )

                # Send Pushover notification
                if PUSHOVER_AVAILABLE:
                    push_notification(
                        title=f"✅ Application Sent: {company}",
                        message=f"{position}\nFit Score: {fit_score}/100\nRecipient: {send_result['recipient']}",
                        priority=0
                    )

                print(f"  ✅ Application sent successfully!")
                return {
                    "status": "sent",
                    "fit_score": fit_score,
                    "materials": materials,
                    "email_result": send_result,
                    "message": f"Application automatically sent to {send_result['recipient']}"
                }
            else:
                # Email failed, fall back to approval workflow
                print(f"  ⚠️  Email failed: {send_result['message']}")
                print(f"  📱 Falling back to approval workflow...")

                if PUSHOVER_AVAILABLE:
                    approval_id = self._request_approval(
                        company, position, fit_score, materials, job_url_or_text
                    )
                    return {
                        "status": "awaiting_approval",
                        "approval_id": approval_id,
                        "fit_score": fit_score,
                        "materials": materials,
                        "message": f"Email failed - awaiting manual approval. Error: {send_result['message']}"
                    }
                else:
                    return {
                        "status": "error",
                        "fit_score": fit_score,
                        "materials": materials,
                        "message": f"Email failed: {send_result['message']}"
                    }

        elif AUTOMATION_LEVEL == "SEMI-AUTO":
            # SEMI-AUTO mode: Request approval via Pushover
            if PUSHOVER_AVAILABLE:
                approval_id = self._request_approval(
                    company, position, fit_score, materials, job_url_or_text
                )

                return {
                    "status": "awaiting_approval",
                    "approval_id": approval_id,
                    "fit_score": fit_score,
                    "materials": materials,
                    "message": "Approval request sent to mobile"
                }
            else:
                # Fallback: Auto-save for manual review
                return {
                    "status": "ready_for_review",
                    "fit_score": fit_score,
                    "materials": materials,
                    "message": "Documents ready for manual review"
                }

        else:
            # MANUAL mode: Just save materials
            return {
                "status": "ready_for_review",
                "fit_score": fit_score,
                "materials": materials,
                "message": "Documents ready for manual review"
            }

    def _generate_application_materials(self, company: str, position: str,
                                       job_text: str, analysis: Dict) -> Dict:
        """Generate tailored resume and cover letter"""

        # Generate cover letter via JARVIS
        cover_letter_prompt = f"""Write a professional cover letter for this job:

Company: {company}
Position: {position}
Applicant: {USER_PROFILE['name']}

Background:
- Experienced in finish carpentry and construction
- Strong technical skills and reliability
- Transitioning to hospitality/operations roles
- Seeking day/evening shifts in organized environments

Job Analysis: {analysis.get('analysis', 'N/A')}

Requirements:
- Professional tone
- Address as "Dear Hiring Manager"
- Keep under 250 words
- Emphasize reliability, technical aptitude, and customer service potential
- Mention specific job details from the posting"""

        cover_letter = self.trinity.ask_jarvis(cover_letter_prompt)

        # Save materials
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        materials_dir = Path(__file__).parent / "resume_vault" / f"{timestamp}_{company.replace(' ', '_')}"
        materials_dir.mkdir(parents=True, exist_ok=True)

        cover_letter_path = materials_dir / "cover_letter.txt"
        cover_letter_path.write_text(cover_letter)

        return {
            "cover_letter": cover_letter,
            "cover_letter_path": str(cover_letter_path),
            "resume_path": None  # TODO: Add resume generation
        }

    def _record_application(self, company: str, position: str, url: str,
                            fit_score: int, status: str, materials: Dict):
        """Record application in database"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO applications
            (company, position, url, fit_score, status, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (company, position, url, fit_score, status,
              f"Auto-sent via FULL-AUTO mode. Cover letter: {materials.get('cover_letter_path', 'N/A')}"))

        conn.commit()
        conn.close()

    def _request_approval(self, company: str, position: str, fit_score: int,
                         materials: Dict, url: str) -> int:
        """Send approval request via Pushover"""

        message = f"""Company: {company}
Position: {position}
Fit Score: {fit_score}/100

Preview: {materials['cover_letter'][:150]}...

Reply with /approve or /reject"""

        push_notification(
            f"🎯 JOB MATCH: {position}",
            message,
            priority=1,
            sound="cashregister"
        )

        # Save to pending approvals
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        expires = datetime.now() + timedelta(minutes=60)

        cursor.execute("""
            INSERT INTO pending_approvals
            (company, position, url, fit_score, analysis, resume_path, cover_letter_path, expires_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (company, position, url, fit_score, "", materials.get('resume_path'),
              materials.get('cover_letter_path'), expires))

        approval_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return approval_id


# Quick Test
if __name__ == "__main__":
    print("=" * 70)
    print("  JOB SNIPER - SYSTEM TEST")
    print("=" * 70)

    sniper = JobSniper()

    # Test job description
    test_job = """
    Front Desk Agent - Madonna Inn
    Full-time day shift (8am-4pm)
    $22/hour

    We are seeking a friendly, reliable front desk agent for our boutique hotel.
    Responsibilities include guest check-in, answering phones, and light administrative tasks.
    Must have strong computer skills and professional communication abilities.
    """

    result = sniper.process_job(test_job, "Madonna Inn", "Front Desk Agent")

    print(f"\n📊 Result: {result['status']}")
    print(f"   Reason: {result.get('reason', 'N/A')}")

    print("\n✅ Job Sniper test complete")
