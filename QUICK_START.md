# ⚡ Trinity System - Quick Start Guide

**You're 5 minutes from launching your autonomous job hunting system.**

---

## 🎯 What You Have

✅ **FULL-AUTO Job Sniper** with 7-layer safety system
✅ **10 applications/day** limit (3/hour rate limiting)
✅ **80+ fit score** requirement (strict quality control)
✅ **Kill switch** for emergency shutdown
✅ **Live monitoring** dashboard
✅ **100% test pass rate** (8/8 safety tests)

---

## 🚀 Start in 3 Steps

### Step 1: Start Trinity Server (1 minute)
```bash
cd ~/Desktop/Trinity-System
./start_trinity.sh
```

Server runs on: `http://localhost:8001`

### Step 2: Open Monitor (1 minute)
Open a **second terminal window**:
```bash
cd ~/Desktop/Trinity-System
source venv/bin/activate
python3 monitor.py
```

### Step 3: Test with Real Job (3 minutes)
1. Find a job posting you like
2. Copy the URL or full job description text
3. Use API to submit:

```bash
curl -X POST http://localhost:8001/job/apply \
  -H "Authorization: Bearer pineapple9devices" \
  -H "Content-Type: application/json" \
  -d '{
    "job_url_or_text":"[paste job posting here]",
    "company":"Company Name",
    "position":"Position Title"
  }'
```

4. Check your Gmail sent folder
5. Verify application looks professional
6. Check monitor dashboard

---

## 🛡️ Safety Features (Always Active)

| Feature | Threshold | What It Does |
|---------|-----------|--------------|
| **Fit Score** | 80/100 | Blocks weak matches |
| **Keywords** | Required | Must mention hospitality/hotel |
| **Night Shifts** | Blocked | Auto-rejects graveyard/overnight |
| **Rate Limit** | 3/hour, 10/day | Prevents spam |
| **Duplicates** | 90 days | Can't reapply to same company |
| **Scams** | Auto-detect | Blocks MLM/suspicious patterns |
| **Kill Switch** | Manual | Emergency stop button |

---

## 📊 Monitor Commands

While in monitor (press keys):
- **K** - Toggle Kill Switch (EMERGENCY STOP)
- **R** - Refresh display
- **L** - View full application log
- **B** - View blacklisted companies
- **Q** - Quit monitor

---

## 🚨 Emergency: How to Stop Everything

### Method 1: Kill Switch (Recommended)
1. Open monitor (`python3 monitor.py`)
2. Press `K`
3. Confirm with Pushover notification

### Method 2: Stop Server
```bash
# Find Trinity process
ps aux | grep "python3 main.py"

# Kill it
kill [PID]
```

### Method 3: Create Kill Switch File
```bash
touch ~/Desktop/Trinity-System/job_logs/KILL_SWITCH
```

---

## ✅ First Application Checklist

After your first test application:

**Check Gmail:**
- [ ] Email sent to correct company
- [ ] Subject line professional
- [ ] Cover letter looks good
- [ ] No typos or formatting errors
- [ ] Your contact info correct

**Check Monitor:**
- [ ] Application logged in database
- [ ] Fit score matches expectation
- [ ] Rate limit incremented (1/10 today)

**Check Pushover:**
- [ ] Notification received (optional)

**If ALL checkboxes pass:** System is working correctly!

**If ANY fail:** Activate kill switch and troubleshoot

---

## 📈 What to Expect

### First Hour:
- Submit 1-3 test applications manually via API
- Verify each one in Gmail
- Get comfortable with monitor

### First Day:
- Monitor closely (check every 2 hours)
- Expect 3-6 applications if jobs available
- All should be quality matches

### First Week:
- 20-40 applications total
- Response rate: 5-15% typical
- Interview requests: 1-3 expected

### Red Flags (Activate Kill Switch If):
- Application to night shift job
- Application outside your area
- Application to obvious scam
- Fit score below 80
- More than 3 apps in one hour

---

## 🔧 Quick Troubleshooting

**Problem:** Server won't start
```bash
# Check if port 8001 in use
lsof -i :8001

# Kill conflicting process
kill [PID]
```

**Problem:** Tests failing
```bash
cd ~/Desktop/Trinity-System
source venv/bin/activate
python3 test_suite.py

# All must pass before going live
```

**Problem:** Gmail not sending
```bash
# Verify .env credentials
cat .env | grep EMAIL

# Test Gmail connection manually
```

---

## 📞 Key Files

```
Trinity-System/
├── start_trinity.sh       ← Start server
├── monitor.py             ← Dashboard
├── test_suite.py          ← Safety tests
├── FULL_AUTO_GUIDE.md     ← Complete docs
├── .env                   ← Credentials
└── job_logs/
    ├── applications.db    ← All applications
    ├── rate_limits.json   ← Rate tracking
    ├── blacklist.json     ← Blocked companies
    └── KILL_SWITCH        ← Emergency stop
```

---

## 🎯 Success Metrics

**After 1 week, you should see:**
- 10-30 applications sent
- Zero false positives (wrong jobs)
- 85+ average fit score
- 1-5 company responses
- Zero spam complaints

**If metrics are off, adjust settings in .env**

---

## ⚠️ Remember

1. **You're in control** - Kill switch always available
2. **First week is testing** - Monitor closely
3. **AI makes mistakes** - Check your emails
4. **Quality > Quantity** - 10 good apps > 50 bad ones
5. **Bot-Factory is safe** - Trinity runs low priority

---

## 🚀 Ready to Launch?

Run these three commands in order:

**Terminal 1:**
```bash
cd ~/Desktop/Trinity-System
./start_trinity.sh
```

**Terminal 2:**
```bash
cd ~/Desktop/Trinity-System
source venv/bin/activate
python3 monitor.py
```

**Then:** Submit your first test job via API or web interface

---

**Questions? Check FULL_AUTO_GUIDE.md for complete documentation.**

**Good hunting! 🎯**
