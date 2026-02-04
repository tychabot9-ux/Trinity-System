#!/usr/bin/env python3
"""
Trinity Router - The Brain
Coordinates NEXUS (Gemini), JARVIS (Claude), and AVA (Voice)

Routing Logic:
- Job analysis → NEXUS (Gemini) for initial analysis
- Resume writing → JARVIS (Claude) for precise language
- Voice output → AVA (edge-tts) for speech
"""

import os
import sys
import subprocess
import tempfile
from pathlib import Path
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Add Bot-Factory to path for ava_speak import
bot_factory_path = Path.home() / "Desktop" / "Bot-Factory"
if bot_factory_path.exists():
    sys.path.insert(0, str(bot_factory_path))

class TrinityRouter:
    """The Trinity System - Personal AI Operating System"""

    def __init__(self):
        print("🔵 Initializing Trinity System...")

        # 1. NEXUS (Gemini): The Analyst & Memory
        try:
            from google import genai
            self.nexus_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
            print("  ✅ NEXUS (Gemini) online")
        except Exception as e:
            print(f"  ❌ NEXUS failed: {e}")
            self.nexus_client = None

        # 2. JARVIS (Claude): The Architect & Writer
        try:
            from anthropic import Anthropic
            self.jarvis_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
            print("  ✅ JARVIS (Claude) online")
        except Exception as e:
            print(f"  ❌ JARVIS failed: {e}")
            self.jarvis_client = None

        # 3. AVA (Voice): The Interface
        try:
            from ava_speak import speak
            self.ava_speak = speak
            print("  ✅ AVA (Voice) online")
        except ImportError:
            print("  ⚠️  AVA (Voice) not available - using fallback")
            self.ava_speak = self._fallback_speak

        print("🟢 Trinity System online\n")

    def _fallback_speak(self, text, blocking=True):
        """Fallback TTS using macOS say command"""
        try:
            if blocking:
                subprocess.run(["say", "-v", "Ava", text])
            else:
                subprocess.Popen(["say", "-v", "Ava", text],
                               stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL)
        except:
            print(f"[AVA]: {text}")

    def route_command(self, user_input: str, mode="auto") -> dict:
        """
        Route user command to appropriate AI system.

        Args:
            user_input: User's command/question
            mode: "auto" (detect), "job" (force job sniper), "chat" (force conversation)

        Returns:
            dict with 'response', 'source', and optional 'data'
        """
        print(f"\n⚡ Command Received: {user_input[:100]}...")

        # Detect mode if auto
        if mode == "auto":
            if any(word in user_input.lower() for word in ["job", "resume", "apply", "cover letter", "application"]):
                mode = "job"
            else:
                mode = "chat"

        # JOB SNIPER MODE
        if mode == "job":
            print("🎯 Routing to Job Sniper...")
            try:
                # Step 1: NEXUS analyzes the job
                analysis = self.ask_nexus(
                    f"Analyze this job posting for stress level, work environment, and fit "
                    f"for someone with carpentry/construction background transitioning to hospitality. "
                    f"Job info: {user_input}"
                )

                # Step 2: JARVIS creates tailored content
                if analysis:
                    cover_letter = self.ask_jarvis(
                        f"Based on this job analysis, write a professional cover letter "
                        f"for Ty Brown (carpentry/construction to hospitality transition). "
                        f"Analysis: {analysis}"
                    )

                    return {
                        "response": cover_letter,
                        "source": "Job Sniper (NEXUS + JARVIS)",
                        "data": {"analysis": analysis, "cover_letter": cover_letter}
                    }
            except Exception as e:
                return {"response": f"Job analysis failed: {e}", "source": "Error"}

        # CHAT MODE (default)
        else:
            print("💬 Routing to JARVIS for conversation...")
            response = self.ask_jarvis(user_input)
            return {
                "response": response,
                "source": "JARVIS (Claude)"
            }

    def ask_nexus(self, prompt: str) -> str:
        """Query NEXUS (Gemini) for analysis"""
        if not self.nexus_client:
            return "NEXUS unavailable"

        try:
            response = self.nexus_client.models.generate_content(
                model='models/gemini-2.5-pro',
                contents=prompt
            )
            return response.text
        except Exception as e:
            return f"NEXUS error: {e}"

    def ask_jarvis(self, prompt: str) -> str:
        """Query JARVIS (Claude) for deep reasoning"""
        if not self.jarvis_client:
            return "JARVIS unavailable"

        try:
            message = self.jarvis_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2048,
                messages=[{"role": "user", "content": prompt}]
            )
            return message.content[0].text
        except Exception as e:
            return f"JARVIS error: {e}"

    def speak_ava(self, text: str, blocking=False):
        """Speak text using AVA voice"""
        self.ava_speak(text, blocking=blocking)

    def analyze_job_posting(self, job_url_or_text: str) -> dict:
        """
        Complete job analysis workflow.

        Returns:
            dict with 'fit_score', 'analysis', 'recommendation'
        """
        print(f"\n🔍 Analyzing job posting...")

        # NEXUS: Initial analysis
        nexus_prompt = f"""Analyze this job posting and rate it for:
1. Stress Level (1-10, where 1=calm, 10=chaos)
2. Fit Score (1-100) for someone with:
   - Carpentry/construction background
   - Strong reliability and technical skills
   - Seeking hospitality day/evening shifts
   - Prefers organized, professional environments

Job posting: {job_url_or_text}

Respond with JSON format:
{{
  "stress_level": X,
  "fit_score": Y,
  "shift_type": "day/evening/night",
  "environment": "description",
  "recommendation": "apply/review/reject"
}}"""

        analysis = self.ask_nexus(nexus_prompt)

        # Parse and return
        try:
            import json
            import re
            # Extract JSON from response
            json_match = re.search(r'\{[^}]+\}', analysis, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                return {
                    "fit_score": data.get("fit_score", 0),
                    "analysis": analysis,
                    "recommendation": data.get("recommendation", "review"),
                    "raw_data": data
                }
        except:
            pass

        return {
            "fit_score": 0,
            "analysis": analysis,
            "recommendation": "review"
        }


# Quick Test
if __name__ == "__main__":
    print("=" * 70)
    print("  TRINITY SYSTEM - INITIALIZATION TEST")
    print("=" * 70)

    system = TrinityRouter()

    print("\n📊 System Status:")
    print(f"  NEXUS: {'✅ Online' if system.nexus_model else '❌ Offline'}")
    print(f"  JARVIS: {'✅ Online' if system.jarvis_client else '❌ Offline'}")
    print(f"  AVA: ✅ Online")

    print("\n🧪 Testing JARVIS...")
    response = system.ask_jarvis("What is 2+2? Answer in one sentence.")
    print(f"  Response: {response}")

    print("\n✅ Trinity System test complete")
