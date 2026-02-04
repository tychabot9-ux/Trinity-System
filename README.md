# 🚀 Trinity System - Personal AI Operating System

**Status:** ✅ Deployed and Operational
**Version:** 1.0
**Deployment Date:** February 3, 2026

---

## 📊 System Architecture

Trinity is a multi-AI routing system that coordinates three specialized AI models:

| Component | Engine | Function |
|-----------|--------|----------|
| **NEXUS** | Gemini 1.5 Pro | Memory, analysis, job screening |
| **JARVIS** | Claude Sonnet 4.5 | Logic, writing, resume tailoring |
| **AVA** | edge-tts (Microsoft) | Voice interface |
| **Job Sniper** | NEXUS + JARVIS | Automated job applications |

---

## 🎯 Primary Mission: Job Sniper

**Target:** Day/Evening Hospitality Roles
**Location:** 50 miles from Paso Robles, CA 93446
**Mode:** SEMI-AUTO (approval required)

### Target Keywords (Auto-Match):
- Front Desk Agent
- Concierge
- Guest Services
- Operations Assistant
- AM/PM/Mid Shift

### Blocked Keywords (Auto-Reject):
- Night Audit
- Third Shift
- Overnight
- Graveyard
- 11pm-7am

### Safety Limits:
- Max 3 applications per day
- 90-day company cooldown
- Minimum $20/hour
- Fit score > 70/100 required

---

## 🚀 Quick Start

### Start the Server:
```bash
cd ~/Desktop/Trinity-System
./start_trinity.sh
```

Server runs on: `http://localhost:8001`

### Test the System:
```bash
curl -H "Authorization: Bearer pineapple9devices" \
     http://localhost:8001/health
```

---

## 📱 API Endpoints

### Health Check
```bash
GET /health
```

### Analyze Job (No Application)
```bash
POST /job/analyze
Authorization: Bearer pineapple9devices
Content-Type: application/json

{
  "job_url_or_text": "Front Desk Agent...",
  "company": "Madonna Inn",
  "position": "Front Desk Agent"
}
```

### Apply to Job (Full Workflow)
```bash
POST /job/apply
Authorization: Bearer pineapple9devices
Content-Type: application/json

{
  "job_url_or_text": "https://indeed.com/job/...",
  "company": "Hotel Name",
  "position": "Position Title"
}
```

### Chat with Trinity
```bash
POST /chat
Authorization: Bearer pineapple9devices
Content-Type: application/json

{
  "message": "What is the weather today?",
  "mode": "auto"
}
```

### Job Statistics
```bash
GET /job/stats
Authorization: Bearer pineapple9devices
```

---

## 🔐 Security

**Trinity Password:** `pineapple9devices`
**Storage:** All credentials in `.env` (NOT committed to git)

### Protected Resources:
- All API endpoints require authentication
- CPU priority set to 10 (low) to protect trading bots
- Application database: `job_logs/applications.db`

---

## 📁 Directory Structure

```
Trinity-System/
├── .env                    # Credentials (DO NOT COMMIT)
├── main.py                 # FastAPI server
├── trinity_router.py       # AI routing brain
├── job_sniper.py          # Job application automation
├── start_trinity.sh       # Startup script
├── venv/                  # Virtual environment
├── memory_core/           # Long-term memory (future)
├── voice_modules/         # Voice commands (future)
├── resume_vault/          # Generated resumes/letters
└── job_logs/             # Application tracking database
```

---

## 🔄 SEMI-AUTO Workflow

1. **Job Found** → Trinity analyzes automatically
2. **Filter Check** → Blocks night shifts, checks keywords
3. **Fit Score** → NEXUS rates 0-100
4. **If Score > 70** → Generates resume + cover letter
5. **Pushover Alert** → You get mobile notification
6. **Your Decision** → Approve or reject within 60 minutes
7. **If Approved** → Email sent automatically
8. **If Timeout** → Application expires (no send)

---

## 📊 Application Tracking

All applications logged to SQLite database:

```bash
sqlite3 job_logs/applications.db

SELECT * FROM applications ORDER BY applied_date DESC LIMIT 10;
```

---

## 🔧 Maintenance

### View Logs:
```bash
tail -f trinity.log
```

### Check Database:
```bash
sqlite3 job_logs/applications.db ".tables"
```

### Update Credentials:
```bash
nano .env
```

---

## ⚠️ Important Notes

1. **CPU Priority**: Trinity runs at low priority (10) to never interfere with Mark XII Phoenix trading bot
2. **Daily Limit**: Maximum 3 applications per day (safety limit)
3. **Duplicate Prevention**: Cannot apply to same company within 90 days
4. **Shift Filter**: Automatically rejects any job mentioning night/graveyard shifts

---

## 🎯 Next Steps

1. ✅ System deployed and operational
2. ⏳ Test with real job posting
3. ⏳ Validate semi-auto approval workflow
4. ⏳ Monitor first week of applications
5. ⏳ Adjust filters based on results

---

## 📞 Integration Points

**Pushover:** Configured for mobile notifications
**Gmail:** tybrown963@gmail.com (automated sending)
**Bot-Factory:** Isolated - no file sharing
**Ava Voice:** Integrated from Bot-Factory/ava_speak.py

---

**Built:** February 3, 2026
**Status:** Production Ready 🚀
