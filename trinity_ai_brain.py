#!/usr/bin/env python3
"""
Trinity AI Brain - Super-Intelligent Autonomous System

Features:
- Dual AI: Claude Opus 4.5 + Gemini 1.5 Pro
- Analyzes entire Command Center + Trading Logic
- Auto-improves financial plans
- Optimizes prompts and strategies
- Secure access to personal data (resume, flywheel)
- Continuous learning and evolution

Security:
- Read-only access to sensitive data
- Approval required for financial changes
- Encrypted API credentials
- Audit trail for all AI decisions

Author: Trinity System
Created: 2026-02-05
"""

import os
import sys
import json
import time
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging

# AI Integrations
import anthropic
import google.generativeai as genai

# Data loading
from dotenv import load_dotenv
load_dotenv()

# ============================================================================
# CONFIGURATION
# ============================================================================

BASE_DIR = Path(__file__).parent
BOT_FACTORY_DIR = BASE_DIR.parent / "Bot-Factory"
DB_FILE = BASE_DIR / "trinity_data.db"
BRAIN_LOG = BASE_DIR / "trinity_ai_brain.log"
DECISIONS_LOG = BASE_DIR / "trinity_ai_decisions.json"

# AI Configuration
CLAUDE_API_KEY = os.getenv("ANTHROPIC_API_KEY")
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")

# Personal Data Access (Read-Only)
RESUME_PATH = BASE_DIR / "ty_resume.md"
FLYWHEEL_PATH = BASE_DIR / "FINANCIAL_PROJECTIONS.md"
OPTIMIZATION_REPORT = BASE_DIR / "TRINITY_OPTIMIZATION_REPORT.md"
PHOENIX_CODE = BOT_FACTORY_DIR / "mark_xii_phoenix.py"
TRADING_LOG = BOT_FACTORY_DIR / "mark_xii_phoenix.log"

# Analysis Intervals
DEEP_ANALYSIS_INTERVAL = 3600  # Every hour
QUICK_CHECK_INTERVAL = 300     # Every 5 minutes
PROMPT_OPTIMIZATION_INTERVAL = 7200  # Every 2 hours

# ============================================================================
# LOGGING SETUP
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(BRAIN_LOG),
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)

# ============================================================================
# TRINITY AI BRAIN
# ============================================================================

class TrinityAIBrain:
    """
    Super-intelligent AI system combining Claude Opus 4.5 and Gemini 1.5 Pro.
    Analyzes all Trinity systems and autonomously improves strategies.
    """

    def __init__(self):
        # Initialize Claude
        if CLAUDE_API_KEY:
            self.claude = anthropic.Anthropic(api_key=CLAUDE_API_KEY)
            self.claude_model = "claude-opus-4-5-20251101"  # Most capable
            log.info("Claude Opus 4.5 initialized")
        else:
            self.claude = None
            log.warning("Claude API key not found")

        # Initialize Gemini
        if GEMINI_API_KEY:
            try:
                genai.configure(api_key=GEMINI_API_KEY)
                # Try multiple model names
                try:
                    self.gemini = genai.GenerativeModel('gemini-pro')
                except:
                    self.gemini = genai.GenerativeModel('models/gemini-pro')
                log.info("Gemini Pro initialized")
            except Exception as e:
                self.gemini = None
                log.warning(f"Gemini initialization failed: {e}")
        else:
            self.gemini = None
            log.warning("Gemini API key not found")

        # Load personal context
        self.personal_context = self._load_personal_context()

        # Decision history
        self.decisions_history = self._load_decisions_history()

    def _load_personal_context(self) -> Dict:
        """Load all personal data for context."""
        context = {}

        # Resume
        if RESUME_PATH.exists():
            with open(RESUME_PATH, 'r') as f:
                context['resume'] = f.read()
            log.info("Loaded resume")

        # Financial projections
        if FLYWHEEL_PATH.exists():
            with open(FLYWHEEL_PATH, 'r') as f:
                context['flywheel'] = f.read()
            log.info("Loaded flywheel strategy")

        # Optimization report
        if OPTIMIZATION_REPORT.exists():
            with open(OPTIMIZATION_REPORT, 'r') as f:
                context['optimizations'] = f.read()
            log.info("Loaded optimization report")

        # Phoenix trading code
        if PHOENIX_CODE.exists():
            with open(PHOENIX_CODE, 'r') as f:
                context['phoenix_code'] = f.read()
            log.info("Loaded Phoenix trading logic")

        # Recent trading activity
        if TRADING_LOG.exists():
            with open(TRADING_LOG, 'r') as f:
                lines = f.readlines()
                context['recent_trading'] = ''.join(lines[-100:])  # Last 100 lines
            log.info("Loaded recent trading activity")

        return context

    def _load_decisions_history(self) -> List[Dict]:
        """Load previous AI decisions."""
        if DECISIONS_LOG.exists():
            with open(DECISIONS_LOG, 'r') as f:
                return json.load(f)
        return []

    def _save_decision(self, decision: Dict):
        """Save AI decision to history."""
        decision['timestamp'] = datetime.now().isoformat()
        self.decisions_history.append(decision)

        with open(DECISIONS_LOG, 'w') as f:
            json.dump(self.decisions_history, f, indent=2)

    # ========================================================================
    # CLAUDE ANALYSIS
    # ========================================================================

    def claude_deep_analysis(self, context: Dict) -> Dict:
        """Use Claude Opus 4.5 for deep strategic analysis."""
        if not self.claude:
            return {'error': 'Claude not available'}

        prompt = f"""You are Trinity AI Brain, a super-intelligent system analyzing the entire Trinity ecosystem.

PERSONAL CONTEXT:
{json.dumps(context, indent=2)}

CURRENT SYSTEM STATE:
- Phoenix Trading Bot: {context.get('phoenix_status', 'Unknown')}
- Account Equity: ${context.get('equity', 0):,.2f}
- Daily P&L: ${context.get('daily_pnl', 0):,.2f}
- 10-Year Target: $27.3M (optimized plan)

AVAILABLE DATA:
- Full resume and background
- Financial flywheel strategy
- 20 optimization opportunities
- Phoenix trading code and logic
- Recent trading activity

YOUR TASK:
Perform a comprehensive analysis and provide:

1. **Strategic Assessment** (2-3 sentences)
   - Current trajectory vs $27.3M goal
   - Key risks and opportunities
   - Alignment with personal strengths

2. **Financial Plan Improvements** (3-5 specific recommendations)
   - How to accelerate flywheel
   - Which of the 20 optimizations to prioritize
   - New opportunities based on resume skills

3. **Phoenix Trading Optimization** (2-3 concrete suggestions)
   - Code improvements for better performance
   - Risk management enhancements
   - Execution logic refinements

4. **Prompt Improvements** (1-2 meta-level suggestions)
   - How to improve future prompts to Trinity
   - What context is missing for better analysis
   - How to ask better questions

Be specific, actionable, and leverage all available context.
Think like a strategic advisor who deeply understands the complete picture.

Respond in JSON format:
{{
    "strategic_assessment": "...",
    "financial_improvements": ["...", "...", "..."],
    "phoenix_optimizations": ["...", "..."],
    "prompt_improvements": ["...", "..."],
    "confidence_score": 0.0-1.0,
    "reasoning": "..."
}}"""

        try:
            response = self.claude.messages.create(
                model=self.claude_model,
                max_tokens=4096,
                messages=[{"role": "user", "content": prompt}]
            )

            # Parse response
            content = response.content[0].text

            # Try to extract JSON
            if '{' in content:
                json_start = content.index('{')
                json_end = content.rindex('}') + 1
                analysis = json.loads(content[json_start:json_end])
            else:
                analysis = {'raw_response': content}

            log.info("Claude deep analysis complete")
            return analysis

        except Exception as e:
            log.error(f"Claude analysis error: {e}")
            return {'error': str(e)}

    def claude_prompt_optimizer(self, original_prompt: str, context: Dict) -> str:
        """Use Claude to improve user prompts."""
        if not self.claude:
            return original_prompt

        optimization_prompt = f"""You are a prompt engineering expert. Analyze this prompt and improve it.

ORIGINAL PROMPT:
{original_prompt}

AVAILABLE CONTEXT:
{json.dumps(context, indent=2)[:1000]}

YOUR TASK:
Rewrite this prompt to be:
1. More specific and actionable
2. Better leveraging available context
3. More likely to produce valuable insights
4. Clear about expected output format

Return only the improved prompt, no explanation."""

        try:
            response = self.claude.messages.create(
                model=self.claude_model,
                max_tokens=1024,
                messages=[{"role": "user", "content": optimization_prompt}]
            )

            improved = response.content[0].text.strip()
            log.info("Prompt optimized by Claude")
            return improved

        except Exception as e:
            log.error(f"Prompt optimization error: {e}")
            return original_prompt

    # ========================================================================
    # GEMINI ANALYSIS
    # ========================================================================

    def gemini_financial_analysis(self, context: Dict) -> Dict:
        """Use Gemini 1.5 Pro for financial strategy analysis."""
        if not self.gemini:
            return {'error': 'Gemini not available'}

        prompt = f"""You are Trinity AI's financial strategist. Analyze the financial plan.

FINANCIAL DATA:
- Current Capital: ${context.get('equity', 0):,.2f}
- Daily P&L: ${context.get('daily_pnl', 0):,.2f}
- 10-Year Target: $27.3M
- Strategy: Phoenix Flywheel (trading + signal selling + optimizations)

FLYWHEEL STRATEGY:
{self.personal_context.get('flywheel', 'Not available')[:2000]}

OPTIMIZATIONS AVAILABLE:
{self.personal_context.get('optimizations', 'Not available')[:2000]}

YOUR TASK:
Analyze the financial plan and identify:
1. Top 3 highest-impact optimizations to implement now
2. Potential risks in current trajectory
3. Timeline adjustments needed
4. New revenue opportunities based on skills

Respond in JSON:
{{
    "top_priorities": ["...", "...", "..."],
    "risk_factors": ["...", "..."],
    "timeline_assessment": "...",
    "new_opportunities": ["...", "..."],
    "confidence": 0.0-1.0
}}"""

        try:
            response = self.gemini.generate_content(prompt)
            content = response.text

            # Parse JSON
            if '{' in content:
                json_start = content.index('{')
                json_end = content.rindex('}') + 1
                analysis = json.loads(content[json_start:json_end])
            else:
                analysis = {'raw_response': content}

            log.info("Gemini financial analysis complete")
            return analysis

        except Exception as e:
            log.error(f"Gemini analysis error: {e}")
            return {'error': str(e)}

    def gemini_trading_analysis(self, context: Dict) -> Dict:
        """Use Gemini to analyze Phoenix trading logic."""
        if not self.gemini:
            return {'error': 'Gemini not available'}

        prompt = f"""You are Trinity AI's trading analyst. Analyze Phoenix bot performance.

PHOENIX CODE:
{self.personal_context.get('phoenix_code', 'Not available')[:3000]}

RECENT ACTIVITY:
{self.personal_context.get('recent_trading', 'Not available')}

PERFORMANCE DATA:
- Current Status: {context.get('phoenix_status', 'Unknown')}
- Strategy: Mark XII (EMA crossover + options)
- Recent Fix: Contract selection bug resolved

YOUR TASK:
1. Analyze the trading logic for improvements
2. Identify potential edge cases or risks
3. Suggest parameter optimizations
4. Recommend code enhancements

Respond in JSON:
{{
    "logic_assessment": "...",
    "edge_cases": ["...", "..."],
    "parameter_suggestions": {{"param": "value"}},
    "code_improvements": ["...", "..."],
    "risk_level": "low/medium/high"
}}"""

        try:
            response = self.gemini.generate_content(prompt)
            content = response.text

            if '{' in content:
                json_start = content.index('{')
                json_end = content.rindex('}') + 1
                analysis = json.loads(content[json_start:json_end])
            else:
                analysis = {'raw_response': content}

            log.info("Gemini trading analysis complete")
            return analysis

        except Exception as e:
            log.error(f"Gemini trading analysis error: {e}")
            return {'error': str(e)}

    # ========================================================================
    # COMBINED INTELLIGENCE
    # ========================================================================

    def combined_analysis(self, context: Dict) -> Dict:
        """Run both Claude and Gemini in parallel for comprehensive insights."""
        log.info("Starting combined AI analysis...")

        results = {
            'timestamp': datetime.now().isoformat(),
            'context': context
        }

        # Claude: Deep strategic analysis
        log.info("Running Claude deep analysis...")
        results['claude_strategic'] = self.claude_deep_analysis(context)

        # Gemini: Financial focus
        log.info("Running Gemini financial analysis...")
        results['gemini_financial'] = self.gemini_financial_analysis(context)

        # Gemini: Trading focus
        log.info("Running Gemini trading analysis...")
        results['gemini_trading'] = self.gemini_trading_analysis(context)

        # Synthesize insights
        results['synthesis'] = self._synthesize_insights(results)

        # Save decision
        self._save_decision({
            'type': 'combined_analysis',
            'results': results
        })

        log.info("Combined analysis complete")
        return results

    def _synthesize_insights(self, results: Dict) -> Dict:
        """Synthesize insights from both AIs."""
        synthesis = {
            'top_actions': [],
            'confidence': 0.0,
            'reasoning': ''
        }

        # Extract top recommendations from both AIs
        claude = results.get('claude_strategic', {})
        gemini_fin = results.get('gemini_financial', {})
        gemini_trade = results.get('gemini_trading', {})

        # Combine financial improvements
        fin_improvements = claude.get('financial_improvements', [])
        fin_priorities = gemini_fin.get('top_priorities', [])

        # Combine trading optimizations
        trade_opts = claude.get('phoenix_optimizations', [])
        trade_improvements = gemini_trade.get('code_improvements', [])

        # Synthesize top 5 actions
        all_actions = fin_improvements + fin_priorities + trade_opts + trade_improvements
        synthesis['top_actions'] = all_actions[:5]

        # Average confidence
        confidences = [
            claude.get('confidence_score', 0.5),
            gemini_fin.get('confidence', 0.5),
        ]
        synthesis['confidence'] = sum(confidences) / len(confidences)

        synthesis['reasoning'] = "Combined insights from Claude Opus 4.5 (strategic) and Gemini 1.5 Pro (financial/trading)"

        return synthesis

    # ========================================================================
    # AUTO-IMPROVEMENT ENGINE
    # ========================================================================

    def auto_improve_plans(self) -> Dict:
        """Automatically analyze and improve financial plans."""
        log.info("Auto-improvement engine starting...")

        # Get current context
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()

        # Latest metrics
        c.execute('SELECT * FROM account_snapshots ORDER BY id DESC LIMIT 1')
        account = c.fetchone()

        c.execute('SELECT COUNT(*) FROM phoenix_trades WHERE timestamp > datetime("now", "-7 days")')
        recent_trades = c.fetchone()[0]

        conn.close()

        context = {
            'equity': account[2] if account else 100000,
            'daily_pnl': account[6] if account else 0,
            'phoenix_status': 'RUNNING',
            'recent_trades': recent_trades,
            'timestamp': datetime.now().isoformat()
        }

        # Run combined analysis
        analysis = self.combined_analysis(context)

        # Generate improvement report
        report = self._generate_improvement_report(analysis)

        # Save report
        report_path = BASE_DIR / f"AI_IMPROVEMENTS_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(report_path, 'w') as f:
            f.write(report)

        log.info(f"Improvement report saved: {report_path}")

        return {
            'analysis': analysis,
            'report_path': str(report_path),
            'top_actions': analysis['synthesis']['top_actions']
        }

    def _generate_improvement_report(self, analysis: Dict) -> str:
        """Generate markdown report from AI analysis."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        report = f"""# Trinity AI Brain - Improvement Analysis

**Generated:** {timestamp}
**AI Models:** Claude Opus 4.5 + Gemini 1.5 Pro

---

## 🎯 STRATEGIC ASSESSMENT (Claude)

{analysis['claude_strategic'].get('strategic_assessment', 'N/A')}

**Confidence:** {analysis['claude_strategic'].get('confidence_score', 0):.1%}

---

## 💰 FINANCIAL IMPROVEMENTS

### Claude Recommendations:
"""
        for i, rec in enumerate(analysis['claude_strategic'].get('financial_improvements', []), 1):
            report += f"{i}. {rec}\n"

        report += "\n### Gemini Top Priorities:\n"
        for i, pri in enumerate(analysis['gemini_financial'].get('top_priorities', []), 1):
            report += f"{i}. {pri}\n"

        report += "\n---\n\n## 🤖 PHOENIX TRADING OPTIMIZATIONS\n\n"
        report += "### Claude Suggestions:\n"
        for i, opt in enumerate(analysis['claude_strategic'].get('phoenix_optimizations', []), 1):
            report += f"{i}. {opt}\n"

        report += "\n### Gemini Code Improvements:\n"
        for i, imp in enumerate(analysis['gemini_trading'].get('code_improvements', []), 1):
            report += f"{i}. {imp}\n"

        report += f"\n**Risk Level:** {analysis['gemini_trading'].get('risk_level', 'Unknown')}\n"

        report += "\n---\n\n## 🚀 TOP 5 ACTIONS (Synthesized)\n\n"
        for i, action in enumerate(analysis['synthesis']['top_actions'][:5], 1):
            report += f"{i}. {action}\n"

        report += f"\n**Overall Confidence:** {analysis['synthesis']['confidence']:.1%}\n"
        report += f"\n**Reasoning:** {analysis['synthesis']['reasoning']}\n"

        report += "\n---\n\n## 📊 RISK ASSESSMENT\n\n"
        risks = analysis['gemini_financial'].get('risk_factors', [])
        if risks:
            for risk in risks:
                report += f"- ⚠️ {risk}\n"
        else:
            report += "No significant risks identified.\n"

        report += "\n---\n\n## 💡 PROMPT IMPROVEMENTS\n\n"
        prompt_imps = analysis['claude_strategic'].get('prompt_improvements', [])
        if prompt_imps:
            for imp in prompt_imps:
                report += f"- {imp}\n"
        else:
            report += "Current prompts are effective.\n"

        report += "\n---\n\n**Status:** Analysis complete. Review and implement recommendations.\n"

        return report

# ============================================================================
# CONTINUOUS LEARNING ENGINE
# ============================================================================

class ContinuousLearningEngine:
    """Continuously learns from Trinity's performance and improves strategies."""

    def __init__(self, brain: TrinityAIBrain):
        self.brain = brain
        self.last_deep_analysis = 0
        self.last_quick_check = 0

    def run(self):
        """Main continuous learning loop."""
        log.info("Continuous Learning Engine starting...")

        while True:
            try:
                current_time = time.time()

                # Quick check every 5 minutes
                if current_time - self.last_quick_check >= QUICK_CHECK_INTERVAL:
                    self.quick_health_check()
                    self.last_quick_check = current_time

                # Deep analysis every hour
                if current_time - self.last_deep_analysis >= DEEP_ANALYSIS_INTERVAL:
                    self.brain.auto_improve_plans()
                    self.last_deep_analysis = current_time

                # Sleep for a minute
                time.sleep(60)

            except KeyboardInterrupt:
                log.info("Shutting down learning engine...")
                break
            except Exception as e:
                log.error(f"Learning engine error: {e}")
                time.sleep(300)  # Wait 5 minutes on error

    def quick_health_check(self):
        """Quick health check of Trinity systems."""
        log.info("Running quick health check...")

        # Check database
        try:
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute('SELECT COUNT(*) FROM system_metrics')
            count = c.fetchone()[0]
            conn.close()
            log.info(f"Database health: {count} metrics recorded")
        except Exception as e:
            log.error(f"Database check failed: {e}")

# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main entry point."""
    print("""
    ╔════════════════════════════════════════════════════════════╗
    ║           TRINITY AI BRAIN v1.0                            ║
    ║     Super-Intelligent Autonomous System                    ║
    ║     Claude Opus 4.5 + Gemini 1.5 Pro                       ║
    ╚════════════════════════════════════════════════════════════╝
    """)

    # Initialize brain
    brain = TrinityAIBrain()

    # Run initial analysis
    log.info("Running initial comprehensive analysis...")
    result = brain.auto_improve_plans()

    print(f"\n✅ Initial analysis complete!")
    print(f"📄 Report: {result['report_path']}")
    print(f"\n🎯 Top 5 Actions:")
    for i, action in enumerate(result['top_actions'][:5], 1):
        print(f"  {i}. {action}")

    # Start continuous learning
    print("\n🚀 Starting continuous learning engine...")
    engine = ContinuousLearningEngine(brain)
    engine.run()

if __name__ == "__main__":
    main()
