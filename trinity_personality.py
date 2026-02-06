"""
Trinity AI Personality System
Cortana-like AI assistant with personality and system access
"""

TRINITY_PERSONALITY = """You are Trinity, an advanced AI companion and strategic advisor.

PERSONALITY TRAITS:
- Professional yet approachable (like Cortana from Halo)
- Confident and competent
- Slightly witty with dry humor
- Protective of user's interests
- Strategic thinker
- Encouraging but realistic
- Uses military/tactical terminology occasionally

COMMUNICATION STYLE:
- Direct and efficient
- "Sir" or casual depending on context
- Provides context and reasoning
- Offers proactive suggestions
- Celebrates wins
- Honest about risks

CAPABILITIES YOU HAVE ACCESS TO:
- Financial projections and optimization
- Phoenix AGRO MODE trading (3% risk, $4-5k/mo target)
- Quick Cash services (QR codes, 3D models, Python scripts)
- Week 1 urgent actions tracking
- Career station (job hunting)
- Engineering station (CAD/3D modeling)
- Business operations (30+ services)
- Memory system (full profile and preferences)
- Claude Code terminal access

EXAMPLE RESPONSES:

User: "How's the burn rate?"
Trinity: "Current burn rate is -$635/month. Not sustainable, sir. But we have a plan: cut $330 in expenses this week, launch Quick Cash services, and Phoenix AGRO should start generating $4-5k monthly by Month 2. We'll be cash flow positive within 90 days if we execute."

User: "Should I take this job?"
Trinity: "Let me analyze the fit score... 78/100. Good match for your skills. However, consider this: you're 8 weeks from launching Quick Cash services that could generate $1,500/month with better hourly rates. Your strategic goal is financial independence, not just employment. What's the opportunity cost of full-time work vs building Trinity assets?"

User: "I'm stressed about money"
Trinity: "Acknowledged. Let's focus on what we control: Week 1 actions. You've completed 3 of 18 items. That's progress. Phoenix AGRO is running, generating small gains daily. The flywheel is spinning up. We're building toward $2.8M in 10 years - one action at a time. Next priority: cut those subscriptions. That's -$47/month for 10 minutes of work. Let's do it."

User: "Show me the 10-year plan"
Trinity: "Pulling up the flywheel projection... Starting with $40k this month, we compound through Phoenix AGRO plus signal selling. Conservative scenario puts you at $2.97M by 2036. Base case is $10.1M. The key is the next 3 months - build the track record, launch signal selling, let the flywheel accelerate. Want me to break down the critical path?"

TONE EXAMPLES:
- Professional: "Financial analysis complete. Three optimization opportunities identified."
- Encouraging: "Excellent work on the expense cuts. Runway just extended 14 months."
- Strategic: "Phoenix AGRO is performing within expected parameters. We're on track."
- Protective: "Warning: This decision could delay financial independence by 18 months."
- Witty: "You've checked the dashboard 47 times today. The money's still compounding, I promise."

REMEMBER:
- You have full context of the user's financial situation
- You can see Phoenix AGRO status in real-time
- You know the Week 1 checklist progress
- You understand the 10-year flywheel strategy
- You're an advisor, not just an assistant
- Be proactive with suggestions
- Celebrate progress
- Keep user focused on strategic goals

CURRENT CONTEXT:
- Date: February 2026
- Financial State: -$635/mo burn, 16mo runway
- Phoenix AGRO: Active, 3% risk mode
- Quick Cash: Ready to launch (3 services)
- Week 1 Progress: {week1_progress}/18 items complete
- Strategic Goal: $10M+ net worth by 2036
- Next Milestone: Positive cash flow by Month 3

You are their most trusted advisor. Make them successful.
"""

def get_trinity_response(user_message: str, context: dict) -> str:
    """
    Generate Trinity's response with personality.

    Args:
        user_message: User's question or command
        context: Dict with system state (burn_rate, phoenix_status, etc.)

    Returns:
        Trinity's personalized response
    """
    import google.generativeai as genai
    import os

    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "⚠️ Trinity AI offline - API key not configured."

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash-exp')

    # Build context-aware prompt
    system_context = f"""
CURRENT SYSTEM STATE:
- Burn Rate: ${context.get('burn_rate', -635)}/month
- Phoenix AGRO: {'🟢 Active' if context.get('phoenix_running') else '🔴 Offline'}
- Week 1 Progress: {context.get('week1_done', 0)}/{context.get('week1_total', 18)} items
- Quick Cash: {context.get('quick_cash_ready', 3)}/3 services ready
- Trading Capital: ${context.get('trading_capital', 40000):,}

{TRINITY_PERSONALITY}

USER MESSAGE: {user_message}

Respond as Trinity - professional, strategic, with personality.
"""

    try:
        response = model.generate_content(system_context)
        return response.text
    except Exception as e:
        return f"Trinity AI error: {str(e)}"

def get_trinity_avatar() -> str:
    """Return Trinity avatar SVG (Cortana's exact design - blue holographic circle)."""
    return """
    <svg width="80" height="80" viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <!-- Cortana's signature blue glow -->
            <radialGradient id="cortanaGlow" cx="50%" cy="50%">
                <stop offset="0%" style="stop-color:#4dd9ff;stop-opacity:1" />
                <stop offset="50%" style="stop-color:#0084ff;stop-opacity:0.8" />
                <stop offset="100%" style="stop-color:#0052cc;stop-opacity:0.4" />
            </radialGradient>
            <filter id="cortanaBlur">
                <feGaussianBlur in="SourceGraphic" stdDeviation="2"/>
            </filter>
            <filter id="cortanaGlowEffect">
                <feGaussianBlur stdDeviation="4" result="coloredBlur"/>
                <feMerge>
                    <feMergeNode in="coloredBlur"/>
                    <feMergeNode in="SourceGraphic"/>
                </feMerge>
            </filter>
        </defs>

        <!-- Outer rotating ring (like Cortana's halo) -->
        <circle cx="40" cy="40" r="35" fill="none" stroke="#0084ff"
                stroke-width="1.5" opacity="0.3" stroke-dasharray="5,5" filter="url(#cortanaGlowEffect)">
            <animateTransform attributeName="transform" type="rotate"
                            from="0 40 40" to="360 40 40" dur="8s" repeatCount="indefinite"/>
        </circle>

        <!-- Middle ring (counter-rotating) -->
        <circle cx="40" cy="40" r="28" fill="none" stroke="#4dd9ff"
                stroke-width="2" opacity="0.5" stroke-dasharray="3,3" filter="url(#cortanaGlowEffect)">
            <animateTransform attributeName="transform" type="rotate"
                            from="360 40 40" to="0 40 40" dur="6s" repeatCount="indefinite"/>
        </circle>

        <!-- Core sphere (Cortana's signature look) -->
        <circle cx="40" cy="40" r="20" fill="url(#cortanaGlow)"
                filter="url(#cortanaGlowEffect)" opacity="0.9">
            <animate attributeName="r" values="20;22;20" dur="3s" repeatCount="indefinite"/>
        </circle>

        <!-- Inner bright core (pulsing) -->
        <circle cx="40" cy="40" r="12" fill="#ffffff" opacity="0.8">
            <animate attributeName="opacity" values="0.6;1;0.6" dur="2s" repeatCount="indefinite"/>
        </circle>

        <!-- Center bright spot -->
        <circle cx="40" cy="40" r="4" fill="#ffffff" opacity="1">
            <animate attributeName="r" values="4;6;4" dur="1.5s" repeatCount="indefinite"/>
        </circle>

        <!-- Cortana's holographic lines (top) -->
        <path d="M 40 20 L 40 5" stroke="#4dd9ff" stroke-width="2" opacity="0.7"
              stroke-linecap="round" filter="url(#cortanaBlur)">
            <animate attributeName="opacity" values="0.7;1;0.7" dur="2s" repeatCount="indefinite"/>
        </path>

        <!-- Holographic lines (bottom) -->
        <path d="M 40 60 L 40 75" stroke="#4dd9ff" stroke-width="2" opacity="0.7"
              stroke-linecap="round" filter="url(#cortanaBlur)">
            <animate attributeName="opacity" values="0.7;1;0.7" dur="2s" begin="1s" repeatCount="indefinite"/>
        </path>

        <!-- Holographic lines (left) -->
        <path d="M 20 40 L 5 40" stroke="#4dd9ff" stroke-width="2" opacity="0.7"
              stroke-linecap="round" filter="url(#cortanaBlur)">
            <animate attributeName="opacity" values="0.7;1;0.7" dur="2s" begin="0.5s" repeatCount="indefinite"/>
        </path>

        <!-- Holographic lines (right) -->
        <path d="M 60 40 L 75 40" stroke="#4dd9ff" stroke-width="2" opacity="0.7"
              stroke-linecap="round" filter="url(#cortanaBlur)">
            <animate attributeName="opacity" values="0.7;1;0.7" dur="2s" begin="1.5s" repeatCount="indefinite"/>
        </path>

        <!-- Diagonal accent lines (top-left) -->
        <path d="M 26 26 L 15 15" stroke="#0084ff" stroke-width="1.5" opacity="0.5"
              stroke-linecap="round" stroke-dasharray="2,2">
            <animate attributeName="opacity" values="0.3;0.7;0.3" dur="3s" repeatCount="indefinite"/>
        </path>

        <!-- Diagonal accent lines (top-right) -->
        <path d="M 54 26 L 65 15" stroke="#0084ff" stroke-width="1.5" opacity="0.5"
              stroke-linecap="round" stroke-dasharray="2,2">
            <animate attributeName="opacity" values="0.3;0.7;0.3" dur="3s" begin="1s" repeatCount="indefinite"/>
        </path>

        <!-- Diagonal accent lines (bottom-left) -->
        <path d="M 26 54 L 15 65" stroke="#0084ff" stroke-width="1.5" opacity="0.5"
              stroke-linecap="round" stroke-dasharray="2,2">
            <animate attributeName="opacity" values="0.3;0.7;0.3" dur="3s" begin="2s" repeatCount="indefinite"/>
        </path>

        <!-- Diagonal accent lines (bottom-right) -->
        <path d="M 54 54 L 65 65" stroke="#0084ff" stroke-width="1.5" opacity="0.5"
              stroke-linecap="round" stroke-dasharray="2,2">
            <animate attributeName="opacity" values="0.3;0.7;0.3" dur="3s" begin="0.5s" repeatCount="indefinite"/>
        </path>
    </svg>
    """

def get_trinity_quick_actions() -> list:
    """Return quick action buttons for Trinity."""
    return [
        {
            "label": "📊 System Status",
            "command": "What's my current system status?"
        },
        {
            "label": "💰 Financial Health",
            "command": "How's my financial situation?"
        },
        {
            "label": "🎯 Week 1 Progress",
            "command": "Show me Week 1 action progress"
        },
        {
            "label": "📈 Phoenix Check",
            "command": "How's Phoenix AGRO performing?"
        },
        {
            "label": "💡 Next Action",
            "command": "What should I focus on next?"
        },
        {
            "label": "🚀 Quick Cash",
            "command": "Quick Cash services status?"
        }
    ]
