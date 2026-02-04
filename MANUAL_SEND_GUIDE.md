# Manual Email Workflow (No Gmail SMTP Needed!)

Trinity creates perfect drafts. You review and send manually. Simple and safe.

## How It Works:

1. **Trinity creates draft** → Saved in `email_drafts/`
2. **You review draft** → Check it looks good
3. **Copy to Gmail** → Paste into Gmail compose
4. **Send manually** → Click send in Gmail web

## Step-by-Step:

### When Trinity Creates a Draft:

```bash
cd ~/Desktop/Trinity-System/email_drafts
ls -lt | head -5  # See latest drafts
```

### To Send a Draft:

1. **Open the draft file:**
   ```bash
   open email_drafts/[latest-draft].txt
   # or
   cat email_drafts/[latest-draft].txt
   ```

2. **Copy the email body** (everything between the lines)

3. **Go to Gmail:** https://mail.google.com/mail/?view=cm&fs=1&tf=1

4. **Paste and send:**
   - To: (get from job posting)
   - Subject: Application for [Position]
   - Body: (paste the cover letter)
   - Click Send

## Quick Commands:

```bash
# See latest draft
cat email_drafts/*.txt | tail -50

# Count drafts today
ls -l email_drafts/ | wc -l

# Open drafts folder
open email_drafts/
```

## Benefits:

✅ No Gmail authentication issues
✅ You review every email before sending
✅ Full control over when/what gets sent
✅ Trinity still does 95% of the work
✅ No risk of account suspension
