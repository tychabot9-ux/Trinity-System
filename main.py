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
from typing import Optional
from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
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
