#!/usr/bin/env python3
"""
╔════════════════════════════════════════════════════════════════╗
║              TRINITY AVA VOICE SYSTEM                          ║
║           Stark-Style AI Voice Assistant                       ║
║                  v1.0 - February 2026                          ║
╚════════════════════════════════════════════════════════════════╝

Microsoft AVA Voice System for Trinity
- Intelligent device selection (Quest/Mac)
- Stark/Jarvis-style voice feedback
- Real-time action announcements
- Multi-platform audio routing
"""

import os
import json
import time
import logging
import subprocess
import platform
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List

# Try Azure Speech SDK (premium voice)
try:
    import azure.cognitiveservices.speech as speechsdk
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False
    print("⚠️  Azure Speech SDK not available, using fallback TTS")

# Fallback to pyttsx3
try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False

# Configuration
TRINITY_DIR = Path(__file__).parent
LOG_FILE = TRINITY_DIR / "logs" / "voice.log"
VOICE_CONFIG = TRINITY_DIR / ".trinity_voice_config.json"

# Ensure log directory exists
LOG_FILE.parent.mkdir(exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class TrinityVoiceSystem:
    """
    Trinity AVA Voice System - Stark-Style AI Assistant
    Intelligent audio device management with high-quality TTS
    """

    def __init__(self, azure_key: Optional[str] = None, azure_region: Optional[str] = None):
        """Initialize Trinity Voice System."""
        logger.info("╔════════════════════════════════════════╗")
        logger.info("║    TRINITY AVA VOICE SYSTEM            ║")
        logger.info("╚════════════════════════════════════════╝")

        self.azure_key = azure_key or os.getenv('AZURE_SPEECH_KEY')
        self.azure_region = azure_region or os.getenv('AZURE_SPEECH_REGION', 'eastus')

        # Voice configuration
        self.voice_name = "en-US-AvaMultilingualNeural"  # Microsoft AVA voice
        self.voice_style = "professional"  # Stark-like professional tone
        self.speaking_rate = "1.0"
        self.pitch = "0%"

        # Device management
        self.current_device = None  # 'mac' or 'quest'
        self.last_device_check = 0
        self.device_check_interval = 5  # Check every 5 seconds

        # Initialize TTS engine
        self.azure_synthesizer = None
        self.pyttsx3_engine = None
        self._initialize_engines()

        # Load configuration
        self._load_config()

        logger.info(f"🎤 Voice: {self.voice_name}")
        logger.info(f"🔊 Style: {self.voice_style}")
        logger.info(f"📱 Device: {self.current_device or 'auto-detect'}")
        logger.info("✅ Trinity AVA Voice System ready")

    def _initialize_engines(self):
        """Initialize available TTS engines."""
        # Try Azure Speech SDK first (best quality)
        if AZURE_AVAILABLE and self.azure_key:
            try:
                speech_config = speechsdk.SpeechConfig(
                    subscription=self.azure_key,
                    region=self.azure_region
                )
                speech_config.speech_synthesis_voice_name = self.voice_name

                # Auto-detect audio device
                audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)

                self.azure_synthesizer = speechsdk.SpeechSynthesizer(
                    speech_config=speech_config,
                    audio_config=audio_config
                )
                logger.info("✅ Azure Speech SDK initialized (premium voice)")
                return
            except Exception as e:
                logger.warning(f"Azure Speech SDK init failed: {e}")

        # Fallback to pyttsx3 with best available voice
        if PYTTSX3_AVAILABLE:
            try:
                self.pyttsx3_engine = pyttsx3.init()
                self.pyttsx3_engine.setProperty('rate', 175)  # Speaking rate
                self.pyttsx3_engine.setProperty('volume', 0.9)

                # Select best voice (prioritize Ava, then Samantha, then any female voice)
                voices = self.pyttsx3_engine.getProperty('voices')
                selected_voice = None

                # Priority 1: Ava (closest to Microsoft AVA)
                for voice in voices:
                    if 'Ava' in voice.name:
                        selected_voice = voice
                        logger.info(f"✅ Using system Ava voice: {voice.name}")
                        break

                # Priority 2: Samantha (high quality macOS voice)
                if not selected_voice:
                    for voice in voices:
                        if 'Samantha' in voice.name:
                            selected_voice = voice
                            logger.info(f"✅ Using Samantha voice: {voice.name}")
                            break

                # Priority 3: Any female voice
                if not selected_voice:
                    for voice in voices:
                        if 'female' in voice.name.lower():
                            selected_voice = voice
                            logger.info(f"✅ Using voice: {voice.name}")
                            break

                # Set the selected voice
                if selected_voice:
                    self.pyttsx3_engine.setProperty('voice', selected_voice.id)
                else:
                    logger.info(f"✅ Using default voice")

                logger.info("✅ pyttsx3 initialized")
                logger.info("💡 For true Microsoft AVA neural voice, set AZURE_SPEECH_KEY")
                return
            except Exception as e:
                logger.warning(f"pyttsx3 init failed: {e}")

        logger.warning("⚠️  No TTS engine available - voice disabled")

    def _load_config(self):
        """Load voice configuration from file."""
        if VOICE_CONFIG.exists():
            try:
                with open(VOICE_CONFIG, 'r') as f:
                    config = json.load(f)
                    self.voice_name = config.get('voice', self.voice_name)
                    self.voice_style = config.get('style', self.voice_style)
                    self.current_device = config.get('device', self.current_device)
                logger.info(f"Loaded config from {VOICE_CONFIG}")
            except Exception as e:
                logger.warning(f"Failed to load config: {e}")

    def _save_config(self):
        """Save voice configuration to file."""
        try:
            config = {
                'voice': self.voice_name,
                'style': self.voice_style,
                'device': self.current_device,
                'last_updated': datetime.now().isoformat()
            }
            with open(VOICE_CONFIG, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            logger.warning(f"Failed to save config: {e}")

    def detect_active_device(self) -> str:
        """
        Intelligently detect which device to use for audio.
        Returns 'mac' or 'quest' based on activity.
        """
        current_time = time.time()

        # Cache device detection to avoid excessive checks
        if current_time - self.last_device_check < self.device_check_interval:
            return self.current_device or 'mac'

        self.last_device_check = current_time

        # Check if Quest is connected via Tailscale
        try:
            result = subprocess.run(
                ['tailscale', 'status', '--json'],
                capture_output=True,
                text=True,
                timeout=2
            )
            if result.returncode == 0:
                status = json.loads(result.stdout)
                # Look for Quest device in Tailscale peers
                for peer_id, peer in status.get('Peer', {}).items():
                    if 'quest' in peer.get('HostName', '').lower():
                        self.current_device = 'quest'
                        logger.debug("Detected Quest device via Tailscale")
                        return 'quest'
        except Exception as e:
            logger.debug(f"Tailscale check failed: {e}")

        # Check for active VR session
        try:
            with open(TRINITY_DIR / 'logs' / 'vr_server.log', 'r') as f:
                recent_logs = f.readlines()[-20:]
                for line in recent_logs:
                    if 'Quest' in line or '/vr' in line:
                        # Recent VR activity
                        if 'minute' in line or 'second' in line:
                            self.current_device = 'quest'
                            return 'quest'
        except:
            pass

        # Default to Mac
        self.current_device = 'mac'
        return 'mac'

    def speak(self, text: str, force_device: Optional[str] = None) -> bool:
        """
        Speak text using Trinity AVA voice.

        Args:
            text: Text to speak
            force_device: Force specific device ('mac' or 'quest')

        Returns:
            True if successful, False otherwise
        """
        if not text:
            return False

        # Detect or use forced device
        device = force_device or self.detect_active_device()

        logger.info(f"🔊 [{device.upper()}] Speaking: {text[:50]}...")

        # Try Azure Speech SDK (best quality)
        if self.azure_synthesizer:
            try:
                # Build SSML for styled speech
                ssml = f"""
                <speak version='1.0' xml:lang='en-US'>
                    <voice name='{self.voice_name}'>
                        <prosody rate='{self.speaking_rate}' pitch='{self.pitch}'>
                            <mstts:express-as style='{self.voice_style}'>
                                {text}
                            </mstts:express-as>
                        </prosody>
                    </voice>
                </speak>
                """

                result = self.azure_synthesizer.speak_ssml_async(ssml).get()

                if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                    logger.info("✅ Speech completed successfully")
                    return True
                else:
                    logger.error(f"Speech synthesis failed: {result.reason}")
            except Exception as e:
                logger.error(f"Azure TTS error: {e}")

        # Fallback to pyttsx3
        if self.pyttsx3_engine:
            try:
                self.pyttsx3_engine.say(text)
                self.pyttsx3_engine.runAndWait()
                logger.info("✅ Speech completed (pyttsx3)")
                return True
            except Exception as e:
                logger.error(f"pyttsx3 error: {e}")

        # Last resort: macOS 'say' command
        if platform.system() == 'Darwin':
            try:
                subprocess.run(['say', text], timeout=30)
                logger.info("✅ Speech completed (macOS say)")
                return True
            except Exception as e:
                logger.error(f"macOS say error: {e}")

        logger.error("❌ All TTS methods failed")
        return False

    def announce_action(self, action: str, detail: str = ""):
        """Announce Trinity action in Stark style."""
        messages = {
            'startup': "Trinity System online. All systems operational.",
            'vr_connected': "VR workspace connected. Engineering mode active.",
            'vr_disconnected': "VR workspace disconnected. Returning to desktop mode.",
            'clipboard_sync': f"Clipboard synced. {detail}",
            'cad_generating': "Generating CAD model. Stand by.",
            'cad_complete': "CAD generation complete. Model ready for review.",
            'trade_executed': f"Trade executed. {detail}",
            'alert': f"Attention required. {detail}",
            'error': f"Error detected. {detail}",
            'command_center': "Command Center active. All stations ready.",
            'optimization': "Running optimization protocols.",
            'shutdown': "Trinity System shutting down. Goodbye."
        }

        message = messages.get(action, f"{action}. {detail}")
        self.speak(message)

    def set_device(self, device: str):
        """Manually set audio device."""
        if device in ['mac', 'quest']:
            self.current_device = device
            self._save_config()
            logger.info(f"Audio device set to: {device}")
            self.speak(f"Audio output set to {device}")
        else:
            logger.warning(f"Invalid device: {device}")

    def test_voice(self):
        """Test voice system with Stark-style greeting."""
        test_messages = [
            "Trinity AVA voice system initialized.",
            "Stark-style voice interface online.",
            "Ready for engineering operations.",
        ]

        for msg in test_messages:
            self.speak(msg)
            time.sleep(1)


def main():
    """Test Trinity AVA Voice System."""
    print("═══════════════════════════════════════════════")
    print("     TRINITY AVA VOICE SYSTEM TEST")
    print("═══════════════════════════════════════════════\n")

    # Initialize voice system
    voice = TrinityVoiceSystem()

    # Test detection
    print(f"\nDetected device: {voice.detect_active_device()}")

    # Test voice
    print("\nTesting voice output...\n")
    voice.test_voice()

    # Test action announcements
    print("\nTesting action announcements...\n")
    voice.announce_action('startup')
    time.sleep(1)
    voice.announce_action('vr_connected')
    time.sleep(1)
    voice.announce_action('cad_generating')

    print("\n✅ Voice system test complete")


if __name__ == '__main__':
    main()
