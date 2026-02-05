# Trinity Command Center - Quick Reference Guide

## System Status: ✅ FULLY OPERATIONAL

---

## What Was Fixed (TL;DR)

1. **Database paths** - Job tracking now works
2. **Auto-initialization** - Databases create themselves
3. **Error handling** - No more crashes, only error messages
4. **API updates** - Using latest Gemini models
5. **Security** - Input sanitization added
6. **Performance** - Memory queries optimized

**Result:** System is robust, user-friendly, and production-ready.

---

## Quick Start

```bash
# 1. Ensure dependencies installed
pip install streamlit google-generativeai requests psutil python-dotenv pillow

# 2. Set environment variables in .env
GOOGLE_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here

# 3. Run the application
streamlit run command_center.py --server.port 8001

# 4. Access the interface
# Desktop: http://localhost:8001
# Mobile:  http://[YOUR-IP]:8001
# VR:      http://[YOUR-IP]:8001?vr=true
```

---

## File Structure

```
Trinity-System/
├── command_center.py          # Main application (FIXED ✅)
├── trinity_memory.py          # Memory system (OPTIMIZED ✅)
├── job_logs/
│   └── job_status.db         # Job tracking database (AUTO-CREATED)
├── data/
│   └── trinity_memory.db     # Trinity Memory database (AUTO-CREATED)
├── email_drafts/             # Cover letter drafts
├── cad_output/               # CAD models and previews
└── Bot-Factory/              # (Optional) Trading bot directory
```

---

## What Works Now

### ✅ Career Station
- Job URL submission
- Fit score analysis
- Application tracking
- Draft cover letters
- Statistics dashboard

### ✅ Engineering Station
- AI-powered CAD generation
- OpenSCAD code creation
- STL file compilation
- VR-optimized models
- Model history

### ✅ Memory Dashboard
- User profile management
- Preference learning
- Decision tracking
- Insights discovery
- Knowledge base

### ✅ AI Assistant
- Chat with Trinity
- File uploads (images, code, docs)
- Context-aware responses
- Memory integration
- Multi-turn conversations

### ✅ Trading Station
- Phoenix bot monitoring
- Live trading status
- Performance metrics
- Log viewing
- Macro status

---

## Error Handling

All functions now have proper error handling:

- **File operations** - Graceful errors on permission/encoding issues
- **Database operations** - Auto-initialization, clear error messages
- **API calls** - Timeout protection, user-friendly errors
- **Subprocess calls** - 5-second timeouts, no hangs
- **Bot-Factory** - Graceful degradation if directory missing

---

## Environment Variables

Required in `.env`:

```bash
# Required for AI features
GOOGLE_API_KEY=your_gemini_api_key_here

# Optional (for Claude features)
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Optional (defaults shown)
TRINITY_API_BASE=http://localhost:8001
```

---

## Database Schema

### Job Status Database
Auto-created at: `job_logs/job_status.db`

Tables:
- `job_statuses` - All job applications with status tracking

### Trinity Memory Database
Auto-created at: `data/trinity_memory.db`

Tables:
- `user_profile` - User profile data
- `preferences` - Learned preferences
- `decisions` - Decision history
- `interactions` - All user interactions
- `context_snapshots` - Saved contexts
- `insights` - Discovered patterns
- `knowledge` - Semantic knowledge base

---

## Common Operations

### Add a Job
1. Go to Career Station
2. Paste job URL
3. Click "Analyze Job"
4. Review fit score and draft

### Generate CAD Model
1. Go to Engineering Station
2. Describe what you want
3. Click "Generate Model"
4. Download STL file

### Chat with Trinity
1. Go to AI Assistant
2. Upload files if needed
3. Type your message
4. Get AI-powered response

### View Memory
1. Go to Memory Dashboard
2. Browse tabs (Profile, Preferences, Decisions, etc.)
3. Export data if needed

### Monitor Trading Bot
1. Go to Trading Station
2. View Phoenix status
3. Check live metrics
4. View trading log

---

## Troubleshooting

### "API Key not configured"
- Check `.env` file exists
- Verify `GOOGLE_API_KEY` is set
- Restart application

### "Database error"
- Check permissions on `job_logs/` and `data/` directories
- Delete and recreate databases (will auto-initialize)

### "Bot-Factory not found"
- This is optional - Trading Station will show error
- Create Bot-Factory directory or ignore

### "OpenSCAD not installed"
- Run: `brew install --cask openscad` (macOS)
- Or download from openscad.org

### Application won't start
- Check Python version (3.9+)
- Verify all dependencies installed
- Check port 8001 not already in use

---

## Performance Tips

1. **First run** - Databases initialize automatically (1-2 seconds)
2. **AI responses** - Typical 2-5 seconds depending on query
3. **CAD compilation** - 5-30 seconds depending on complexity
4. **VR mode** - Uses simplified models for better performance

---

## Security Notes

- API keys stored in `.env` (not in git)
- File uploads limited to 10MB
- Input sanitized for path traversal
- Subprocess calls have 5-second timeout
- No executable files allowed in uploads

---

## What's New in This Version

- ✅ Fixed all critical bugs
- ✅ Added comprehensive error handling
- ✅ Updated to latest Gemini API
- ✅ Optimized database queries
- ✅ Added input sanitization
- ✅ Auto-database initialization
- ✅ Graceful error degradation
- ✅ Better error messages

---

## Support

For detailed debugging information, see:
- `DEBUGGING_REPORT.md` - Full analysis and recommendations
- `FIXES_SUMMARY.md` - Quick summary of changes

System validated and ready for production use! 🚀

---

**Last Updated:** February 4, 2026
**Status:** ✅ All Systems Operational
**Version:** Trinity Command Center v1.0
