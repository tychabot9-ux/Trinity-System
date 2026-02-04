# Trinity System - Job Application Workflow

## ✅ Current System Status

Trinity System is **fully operational** with the following features:

### 🎯 Core Features
- **Multi-AI Router**: NEXUS (Gemini) for analysis, JARVIS (Claude) for writing
- **Job Sniper**: Analyzes jobs and generates custom cover letters
- **Web Dashboard**: Track applications with 3-section organization
- **Status Management**: Pending → Applied → Denied/No Response
- **Duplicate Detection**: Prevents applying to same job twice
- **Contact Extraction**: Automatically finds hiring manager info
- **Low CPU Priority**: Runs at nice level 10 to protect trading bot

### 📊 Dashboard Features
- **3 Organized Sections**: Pending Review, Applied, Passed/No Response
- **Checkboxes**: Quick status updates with one click
- **Contact Info Display**: Email, phone, name when available
- **Resume Modal**: Copy/download formatted resume
- **➕ Submit Job Button**: NEW! Manual job submission

---

## 🚀 How to Use Trinity

### Method 1: Submit via Dashboard (Recommended)

1. **Open Dashboard**: http://localhost:8001/dashboard
2. **Click "➕ Submit Job"** button in header
3. **Fill in the form**:
   - Company Name
   - Position Title
   - Paste job description OR job URL
4. **Click "Submit to Trinity"**
5. **Trinity will**:
   - Analyze the job posting
   - Calculate fit score
   - Generate custom cover letter
   - Extract contact information
   - Add to Pending section
6. **Review in Pending section**:
   - Read the cover letter
   - Check contact info
   - Click "✅ Applied" when you send it
   - Or click "❌ Pass" to skip it

### Method 2: API Endpoint (Advanced)

```bash
curl -X POST http://localhost:8001/job/apply \
  -H "Authorization: Bearer ${TRINITY_PASSWORD}" \
  -H "Content-Type: application/json" \
  -d '{
    "job_url_or_text": "Job description here...",
    "company": "Company Name",
    "position": "Position Title"
  }'
```

---

## 📋 Complete Workflow Example

### Step 1: Find Jobs Manually
- Browse Indeed: https://www.indeed.com/
- Browse LinkedIn: https://www.linkedin.com/jobs/
- Check local hotel websites directly
- Search: "front desk", "concierge", "guest services" in Paso Robles, CA

### Step 2: Submit to Trinity
1. Copy job description from Indeed/LinkedIn
2. Open Trinity Dashboard: http://localhost:8001/dashboard
3. Click "➕ Submit Job"
4. Paste description and company info
5. Submit

### Step 3: Review Generated Materials
- Trinity creates custom cover letter in ~30 seconds
- Check the Pending Review section
- Click job card to view full cover letter
- Note the contact information (email/phone)

### Step 4: Send Application
1. Click "📋 Copy Cover Letter"
2. Open your email (or Indeed/LinkedIn application)
3. Paste cover letter
4. Attach resume (copy from Resume modal if needed)
5. Send to contact email shown in Trinity

### Step 5: Track Status
1. Return to Trinity Dashboard
2. Check "✅ Applied" checkbox on the job card
3. Job moves to "Applied" section automatically
4. If no response after 1-2 weeks, check "❌ No Response"

---

## 🔄 Auto-Scanning Status

**Note**: Automated job board scanning is currently disabled due to:
- Indeed blocks automated requests (403 Forbidden)
- LinkedIn requires login for full access
- Safari automation requires admin password
- Chrome browser not installed

**Manual submission via dashboard is more reliable and faster!**

If you want to enable scanning later:
1. Install Chrome browser
2. Run: `safaridriver --enable` (requires admin password)
3. Enable scanner service: `python3 scanner_service.py`

---

## 📊 Statistics

Track your progress:
- Total Applications
- Pending Review count
- Applied count
- Average Fit Score
- Daily application count

View at: http://localhost:8001/job/stats

---

## 🛠️ Server Management

### Start Trinity Server
```bash
source venv/bin/activate
python3 main.py
```

### Check Server Status
```bash
curl http://localhost:8001/health
```

### View Logs
```bash
tail -f trinity.log
```

---

## 💡 Pro Tips

1. **Daily Routine**: Check Indeed/LinkedIn for 10 min each morning, submit 3-5 jobs
2. **Batch Processing**: Submit multiple jobs at once, review all cover letters together
3. **Contact Info**: Trinity extracts email/phone automatically - use it to direct email
4. **Fit Score**: Focus on 80+ score jobs first (green badges)
5. **Follow Up**: Mark as "No Response" after 2 weeks, consider follow-up email
6. **Duplicate Check**: Trinity prevents applying twice to same company/position

---

## 🎯 Target Jobs (Paso Robles, CA)

Trinity is optimized for:
- Front Desk Agent
- Concierge
- Guest Services
- Night Audit
- Hotel Receptionist
- Inn Front Desk

**Salary Target**: $20/hour minimum
**Radius**: 50 miles from Paso Robles, CA

---

## 📧 Contact Information

Email updated to: **tychabot9@gmail.com**
(Previous email suspended due to bot activity)

---

## ⚠️ Important Notes

- Trinity runs with **low CPU priority (nice 10)** to protect trading bot
- Drafts saved locally in `email_drafts/` folder
- Database tracks status in `job_logs/job_status.db`
- All API requests require `TRINITY_PASSWORD` authentication
- Resume data stored in `resume_data.json`

---

**Trinity System Version 1.0**
*Built for Ty Brown - Paso Robles Job Hunt*
