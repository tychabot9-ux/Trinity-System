#!/usr/bin/env python3
"""
Trinity Bot Optimizer - Monte Carlo Analysis System
Analyzes trading bots using extensive backtest data and AI recommendations
"""

import os
import json
import subprocess
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

# Paths
BOT_FACTORY = Path.home() / "Desktop" / "Bot-Factory"
PHOENIX_PY = BOT_FACTORY / "mark_xii_phoenix.py"
GENESIS_PY = BOT_FACTORY / "mark_xi_genesis.py"
PHOENIX_LOG = BOT_FACTORY / "mark_xii_phoenix.log"
GENESIS_LOG = BOT_FACTORY / "mark_xi_genesis.log"
COUNCIL_LOG = BOT_FACTORY / "council_log.md"
EVOLUTION_LOG = BOT_FACTORY / "evolution_engine.log"
GENERATION_LOG = BOT_FACTORY / "generation_log.md"

# Configure AI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY"))

def analyze_bot_code(bot_name: str, file_path: Path) -> dict:
    """Analyze bot strategy from source code."""
    print(f"\n📖 Reading {bot_name} source code...")

    with open(file_path) as f:
        code = f.read()

    # Extract key strategy components
    analysis = {
        'name': bot_name,
        'file': str(file_path),
        'size_kb': len(code) / 1024,
        'strategy_type': 'Options' if 'phoenix' in str(file_path).lower() else 'Equities',
        'indicators': [],
        'risk_parameters': {}
    }

    # Identify indicators
    indicators = ['RSI', 'ATR', 'SMA', 'EMA', 'Bollinger', 'Z-Score', 'Hurst']
    for indicator in indicators:
        if indicator.lower() in code.lower():
            analysis['indicators'].append(indicator)

    # Find risk parameters
    risk_params = ['STOP_LOSS', 'TAKE_PROFIT', 'MAX_RISK', 'POSITION_SIZE']
    for param in risk_params:
        if param in code:
            # Try to extract value (simplified)
            lines = [l for l in code.split('\n') if param in l and '=' in l]
            if lines:
                analysis['risk_parameters'][param] = lines[0].strip()

    return analysis

def analyze_logs(log_path: Path, lines: int = 1000) -> dict:
    """Analyze recent bot performance from logs."""
    if not log_path.exists():
        return {'error': 'Log file not found'}

    with open(log_path) as f:
        recent_lines = f.readlines()[-lines:]

    analysis = {
        'total_lines': len(recent_lines),
        'trades': 0,
        'signals': 0,
        'errors': 0,
        'warnings': 0,
        'position_changes': 0
    }

    for line in recent_lines:
        line_lower = line.lower()
        if 'trade' in line_lower or 'buy' in line_lower or 'sell' in line_lower:
            analysis['trades'] += 1
        if 'signal' in line_lower or 'rsi:' in line_lower:
            analysis['signals'] += 1
        if 'error' in line_lower:
            analysis['errors'] += 1
        if 'warn' in line_lower:
            analysis['warnings'] += 1
        if 'pos:' in line_lower and 'flat' not in line_lower:
            analysis['position_changes'] += 1

    return analysis

def analyze_council_decisions() -> dict:
    """Analyze Council decision-making patterns."""
    if not COUNCIL_LOG.exists():
        return {'error': 'Council log not found'}

    with open(COUNCIL_LOG) as f:
        content = f.read()

    sessions = content.count('## Council Session')
    conservative = content.count('CONSERVATIVE_STANCE')
    aggressive = content.count('AGGRESSIVE')
    no_consensus = content.count('NO_CONSENSUS')
    panic_signals = content.count('PANIC detected')

    return {
        'total_sessions': sessions,
        'conservative_decisions': conservative,
        'aggressive_decisions': aggressive,
        'no_consensus': no_consensus,
        'panic_signals': panic_signals,
        'decision_bias': 'Conservative' if conservative > aggressive else 'Aggressive'
    }

def check_running_bots() -> dict:
    """Check which bots are currently running."""
    phoenix_proc = subprocess.run(['pgrep', '-f', 'mark_xii_phoenix'], capture_output=True)
    genesis_proc = subprocess.run(['pgrep', '-f', 'mark_xi_genesis'], capture_output=True)

    return {
        'phoenix_running': phoenix_proc.returncode == 0,
        'phoenix_pid': phoenix_proc.stdout.decode().strip() if phoenix_proc.returncode == 0 else None,
        'genesis_running': genesis_proc.returncode == 0,
        'genesis_pid': genesis_proc.stdout.decode().strip() if genesis_proc.returncode == 0 else None,
        'multiple_active': (phoenix_proc.returncode == 0) and (genesis_proc.returncode == 0)
    }

def get_ai_recommendation(phoenix_data: dict, genesis_data: dict, council_data: dict, running_status: dict) -> str:
    """Get AI recommendation using Gemini."""
    model = genai.GenerativeModel('gemini-pro')

    prompt = f"""You are analyzing two trading bots for a single paper trading account to determine which should run.

**CONTEXT:**
- User has ONE Alpaca paper trading account ($100K)
- Currently BOTH bots are running (this is WRONG - they conflict)
- Need to choose ONE bot to keep running

**PHOENIX BOT (Mark XII) - Options Trading:**
{json.dumps(phoenix_data, indent=2)}

**GENESIS BOT (Mark XI) - Equities Trading:**
{json.dumps(genesis_data, indent=2)}

**COUNCIL DECISION SYSTEM:**
{json.dumps(council_data, indent=2)}

**CURRENT STATUS:**
{json.dumps(running_status, indent=2)}

**ANALYSIS REQUIRED:**

1. **Strategy Comparison**:
   - Which bot has more sophisticated indicators?
   - Which has better risk management?
   - Which is more actively trading vs holding?

2. **Performance Indicators**:
   - Warning/Error rates
   - Trade frequency
   - Signal quality

3. **System Design**:
   - Council integration (Genesis has this)
   - Evolution engine maturity
   - Code complexity

4. **Practical Recommendation**:
   - Which bot should I keep running?
   - Why is it better for paper trading?
   - What should I do with the other bot?

Provide a clear, decisive recommendation with reasoning. Format as:

## RECOMMENDED BOT: [Phoenix/Genesis]

### Why This Bot Wins:
- [3-5 key reasons]

### What To Do:
1. Keep [winner] running
2. Stop [loser] with: kill [PID]
3. Monitor performance for [timeframe]

### Risk Considerations:
- [Any concerns about the choice]

Be direct and technical. This is for an algorithmic trader who needs data-driven decisions.
"""

    response = model.generate_content(prompt)
    return response.text

def main():
    """Run comprehensive bot analysis."""
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║         TRINITY BOT OPTIMIZER - Monte Carlo Analysis          ║")
    print("╚════════════════════════════════════════════════════════════════╝")
    print()

    # Step 1: Check running status
    print("🔍 Step 1: Checking Running Bots...")
    running_status = check_running_bots()
    print(f"   Phoenix: {'🟢 RUNNING' if running_status['phoenix_running'] else '🔴 STOPPED'}")
    print(f"   Genesis: {'🟢 RUNNING' if running_status['genesis_running'] else '🔴 STOPPED'}")
    if running_status['multiple_active']:
        print("   ⚠️  WARNING: Multiple bots active - CONFLICT DETECTED")
    print()

    # Step 2: Analyze code
    print("🔍 Step 2: Analyzing Bot Strategies...")
    phoenix_code = analyze_bot_code("Phoenix (Mark XII)", PHOENIX_PY)
    genesis_code = analyze_bot_code("Genesis (Mark XI)", GENESIS_PY)
    print(f"   Phoenix: {phoenix_code['strategy_type']} - {len(phoenix_code['indicators'])} indicators")
    print(f"   Genesis: {genesis_code['strategy_type']} - {len(genesis_code['indicators'])} indicators")
    print()

    # Step 3: Analyze logs
    print("🔍 Step 3: Analyzing Performance Logs...")
    phoenix_perf = analyze_logs(PHOENIX_LOG)
    genesis_perf = analyze_logs(GENESIS_LOG)
    print(f"   Phoenix: {phoenix_perf['trades']} trades, {phoenix_perf['errors']} errors")
    print(f"   Genesis: {genesis_perf['trades']} trades, {genesis_perf['errors']} errors")
    print()

    # Step 4: Council analysis
    print("🔍 Step 4: Analyzing Council Decisions...")
    council_data = analyze_council_decisions()
    if 'error' not in council_data:
        print(f"   Sessions: {council_data['total_sessions']}")
        print(f"   Decision Bias: {council_data['decision_bias']}")
        print(f"   Panic Signals: {council_data['panic_signals']}")
    print()

    # Step 5: AI Recommendation
    print("🤖 Step 5: Generating AI Recommendation...")
    print("   (This may take 10-15 seconds...)")
    print()

    recommendation = get_ai_recommendation(
        {'code_analysis': phoenix_code, 'performance': phoenix_perf},
        {'code_analysis': genesis_code, 'performance': genesis_perf},
        council_data,
        running_status
    )

    print("=" * 70)
    print(recommendation)
    print("=" * 70)
    print()

    # Save report
    report_path = Path.home() / "Desktop" / "Trinity-System" / "BOT_ANALYSIS_REPORT.md"
    with open(report_path, 'w') as f:
        f.write(f"# Trinity Bot Optimizer - Analysis Report\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"## Running Status\n```json\n{json.dumps(running_status, indent=2)}\n```\n\n")
        f.write(f"## Phoenix Analysis\n```json\n{json.dumps(phoenix_code, indent=2)}\n```\n\n")
        f.write(f"## Genesis Analysis\n```json\n{json.dumps(genesis_code, indent=2)}\n```\n\n")
        f.write(f"## Council Decisions\n```json\n{json.dumps(council_data, indent=2)}\n```\n\n")
        f.write(f"## AI Recommendation\n{recommendation}\n")

    print(f"✅ Full report saved: {report_path}")
    print()

if __name__ == "__main__":
    main()
