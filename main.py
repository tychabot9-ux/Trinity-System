#!/usr/bin/env python3
"""
Trinity System - Main Server
FastAPI server for mobile/web access

Endpoints:
- POST /job/analyze - Analyze job posting
- POST /job/apply - Process job application
- GET /job/status - Check application status
- POST /chat - Chat with Trinity
- GET /health - System health check
"""

import os
import psutil
import sqlite3
from typing import Optional
from pathlib import Path
from datetime import datetime
import re
from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv

# Set low CPU priority to protect trading bot
p = psutil.Process(os.getpid())
p.nice(10)
print("📉 Trinity CPU Priority set to Low (Background Mode)")

load_dotenv()

# Import Trinity components
from trinity_router import TrinityRouter
from job_sniper import JobSniper
from job_status import (
    init_job_status_db, add_job_status, update_job_status,
    get_jobs_by_status, check_duplicate_application, get_stats as get_job_stats
)

# ============================================================================
# CONFIGURATION
# ============================================================================

TRINITY_PASSWORD = os.getenv("TRINITY_PASSWORD")

# ============================================================================
# APP INITIALIZATION
# ============================================================================

app = FastAPI(
    title="Trinity System",
    description="Personal AI Operating System - Job Sniper + Command Interface",
    version="1.0"
)

# CORS for mobile access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize systems
trinity = TrinityRouter()
job_sniper = JobSniper()

# ============================================================================
# AUTHENTICATION
# ============================================================================

def verify_password(authorization: Optional[str] = Header(None)):
    """Verify Trinity password"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization required")

    if authorization != f"Bearer {TRINITY_PASSWORD}":
        raise HTTPException(status_code=403, detail="Invalid password")

    return True

# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class JobAnalysisRequest(BaseModel):
    job_url_or_text: str
    company: Optional[str] = "Unknown Company"
    position: Optional[str] = "Position"

class ChatRequest(BaseModel):
    message: str
    mode: Optional[str] = "auto"

class ApprovalRequest(BaseModel):
    approval_id: int
    action: str  # "approve" or "reject"

# ============================================================================
# ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Trinity System",
        "status": "online",
        "version": "1.0",
        "components": {
            "NEXUS": "online",
            "JARVIS": "online",
            "AVA": "online",
            "Job Sniper": "online"
        }
    }

@app.get("/health")
async def health_check():
    """System health check"""
    return {
        "status": "healthy",
        "cpu_priority": p.nice(),
        "memory_mb": psutil.Process().memory_info().rss / 1024 / 1024,
        "uptime": "running"
    }

@app.post("/job/analyze")
async def analyze_job(
    request: JobAnalysisRequest,
    authenticated: bool = Depends(verify_password)
):
    """
    Analyze a job posting without applying.

    Returns fit score, analysis, and recommendation.
    """
    try:
        result = trinity.analyze_job_posting(request.job_url_or_text)

        return {
            "status": "success",
            "company": request.company,
            "position": request.position,
            "fit_score": result.get("fit_score", 0),
            "recommendation": result.get("recommendation", "review"),
            "analysis": result.get("analysis", "")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/job/apply")
async def apply_to_job(
    request: JobAnalysisRequest,
    authenticated: bool = Depends(verify_password)
):
    """
    Process job application through Job Sniper.

    Handles filtering, analysis, and semi-auto approval workflow.
    """
    try:
        result = job_sniper.process_job(
            request.job_url_or_text,
            request.company,
            request.position
        )

        return {
            "status": "success",
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def chat(
    request: ChatRequest,
    authenticated: bool = Depends(verify_password)
):
    """
    Chat with Trinity (general conversation or command).

    Mode can be 'auto', 'job', or 'chat'.
    """
    try:
        result = trinity.route_command(request.message, mode=request.mode)

        return {
            "status": "success",
            "response": result.get("response", ""),
            "source": result.get("source", "Unknown")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/job/approve")
async def approve_application(
    request: ApprovalRequest,
    authenticated: bool = Depends(verify_password)
):
    """
    Approve or reject pending job application.

    Used in SEMI-AUTO mode workflow.
    """
    # TODO: Implement approval workflow
    return {
        "status": "success",
        "message": f"Application {request.action}ed",
        "approval_id": request.approval_id
    }

@app.get("/job/stats")
async def job_stats(authenticated: bool = Depends(verify_password)):
    """Get job application statistics"""
    from job_sniper import get_daily_application_count
    import sqlite3
    from pathlib import Path

    db_path = Path(__file__).parent / "job_logs" / "applications.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM applications")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM pending_approvals WHERE status = 'awaiting_approval'")
    pending = cursor.fetchone()[0]

    conn.close()

    return {
        "total_applications": total,
        "pending_approvals": pending,
        "applications_today": get_daily_application_count(),
        "daily_limit": 3
    }

# ============================================================================
# WEB DASHBOARD ENDPOINTS
# ============================================================================

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    """Serve the web dashboard"""
    dashboard_path = Path(__file__).parent / "dashboard.html"
    if dashboard_path.exists():
        return FileResponse(dashboard_path)
    return HTMLResponse("<h1>Trinity Dashboard</h1><p>Dashboard file not found</p>")

@app.get("/api/drafts")
async def get_drafts():
    """Get list of all draft emails with metadata"""
    drafts_dir = Path(__file__).parent / "email_drafts"

    if not drafts_dir.exists():
        return {"drafts": [], "stats": {"total": 0, "avg_score": 0, "today": 0}}

    drafts = []
    total_score = 0
    today = datetime.now().date()
    today_count = 0

    for draft_file in sorted(drafts_dir.glob("*.txt"), reverse=True):
        try:
            content = draft_file.read_text()

            # Extract metadata from filename: YYYYMMDD_HHMMSS_Company_Name_draft.txt
            match = re.match(r'(\d{8})_(\d{6})_(.+)_draft\.txt', draft_file.name)
            if not match:
                continue

            date_str, time_str, company_slug = match.groups()
            company = company_slug.replace('_', ' ')

            # Parse date
            file_date = datetime.strptime(date_str, '%Y%m%d').date()
            file_time = datetime.strptime(time_str, '%H%M%S').time()

            # Extract details from content
            lines = content.split('\n')
            subject_line = ""
            position = ""

            for i, line in enumerate(lines):
                if "SUBJECT:" in line and i + 1 < len(lines):
                    subject_line = lines[i + 1].strip()
                    if "Application for " in subject_line:
                        position = subject_line.replace("Application for ", "")
                    break

            # Get preview (first paragraph of cover letter)
            body_start = content.find("EMAIL BODY")
            if body_start > 0:
                body_section = content[body_start:]
                paragraphs = [p.strip() for p in body_section.split('\n\n') if p.strip() and not p.startswith('---')]
                preview = paragraphs[1] if len(paragraphs) > 1 else ""
                preview = preview[:200] + "..." if len(preview) > 200 else preview
            else:
                preview = "No preview available"

            # Try to extract fit score from previous notifications (not in draft file)
            # Default to 85 for estimation
            fit_score = 85

            drafts.append({
                "filename": draft_file.name,
                "company": company,
                "position": position or "Position",
                "fit_score": fit_score,
                "preview": preview,
                "date": f"{file_date} {file_time.strftime('%H:%M')}",
                "filepath": str(draft_file)
            })

            total_score += fit_score
            if file_date == today:
                today_count += 1

        except Exception as e:
            print(f"Error processing draft {draft_file.name}: {e}")
            continue

    avg_score = int(total_score / len(drafts)) if drafts else 0

    return {
        "drafts": drafts,
        "stats": {
            "total": len(drafts),
            "avg_score": avg_score,
            "today": today_count
        }
    }

@app.get("/api/draft/{filename}")
async def get_draft(filename: str):
    """Get full content of a specific draft"""
    drafts_dir = Path(__file__).parent / "email_drafts"
    draft_path = drafts_dir / filename

    if not draft_path.exists():
        raise HTTPException(status_code=404, detail="Draft not found")

    content = draft_path.read_text()

    # Extract metadata
    match = re.match(r'(\d{8})_(\d{6})_(.+)_draft\.txt', filename)
    company = match.groups()[2].replace('_', ' ') if match else "Unknown"

    # Extract subject and body
    lines = content.split('\n')
    subject = ""
    position = ""
    cover_letter = ""

    for i, line in enumerate(lines):
        if "SUBJECT:" in line and i + 1 < len(lines):
            subject = lines[i + 1].strip()
            if "Application for " in subject:
                position = subject.replace("Application for ", "")
        elif "EMAIL BODY" in line:
            # Get everything after "EMAIL BODY" section until "END EMAIL"
            body_start = i + 2
            body_lines = []
            for j in range(body_start, len(lines)):
                if "------- END EMAIL" in lines[j]:
                    break
                if not lines[j].startswith('━'):
                    body_lines.append(lines[j])
            cover_letter = '\n'.join(body_lines).strip()
            break

    return {
        "filename": filename,
        "company": company,
        "position": position or "Position",
        "subject": subject,
        "cover_letter": cover_letter,
        "filepath": str(draft_path)
    }

@app.get("/draft-file/{filename}")
async def serve_draft_file(filename: str):
    """Serve the raw draft file"""
    drafts_dir = Path(__file__).parent / "email_drafts"
    draft_path = drafts_dir / filename

    if not draft_path.exists():
        raise HTTPException(status_code=404, detail="Draft not found")

    return FileResponse(draft_path, media_type="text/plain", filename=filename)

@app.get("/api/resume")
async def get_resume():
    """Get resume data"""
    import json
    resume_path = Path(__file__).parent / "resume_data.json"

    if not resume_path.exists():
        raise HTTPException(status_code=404, detail="Resume not found")

    with open(resume_path, 'r') as f:
        resume_data = json.load(f)

    return resume_data

@app.post("/api/job/status")
async def update_status(request: dict):
    """Update job status (pending/applied/denied)"""
    filename = request.get('filename')
    new_status = request.get('status')
    notes = request.get('notes', '')

    if not filename or not new_status:
        raise HTTPException(status_code=400, detail="Missing filename or status")

    success = update_job_status(filename, new_status, notes)

    if success:
        return {"status": "success", "message": f"Job marked as {new_status}"}
    else:
        raise HTTPException(status_code=404, detail="Job not found")

@app.get("/api/jobs/organized")
async def get_organized_jobs():
    """Get jobs organized by status with contact info"""
    init_job_status_db()

    pending = get_jobs_by_status('pending')
    applied = get_jobs_by_status('applied')
    denied = get_jobs_by_status('denied')

    # Also get drafts and match them with statuses
    drafts_dir = Path(__file__).parent / "email_drafts"
    draft_files = {f.name: f for f in drafts_dir.glob("*.txt")} if drafts_dir.exists() else {}

    # Enhance with draft info
    for job_list in [pending, applied, denied]:
        for job in job_list:
            if job['draft_filename'] in draft_files:
                # Add draft preview
                draft_path = draft_files[job['draft_filename']]
                try:
                    content = draft_path.read_text()
                    preview_start = content.find("Dear Hiring Manager")
                    if preview_start > 0:
                        preview = content[preview_start:preview_start+150] + "..."
                    else:
                        preview = content[:150] + "..."
                    job['preview'] = preview
                except:
                    job['preview'] = "Preview unavailable"

    stats = get_job_stats()

    return {
        "pending": pending,
        "applied": applied,
        "denied": denied,
        "stats": stats
    }

@app.get("/api/resume/formatted")
async def get_formatted_resume():
    """Get formatted resume text ready to copy"""
    import json
    resume_path = Path(__file__).parent / "resume_data.json"

    if not resume_path.exists():
        raise HTTPException(status_code=404, detail="Resume not found")

    with open(resume_path, 'r') as f:
        data = json.load(f)

    # Format resume for hospitality positions
    formatted = f"""TY BROWN
{data['personal_info']['location']}
Phone: {data['personal_info']['phone']} • Email: {data['personal_info']['email']}
Driver's License • Reliable Vehicle

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PROFESSIONAL SUMMARY

{data['professional_summary']['hospitality']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CORE COMPETENCIES

"""
    # Add skills in columns
    skills = data['skills']
    for i in range(0, len(skills), 2):
        line = f"• {skills[i]:<45}"
        if i + 1 < len(skills):
            line += f"• {skills[i+1]}"
        formatted += line + "\n"

    formatted += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    formatted += "PROFESSIONAL EXPERIENCE\n\n"

    # Add work experience
    for job in data['work_experience']:
        formatted += f"{job['title']}\n"
        formatted += f"{job['company']} — {job['location']}\n"
        if 'dates' in job:
            formatted += f"{job['dates']}\n"
        formatted += "\n"

        for resp in job['responsibilities'][:5]:  # Top 5 responsibilities
            formatted += f"  • {resp}\n"
        formatted += "\n"

    formatted += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    formatted += f"EDUCATION\n\n{data['education']['high_school']} — {data['education']['status']}\n"
    formatted += f"{data['education']['additional']}\n"

    return {"formatted_resume": formatted}

# ============================================================================
# STARTUP
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    print("=" * 70)
    print("  TRINITY SYSTEM - SERVER STARTING")
    print("=" * 70)
    print(f"  CPU Priority: Low (10)")
    print(f"  Protection: Trading bots have priority")
    print(f"  Access: http://localhost:8001")
    print("=" * 70)

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        log_level="info"
    )
