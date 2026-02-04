#!/usr/bin/env python3
"""
Job Status Management System
Tracks job applications: pending → applied → denied/accepted
Prevents duplicate applications
"""

import json
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Database path
DB_PATH = Path(__file__).parent / "job_logs" / "job_status.db"

def init_job_status_db():
    """Initialize job status database"""
    DB_PATH.parent.mkdir(exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS job_statuses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            draft_filename TEXT UNIQUE,
            company TEXT NOT NULL,
            position TEXT NOT NULL,
            fit_score INTEGER,
            status TEXT DEFAULT 'pending',
            contact_email TEXT,
            contact_name TEXT,
            contact_phone TEXT,
            job_url TEXT,
            source TEXT,
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            applied_date TIMESTAMP,
            response_date TIMESTAMP,
            notes TEXT
        )
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_status ON job_statuses(status)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_company ON job_statuses(company)
    """)

    conn.commit()
    conn.close()

def add_job_status(draft_filename: str, company: str, position: str,
                   fit_score: int, contact_info: Dict = None,
                   job_url: str = None, source: str = "manual") -> int:
    """Add new job to status tracking"""
    init_job_status_db()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    contact_info = contact_info or {}

    try:
        cursor.execute("""
            INSERT INTO job_statuses
            (draft_filename, company, position, fit_score, contact_email,
             contact_name, contact_phone, job_url, source, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending')
        """, (
            draft_filename,
            company,
            position,
            fit_score,
            contact_info.get('email'),
            contact_info.get('name'),
            contact_info.get('phone'),
            job_url,
            source
        ))

        job_id = cursor.lastrowid
        conn.commit()
        return job_id

    except sqlite3.IntegrityError:
        # Already exists, return existing ID
        cursor.execute("SELECT id FROM job_statuses WHERE draft_filename = ?", (draft_filename,))
        result = cursor.fetchone()
        return result[0] if result else None
    finally:
        conn.close()

def update_job_status(draft_filename: str, new_status: str, notes: str = None) -> bool:
    """Update job status (pending → applied → denied/accepted)"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    timestamp_field = None
    if new_status == 'applied':
        timestamp_field = 'applied_date'
    elif new_status in ['denied', 'accepted', 'no_response']:
        timestamp_field = 'response_date'

    if timestamp_field:
        cursor.execute(f"""
            UPDATE job_statuses
            SET status = ?, {timestamp_field} = ?, notes = ?
            WHERE draft_filename = ?
        """, (new_status, datetime.now(), notes, draft_filename))
    else:
        cursor.execute("""
            UPDATE job_statuses
            SET status = ?, notes = ?
            WHERE draft_filename = ?
        """, (new_status, notes, draft_filename))

    success = cursor.rowcount > 0
    conn.commit()
    conn.close()

    return success

def get_jobs_by_status(status: str = None) -> List[Dict]:
    """Get jobs filtered by status"""
    init_job_status_db()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if status:
        cursor.execute("""
            SELECT id, draft_filename, company, position, fit_score, status,
                   contact_email, contact_name, contact_phone, job_url, source,
                   created_date, applied_date, response_date, notes
            FROM job_statuses
            WHERE status = ?
            ORDER BY created_date DESC
        """, (status,))
    else:
        cursor.execute("""
            SELECT id, draft_filename, company, position, fit_score, status,
                   contact_email, contact_name, contact_phone, job_url, source,
                   created_date, applied_date, response_date, notes
            FROM job_statuses
            ORDER BY
                CASE status
                    WHEN 'pending' THEN 1
                    WHEN 'applied' THEN 2
                    WHEN 'denied' THEN 3
                    WHEN 'accepted' THEN 4
                    ELSE 5
                END,
                created_date DESC
        """)

    rows = cursor.fetchall()
    conn.close()

    jobs = []
    for row in rows:
        jobs.append({
            'id': row[0],
            'draft_filename': row[1],
            'company': row[2],
            'position': row[3],
            'fit_score': row[4],
            'status': row[5],
            'contact_email': row[6],
            'contact_name': row[7],
            'contact_phone': row[8],
            'job_url': row[9],
            'source': row[10],
            'created_date': row[11],
            'applied_date': row[12],
            'response_date': row[13],
            'notes': row[14]
        })

    return jobs

def check_duplicate_application(company: str, position: str) -> Optional[Dict]:
    """Check if already applied to this company/position"""
    init_job_status_db()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT status, applied_date
        FROM job_statuses
        WHERE LOWER(company) = LOWER(?)
        AND LOWER(position) = LOWER(?)
        AND status IN ('pending', 'applied')
        ORDER BY created_date DESC
        LIMIT 1
    """, (company, position))

    result = cursor.fetchone()
    conn.close()

    if result:
        return {
            'status': result[0],
            'applied_date': result[1]
        }

    return None

def get_stats() -> Dict:
    """Get application statistics"""
    init_job_status_db()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM job_statuses WHERE status = 'pending'")
    pending = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM job_statuses WHERE status = 'applied'")
    applied = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM job_statuses WHERE status = 'denied'")
    denied = cursor.fetchone()[0]

    cursor.execute("SELECT AVG(fit_score) FROM job_statuses")
    avg_score = cursor.fetchone()[0] or 0

    conn.close()

    return {
        'pending': pending,
        'applied': applied,
        'denied': denied,
        'avg_score': int(avg_score)
    }

if __name__ == "__main__":
    # Test the system
    init_job_status_db()
    print("✅ Job status database initialized")
    print(f"📊 Stats: {get_stats()}")
