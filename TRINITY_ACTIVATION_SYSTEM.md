# Trinity Jarvis Activation System
## Universal Button Integration Architecture

**Version:** 1.0
**Date:** February 5, 2026
**Status:** Design Complete - Ready for Implementation

---

## Executive Summary

This document outlines the complete architecture for activating Trinity Jarvis voice assistant via single-button press across three hardware platforms: iPhone 17 Action button, MacBook F5 key, and Meta Quest controller. The system is designed to feel like Jarvis - instant, reliable, and natural.

**Target Response Time:** <500ms from button press to audio feedback
**Battery Impact:** <2% per day with background services
**Reliability:** 99.9% activation success rate
**Wake Word Alternative:** Hardware button provides instant activation without constant microphone listening

---

## Table of Contents

1. [System Architecture Overview](#system-architecture-overview)
2. [iPhone 17 Integration](#iphone-17-integration)
3. [MacBook Integration](#macbook-integration)
4. [Meta Quest Integration](#meta-quest-integration)
5. [Server Communication Protocol](#server-communication-protocol)
6. [Power Management](#power-management)
7. [Implementation Roadmap](#implementation-roadmap)
8. [Testing Plan](#testing-plan)
9. [Fallback Mechanisms](#fallback-mechanisms)

---

## System Architecture Overview

### High-Level Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                      ACTIVATION TRIGGER                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  iPhone Action Button  │  MacBook F5 Key  │  Quest Controller  │
│         Press          │       Press       │    Button Press    │
│           ↓            │         ↓         │         ↓          │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    LOCAL DEVICE HANDLER                         │
│  • Detect button press event                                    │
│  • Provide immediate haptic/audio feedback (<50ms)              │
│  • Start microphone recording                                   │
│  • Send activation signal to Trinity server                     │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                     TRINITY SERVER                              │
│  URL: http://192.168.1.216:8001                                 │
│  Endpoint: POST /voice/activate                                 │
│  • Receive activation signal                                    │
│  • Open bidirectional audio stream                              │
│  • Process voice input (Speech-to-Text)                         │
│  • Route to AI (JARVIS/NEXUS)                                   │
│  • Stream response (Text-to-Speech)                             │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                       DEVICE OUTPUT                             │
│  • Stream audio response to device                              │
│  • Visual feedback (animated UI)                                │
│  • Handle follow-up conversation                                │
│  • Auto-timeout after 10 seconds of silence                     │
└─────────────────────────────────────────────────────────────────┘
```

### Core Components

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Client Apps** | iOS/macOS/Quest native | Button capture + audio I/O |
| **Trinity Server** | FastAPI (Python) | Central processing hub |
| **Speech-to-Text** | Azure Cognitive Services | Voice recognition |
| **AI Router** | trinity_router.py | JARVIS/NEXUS routing |
| **Text-to-Speech** | Azure AVA Neural Voice | Natural voice response |
| **WebRTC** | LiveKit/Native | Low-latency audio streaming |

### Key Design Principles

1. **Instant Feedback** - User knows activation succeeded within 50ms
2. **Offline Fallback** - Core functions work without internet (local TTS/STT)
3. **Battery Efficiency** - Microphone only activates on button press
4. **Cross-Platform** - Consistent experience across all devices
5. **Privacy First** - No constant microphone listening, explicit activation only
6. **Network Resilient** - Graceful degradation on poor connectivity

---

## iPhone 17 Integration

### Platform Capabilities

Apple's Action button (iPhone 15 Pro+, iPhone 17) provides programmable hardware button access via:
- **App Intents Framework** - Direct app launching
- **Shortcuts Integration** - Custom automation workflows
- **Background Audio Mode** - Persistent audio session capability

### Technical Architecture

```swift
// TrinityJarvis iOS App Structure

┌──────────────────────────────────────────────┐
│         TrinityJarvisApp.swift               │
│  • App lifecycle management                  │
│  • Background audio session setup            │
│  • AppIntent registration                    │
└──────────────────────────────────────────────┘
                    ↓
┌──────────────────────────────────────────────┐
│       ActivateJarvisIntent.swift             │
│  • AppIntent conformance                     │
│  • Action button integration                 │
│  • Immediate activation response             │
└──────────────────────────────────────────────┘
                    ↓
┌──────────────────────────────────────────────┐
│        AudioSessionManager.swift             │
│  • AVAudioSession configuration              │
│  • Microphone input capture                  │
│  • Speaker output routing                    │
│  • Background audio handling                 │
└──────────────────────────────────────────────┘
                    ↓
┌──────────────────────────────────────────────┐
│         TrinityAPIClient.swift               │
│  • WebSocket connection to server            │
│  • Audio streaming (WebRTC)                  │
│  • Network error handling                    │
└──────────────────────────────────────────────┘
```

### Implementation Code Examples

#### 1. App Intent for Action Button

```swift
// ActivateJarvisIntent.swift
import AppIntents
import AVFoundation

struct ActivateJarvisIntent: AppIntent {
    static var title: LocalizedStringResource = "Activate Trinity Jarvis"
    static var description = IntentDescription("Activates Trinity Jarvis voice assistant")

    // Make this intent available to Action button
    static var openAppWhenRun: Bool = false

    @MainActor
    func perform() async throws -> some IntentResult {
        // Immediate haptic feedback
        let haptic = UIImpactFeedbackGenerator(style: .medium)
        haptic.impactOccurred()

        // Play activation tone
        AudioServicesPlaySystemSound(1519) // Peek sound

        // Start voice session
        let audioManager = AudioSessionManager.shared
        try await audioManager.startVoiceSession()

        // Connect to Trinity server
        let apiClient = TrinityAPIClient.shared
        try await apiClient.activateVoiceMode()

        return .result()
    }
}
```

#### 2. Background Audio Session

```swift
// AudioSessionManager.swift
import AVFoundation

class AudioSessionManager: ObservableObject {
    static let shared = AudioSessionManager()

    private let audioSession = AVAudioSession.sharedInstance()
    private var audioEngine = AVAudioEngine()

    func setupAudioSession() throws {
        // Configure for background audio and voice chat
        try audioSession.setCategory(
            .playAndRecord,
            mode: .voiceChat,
            options: [.allowBluetooth, .defaultToSpeaker, .mixWithOthers]
        )

        // Enable background audio
        try audioSession.setActive(true, options: [])

        print("✅ Audio session configured for voice interaction")
    }

    func startVoiceSession() async throws {
        // Start audio engine for recording
        let inputNode = audioEngine.inputNode
        let inputFormat = inputNode.outputFormat(forBus: 0)

        // Install tap to capture audio
        inputNode.installTap(onBus: 0, bufferSize: 4096, format: inputFormat) { buffer, time in
            // Stream audio to Trinity server
            Task {
                await self.streamAudioBuffer(buffer)
            }
        }

        try audioEngine.start()
        print("🎤 Voice session started")
    }

    func stopVoiceSession() {
        audioEngine.stop()
        audioEngine.inputNode.removeTap(onBus: 0)
        print("🛑 Voice session stopped")
    }

    private func streamAudioBuffer(_ buffer: AVAudioPCMBuffer) async {
        // Convert to data and stream via WebSocket
        let apiClient = TrinityAPIClient.shared
        await apiClient.streamAudio(buffer: buffer)
    }
}
```

#### 3. Trinity API Client

```swift
// TrinityAPIClient.swift
import Foundation

class TrinityAPIClient: ObservableObject {
    static let shared = TrinityAPIClient()

    private let baseURL = "http://192.168.1.216:8001"
    private let trinityPassword = "pineapple9devices"
    private var webSocket: URLSessionWebSocketTask?

    func activateVoiceMode() async throws {
        // HTTP activation request for immediate acknowledgment
        var request = URLRequest(url: URL(string: "\(baseURL)/voice/activate")!)
        request.httpMethod = "POST"
        request.setValue("Bearer \(trinityPassword)", forHTTPHeaderField: "Authorization")
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")

        let body = [
            "device": "iphone",
            "timestamp": ISO8601DateFormatter().string(from: Date())
        ]
        request.httpBody = try JSONSerialization.data(withJSONObject: body)

        let (data, response) = try await URLSession.shared.data(for: request)

        guard let httpResponse = response as? HTTPURLResponse,
              httpResponse.statusCode == 200 else {
            throw ActivationError.serverUnavailable
        }

        // Parse response and establish WebSocket for audio streaming
        try await setupWebSocketConnection()

        print("✅ Trinity Jarvis activated")
    }

    private func setupWebSocketConnection() async throws {
        let wsURL = URL(string: "ws://192.168.1.216:8001/voice/stream")!
        var request = URLRequest(url: wsURL)
        request.setValue("Bearer \(trinityPassword)", forHTTPHeaderField: "Authorization")

        webSocket = URLSession.shared.webSocketTask(with: request)
        webSocket?.resume()

        // Start listening for responses
        Task {
            await listenForMessages()
        }
    }

    func streamAudio(buffer: AVAudioPCMBuffer) async {
        // Convert buffer to PCM data
        guard let channelData = buffer.floatChannelData else { return }
        let frameLength = Int(buffer.frameLength)
        let channelCount = Int(buffer.format.channelCount)

        var audioData = Data()
        for frame in 0..<frameLength {
            for channel in 0..<channelCount {
                let sample = channelData[channel][frame]
                var intSample = Int16(sample * 32767.0)
                audioData.append(Data(bytes: &intSample, count: 2))
            }
        }

        // Send via WebSocket
        try? await webSocket?.send(.data(audioData))
    }

    private func listenForMessages() async {
        guard let webSocket = webSocket else { return }

        do {
            let message = try await webSocket.receive()

            switch message {
            case .data(let audioData):
                // Play audio response from Trinity
                await playAudioResponse(audioData)
            case .string(let text):
                print("📝 Trinity: \(text)")
            @unknown default:
                break
            }

            // Continue listening
            await listenForMessages()
        } catch {
            print("❌ WebSocket error: \(error)")
        }
    }

    private func playAudioResponse(_ audioData: Data) async {
        // Use AVAudioPlayer to play response
        let player = try? AVAudioPlayer(data: audioData)
        player?.play()
    }
}

enum ActivationError: Error {
    case serverUnavailable
    case audioSessionFailed
    case networkError
}
```

#### 4. Info.plist Configuration

```xml
<!-- Info.plist -->
<key>NSMicrophoneUsageDescription</key>
<string>Trinity Jarvis needs microphone access to process your voice commands</string>

<key>UIBackgroundModes</key>
<array>
    <string>audio</string>
    <string>processing</string>
</array>

<key>BGTaskSchedulerPermittedIdentifiers</key>
<array>
    <string>com.trinity.jarvis.refresh</string>
</array>
```

### iOS Shortcuts Integration

For users who want to set up Action button:

1. Open **Shortcuts** app
2. Create new shortcut: "Activate Jarvis"
3. Add action: **Run Shortcut** → Select "Activate Trinity Jarvis"
4. Go to **Settings** → **Action Button**
5. Select **Shortcut** → Choose "Activate Jarvis"

Alternative: Users can directly assign the Trinity Jarvis app to Action button if the AppIntent is properly registered.

### Power Management

```swift
// PowerManager.swift
class PowerManager {
    static let shared = PowerManager()

    func optimizeForBattery() {
        // Reduce network polling when on battery
        if ProcessInfo.processInfo.isLowPowerModeEnabled {
            // Use lower quality audio codec
            // Reduce keep-alive frequency
            // Buffer more audio before sending
        }
    }

    func handleBackgroundTask() {
        // Keep WebSocket alive with minimal heartbeat
        // ~1 request per minute = negligible battery impact
    }
}
```

### Expected Battery Impact

- **Idle (button not pressed):** <0.5% per day
  - Minimal background task scheduling
  - No microphone usage
  - Lightweight keep-alive pings

- **Active use (5 interactions/day, 30 sec each):** ~1-2% per day
  - Microphone capture: 0.3% per interaction
  - Network transmission: 0.1% per interaction
  - Audio playback: 0.2% per interaction

---

## MacBook Integration

### Platform Capabilities

macOS provides multiple approaches for global hotkey capture:
- **Carbon Events API** (deprecated but functional)
- **CGEventTap** (modern, requires Accessibility permissions)
- **Karabiner-Elements** (third-party, powerful)
- **LaunchAgent** (system-level daemon)

### Technical Architecture

```
┌──────────────────────────────────────────────┐
│      com.trinity.jarvis.plist                │
│  LaunchAgent daemon (auto-start at login)    │
│  • Keeps binary running in background        │
│  • Restarts on crash                         │
│  • Minimal resource usage                    │
└──────────────────────────────────────────────┘
                    ↓
┌──────────────────────────────────────────────┐
│      trinity_jarvis_hotkey (Swift CLI)       │
│  • CGEventTap for F5 key capture             │
│  • System-wide key interception              │
│  • Minimal memory footprint (~5MB)           │
└──────────────────────────────────────────────┘
                    ↓
┌──────────────────────────────────────────────┐
│         Trinity Server Communication         │
│  • POST /voice/activate                      │
│  • WebSocket audio streaming                 │
│  • Audio I/O via CoreAudio                   │
└──────────────────────────────────────────────┘
```

### Implementation Code Examples

#### 1. LaunchAgent Configuration

```xml
<!-- ~/Library/LaunchAgents/com.trinity.jarvis.plist -->
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.trinity.jarvis</string>

    <key>ProgramArguments</key>
    <array>
        <string>/Users/tybrown/Desktop/Trinity-System/macos_client/trinity_jarvis_hotkey</string>
    </array>

    <key>RunAtLoad</key>
    <true/>

    <key>KeepAlive</key>
    <dict>
        <key>SuccessfulExit</key>
        <false/>
    </dict>

    <key>StandardOutPath</key>
    <string>/Users/tybrown/Desktop/Trinity-System/logs/jarvis_hotkey.log</string>

    <key>StandardErrorPath</key>
    <string>/Users/tybrown/Desktop/Trinity-System/logs/jarvis_hotkey_error.log</string>

    <key>ProcessType</key>
    <string>Background</string>

    <key>Nice</key>
    <integer>10</integer>

    <key>ThrottleInterval</key>
    <integer>10</integer>
</dict>
</plist>
```

#### 2. Global Hotkey Handler (Swift)

```swift
// main.swift - trinity_jarvis_hotkey binary
import Foundation
import Cocoa
import AVFoundation

class TrinityHotkeyMonitor {
    private var eventTap: CFMachPort?
    private let targetKeyCode: CGKeyCode = 96 // F5 key
    private var isProcessingActivation = false

    func start() {
        // Request accessibility permissions if needed
        let options: NSDictionary = [kAXTrustedCheckOptionPrompt.takeRetainedValue() as String: true]
        let accessibilityEnabled = AXIsProcessTrustedWithOptions(options)

        if !accessibilityEnabled {
            print("⚠️  Accessibility permissions required. Please enable in System Settings.")
            exit(1)
        }

        // Create event tap for key monitoring
        let eventMask = (1 << CGEventType.keyDown.rawValue)

        guard let eventTap = CGEvent.tapCreate(
            tap: .cgSessionEventTap,
            place: .headInsertEventTap,
            options: .defaultTap,
            eventsOfInterest: CGEventMask(eventMask),
            callback: { proxy, type, event, refcon in
                let monitor = Unmanaged<TrinityHotkeyMonitor>.fromOpaque(refcon!).takeUnretainedValue()
                return monitor.handleKeyEvent(proxy: proxy, type: type, event: event)
            },
            userInfo: Unmanaged.passUnretained(self).toOpaque()
        ) else {
            print("❌ Failed to create event tap")
            exit(1)
        }

        self.eventTap = eventTap

        // Add to run loop
        let runLoopSource = CFMachPortCreateRunLoopSource(kCFAllocatorDefault, eventTap, 0)
        CFRunLoopAddSource(CFRunLoopGetCurrent(), runLoopSource, .commonModes)
        CGEvent.tapEnable(tap: eventTap, enable: true)

        print("✅ Trinity Jarvis hotkey monitor started (F5)")
        print("📍 Press F5 to activate voice assistant")

        // Run event loop
        CFRunLoopRun()
    }

    private func handleKeyEvent(proxy: CGEventTapProxy, type: CGEventType, event: CGEvent) -> Unmanaged<CGEvent>? {
        // Check if it's F5 key
        let keyCode = event.getIntegerValueField(.keyboardEventKeycode)

        if keyCode == Int64(targetKeyCode) && !isProcessingActivation {
            // Prevent multiple rapid activations
            isProcessingActivation = true

            // Play activation sound
            NSSound(named: "Pop")?.play()

            // Trigger Trinity activation
            Task {
                await activateTrinity()

                // Reset after 2 seconds
                try? await Task.sleep(nanoseconds: 2_000_000_000)
                isProcessingActivation = false
            }

            // Consume the key event (don't pass to other apps)
            return nil
        }

        // Pass through other keys
        return Unmanaged.passRetained(event)
    }

    private func activateTrinity() async {
        let client = TrinityMacClient.shared

        do {
            try await client.activateVoice()
            print("✅ Trinity activated at \(Date())")
        } catch {
            print("❌ Failed to activate Trinity: \(error)")
            // Play error sound
            NSSound(named: "Basso")?.play()
        }
    }

    deinit {
        if let eventTap = eventTap {
            CGEvent.tapEnable(tap: eventTap, enable: false)
            CFMachPortInvalidate(eventTap)
        }
    }
}

// Trinity Mac Client
class TrinityMacClient {
    static let shared = TrinityMacClient()

    private let baseURL = "http://192.168.1.216:8001"
    private let trinityPassword = "pineapple9devices"
    private var audioEngine = AVAudioEngine()

    func activateVoice() async throws {
        // Send activation request
        var request = URLRequest(url: URL(string: "\(baseURL)/voice/activate")!)
        request.httpMethod = "POST"
        request.setValue("Bearer \(trinityPassword)", forHTTPHeaderField: "Authorization")
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")

        let body: [String: Any] = [
            "device": "macbook",
            "timestamp": ISO8601DateFormatter().string(from: Date())
        ]
        request.httpBody = try JSONSerialization.data(withJSONObject: body)

        let (_, response) = try await URLSession.shared.data(for: request)

        guard let httpResponse = response as? HTTPURLResponse,
              httpResponse.statusCode == 200 else {
            throw ClientError.serverError
        }

        // Start audio capture
        try startAudioCapture()

        // Show visual feedback (overlay window)
        await showActivationOverlay()
    }

    private func startAudioCapture() throws {
        let inputNode = audioEngine.inputNode
        let inputFormat = inputNode.outputFormat(forBus: 0)

        inputNode.installTap(onBus: 0, bufferSize: 4096, format: inputFormat) { buffer, time in
            // Stream to Trinity server
            Task {
                await self.streamAudio(buffer)
            }
        }

        try audioEngine.start()
    }

    private func streamAudio(_ buffer: AVAudioPCMBuffer) async {
        // Implementation similar to iOS version
        // Convert buffer to data and send via WebSocket
    }

    private func showActivationOverlay() async {
        // Create transparent overlay window with Jarvis-style animation
        await MainActor.run {
            let overlay = ActivationOverlay()
            overlay.show()
        }
    }
}

enum ClientError: Error {
    case serverError
    case audioError
}

// Entry point
let monitor = TrinityHotkeyMonitor()
monitor.start()
```

#### 3. Visual Activation Overlay

```swift
// ActivationOverlay.swift
import Cocoa
import SwiftUI

class ActivationOverlay {
    private var window: NSWindow?

    func show() {
        let contentView = ActivationView()

        // Create transparent overlay window
        let window = NSWindow(
            contentRect: NSRect(x: 0, y: 0, width: 300, height: 100),
            styleMask: [.borderless, .nonactivatingPanel],
            backing: .buffered,
            defer: false
        )

        window.isOpaque = false
        window.backgroundColor = .clear
        window.level = .floating
        window.collectionBehavior = [.canJoinAllSpaces, .stationary]

        // Center on screen
        if let screen = NSScreen.main {
            let screenRect = screen.frame
            let windowRect = window.frame
            let x = (screenRect.width - windowRect.width) / 2
            let y = (screenRect.height - windowRect.height) / 2
            window.setFrameOrigin(NSPoint(x: x, y: y + 200))
        }

        window.contentView = NSHostingView(rootView: contentView)
        window.makeKeyAndOrderFront(nil)

        self.window = window

        // Auto-dismiss after 3 seconds
        DispatchQueue.main.asyncAfter(deadline: .now() + 3) {
            self.hide()
        }
    }

    func hide() {
        window?.close()
        window = nil
    }
}

struct ActivationView: View {
    @State private var isAnimating = false

    var body: some View {
        VStack(spacing: 12) {
            // Jarvis-style pulsing circle
            Circle()
                .fill(
                    RadialGradient(
                        gradient: Gradient(colors: [.blue, .cyan, .blue.opacity(0)]),
                        center: .center,
                        startRadius: 0,
                        endRadius: 50
                    )
                )
                .frame(width: 60, height: 60)
                .scaleEffect(isAnimating ? 1.2 : 1.0)
                .opacity(isAnimating ? 0.6 : 1.0)
                .animation(.easeInOut(duration: 1.0).repeatForever(autoreverses: true), value: isAnimating)

            Text("Jarvis Listening...")
                .font(.system(size: 16, weight: .medium, design: .rounded))
                .foregroundColor(.white)
        }
        .padding(24)
        .background(
            RoundedRectangle(cornerRadius: 16)
                .fill(.black.opacity(0.8))
                .shadow(color: .cyan.opacity(0.5), radius: 20)
        )
        .onAppear {
            isAnimating = true
        }
    }
}
```

#### 4. Installation Script

```bash
#!/bin/bash
# install_mac_hotkey.sh

echo "📦 Installing Trinity Jarvis hotkey monitor..."

# Build Swift binary
cd ~/Desktop/Trinity-System/macos_client
swiftc -O -o trinity_jarvis_hotkey main.swift ActivationOverlay.swift TrinityMacClient.swift

# Make executable
chmod +x trinity_jarvis_hotkey

# Install LaunchAgent
cp com.trinity.jarvis.plist ~/Library/LaunchAgents/

# Load LaunchAgent
launchctl unload ~/Library/LaunchAgents/com.trinity.jarvis.plist 2>/dev/null
launchctl load ~/Library/LaunchAgents/com.trinity.jarvis.plist

echo "✅ Trinity Jarvis hotkey installed!"
echo "📍 Press F5 anywhere to activate voice assistant"
echo ""
echo "⚠️  If F5 doesn't work:"
echo "   1. Go to System Settings → Privacy & Security → Accessibility"
echo "   2. Add 'trinity_jarvis_hotkey' to allowed apps"
echo "   3. Restart: launchctl unload & load"
```

### Alternative: Simple Python Version

For easier deployment without Swift compilation:

```python
#!/usr/bin/env python3
# trinity_hotkey_mac.py
import asyncio
import requests
from pynput import keyboard
from AppKit import NSSound
import os

TRINITY_URL = "http://192.168.1.216:8001"
TRINITY_PASSWORD = "pineapple9devices"
TARGET_KEY = keyboard.Key.f5

class TrinityHotkeyMac:
    def __init__(self):
        self.is_activating = False

    def on_press(self, key):
        if key == TARGET_KEY and not self.is_activating:
            self.is_activating = True

            # Play sound
            NSSound.soundNamed_("Pop").play()

            # Activate Trinity
            asyncio.run(self.activate_trinity())

            # Reset after 2 seconds
            asyncio.get_event_loop().call_later(2, self.reset_activation)

    async def activate_trinity(self):
        try:
            response = requests.post(
                f"{TRINITY_URL}/voice/activate",
                headers={
                    "Authorization": f"Bearer {TRINITY_PASSWORD}",
                    "Content-Type": "application/json"
                },
                json={
                    "device": "macbook",
                    "timestamp": datetime.now().isoformat()
                },
                timeout=2
            )

            if response.status_code == 200:
                print("✅ Trinity activated")
            else:
                print(f"❌ Activation failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Error: {e}")
            NSSound.soundNamed_("Basso").play()

    def reset_activation(self):
        self.is_activating = False

    def start(self):
        print("✅ Trinity Jarvis hotkey monitor started (F5)")
        with keyboard.Listener(on_press=self.on_press) as listener:
            listener.join()

if __name__ == "__main__":
    monitor = TrinityHotkeyMac()
    monitor.start()
```

### Power Management

- **Idle CPU:** <0.1%
- **Memory:** ~5MB (Swift) or ~20MB (Python)
- **Battery Impact:** Negligible (<0.1% per day)
- **Network:** Only activates on button press

### Permissions Required

1. **Accessibility Access** - Required for global hotkey capture
   - System Settings → Privacy & Security → Accessibility
   - Add `trinity_jarvis_hotkey` binary

2. **Microphone Access** - Required for voice input
   - Automatic prompt on first use

---

## Meta Quest Integration

### Platform Capabilities

Meta Quest provides controller input access via:
- **OVRInput API** - Unity/Unreal controller input
- **WebXR API** - Browser-based VR experiences
- **Android APK** - Native Quest app development

### Technical Architecture

Since Trinity VR workspace already runs in Quest browser, we'll extend it with controller button integration.

```
┌──────────────────────────────────────────────┐
│     Quest Browser (WebXR + JavaScript)       │
│  • Controller button detection               │
│  • Haptic feedback                           │
│  • Spatial audio output                      │
└──────────────────────────────────────────────┘
                    ↓
┌──────────────────────────────────────────────┐
│      Trinity VR Server (Python FastAPI)      │
│  URL: http://192.168.1.216:8503              │
│  • Voice activation endpoint                 │
│  • Audio streaming                           │
│  • Spatial audio rendering                   │
└──────────────────────────────────────────────┘
                    ↓
┌──────────────────────────────────────────────┐
│      Trinity Main Server (Port 8001)         │
│  • Process voice commands                    │
│  • AI routing (JARVIS/NEXUS)                 │
│  • Return audio response                     │
└──────────────────────────────────────────────┘
```

### Implementation Code Examples

#### 1. WebXR Controller Input

```javascript
// trinity_vr_voice.js
class TrinityVoiceVR {
    constructor() {
        this.isActivated = false;
        this.audioContext = new AudioContext();
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.ws = null;
    }

    // Initialize XR session with controller tracking
    async initializeXR() {
        if (!navigator.xr) {
            console.error("WebXR not supported");
            return;
        }

        const session = await navigator.xr.requestSession('immersive-vr', {
            requiredFeatures: ['local-floor'],
            optionalFeatures: ['hand-tracking']
        });

        // Get input sources (controllers)
        session.addEventListener('inputsourceschange', (event) => {
            event.added.forEach(input => {
                this.setupControllerInput(input);
            });
        });

        // Start XR render loop
        this.xrSession = session;
        this.startXRLoop();
    }

    // Setup controller button monitoring
    setupControllerInput(inputSource) {
        // Monitor button presses
        const gamepad = inputSource.gamepad;

        if (gamepad) {
            // Monitor buttons on each frame
            this.monitorButtons(gamepad);
        }
    }

    // Monitor controller buttons
    monitorButtons(gamepad) {
        const checkButtons = () => {
            if (!this.xrSession) return;

            // Button mapping (adjust based on preferred button)
            // buttons[0] = Trigger
            // buttons[1] = Grip
            // buttons[4] = A/X button
            // buttons[5] = B/Y button

            const activationButton = gamepad.buttons[4]; // A/X button

            if (activationButton.pressed && !this.isActivated) {
                this.activateJarvis();
            }

            // Continue monitoring
            this.xrSession.requestAnimationFrame(checkButtons);
        };

        this.xrSession.requestAnimationFrame(checkButtons);
    }

    // Activate Jarvis voice assistant
    async activateJarvis() {
        this.isActivated = true;

        // Haptic feedback
        this.triggerHaptics();

        // Visual feedback (blue glow overlay)
        this.showActivationUI();

        // Play activation sound
        await this.playActivationSound();

        // Start voice recording
        await this.startVoiceRecording();

        // Send activation signal to server
        await this.notifyServer();

        console.log("✅ Jarvis activated in VR");
    }

    // Trigger controller haptics
    triggerHaptics() {
        // Get active controllers
        if (this.xrSession && this.xrSession.inputSources) {
            this.xrSession.inputSources.forEach(inputSource => {
                if (inputSource.gamepad && inputSource.gamepad.hapticActuators) {
                    inputSource.gamepad.hapticActuators[0].pulse(0.6, 100);
                }
            });
        }
    }

    // Show activation UI overlay
    showActivationUI() {
        // Create WebXR overlay plane
        const overlayDiv = document.getElementById('vr-activation-overlay');
        if (overlayDiv) {
            overlayDiv.style.display = 'block';
            overlayDiv.classList.add('pulse-animation');

            // Hide after 3 seconds
            setTimeout(() => {
                overlayDiv.style.display = 'none';
                overlayDiv.classList.remove('pulse-animation');
            }, 3000);
        }
    }

    // Play activation sound in spatial audio
    async playActivationSound() {
        const audioUrl = '/sounds/jarvis_activation.mp3';

        try {
            const response = await fetch(audioUrl);
            const arrayBuffer = await response.arrayBuffer();
            const audioBuffer = await this.audioContext.decodeAudioData(arrayBuffer);

            const source = this.audioContext.createBufferSource();
            source.buffer = audioBuffer;

            // Add spatial audio positioning
            const panner = this.audioContext.createPanner();
            panner.panningModel = 'HRTF';
            panner.setPosition(0, 1, -1); // Above and in front of user

            source.connect(panner);
            panner.connect(this.audioContext.destination);
            source.start(0);
        } catch (error) {
            console.error("Failed to play activation sound:", error);
        }
    }

    // Start voice recording
    async startVoiceRecording() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({
                audio: {
                    echoCancellation: true,
                    noiseSuppression: true,
                    autoGainControl: true
                }
            });

            // Setup media recorder
            this.mediaRecorder = new MediaRecorder(stream, {
                mimeType: 'audio/webm;codecs=opus'
            });

            this.mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    this.audioChunks.push(event.data);
                }
            };

            this.mediaRecorder.onstop = () => {
                this.processVoiceInput();
            };

            // Start recording
            this.mediaRecorder.start(100); // Capture every 100ms

            // Setup WebSocket for streaming
            this.setupWebSocket();

            // Auto-stop after 10 seconds of silence (handled by server)

        } catch (error) {
            console.error("Microphone access failed:", error);
            this.showError("Microphone access denied");
            this.isActivated = false;
        }
    }

    // Setup WebSocket for real-time audio streaming
    setupWebSocket() {
        this.ws = new WebSocket('ws://192.168.1.216:8503/voice/stream');

        this.ws.onopen = () => {
            console.log("✅ Voice stream connected");
        };

        this.ws.onmessage = async (event) => {
            // Receive audio response from Trinity
            if (event.data instanceof Blob) {
                await this.playAudioResponse(event.data);
            } else {
                // Text response
                console.log("📝 Trinity:", event.data);
                this.showTextResponse(event.data);
            }
        };

        this.ws.onerror = (error) => {
            console.error("WebSocket error:", error);
        };

        this.ws.onclose = () => {
            console.log("🔌 Voice stream closed");
            this.isActivated = false;
        };
    }

    // Process recorded voice input
    async processVoiceInput() {
        if (this.audioChunks.length === 0) return;

        const audioBlob = new Blob(this.audioChunks, { type: 'audio/webm' });
        this.audioChunks = [];

        // Send to Trinity server via WebSocket
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(audioBlob);
        }
    }

    // Play audio response from Trinity
    async playAudioResponse(audioBlob) {
        try {
            const arrayBuffer = await audioBlob.arrayBuffer();
            const audioBuffer = await this.audioContext.decodeAudioData(arrayBuffer);

            const source = this.audioContext.createBufferSource();
            source.buffer = audioBuffer;

            // Spatial audio - voice comes from front
            const panner = this.audioContext.createPanner();
            panner.panningModel = 'HRTF';
            panner.setPosition(0, 0.5, -0.8);

            source.connect(panner);
            panner.connect(this.audioContext.destination);
            source.start(0);

            // Reset activation after playback
            source.onended = () => {
                this.isActivated = false;
            };
        } catch (error) {
            console.error("Failed to play audio response:", error);
        }
    }

    // Show text response in VR overlay
    showTextResponse(text) {
        const textDiv = document.getElementById('vr-response-text');
        if (textDiv) {
            textDiv.textContent = text;
            textDiv.style.display = 'block';

            setTimeout(() => {
                textDiv.style.display = 'none';
            }, 5000);
        }
    }

    // Notify server of activation
    async notifyServer() {
        try {
            const response = await fetch('http://192.168.1.216:8503/api/voice/activate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    device: 'meta_quest',
                    timestamp: new Date().toISOString()
                })
            });

            if (!response.ok) {
                throw new Error(`Server error: ${response.status}`);
            }
        } catch (error) {
            console.error("Failed to notify server:", error);
        }
    }

    // Show error in VR
    showError(message) {
        const errorDiv = document.getElementById('vr-error');
        if (errorDiv) {
            errorDiv.textContent = message;
            errorDiv.style.display = 'block';

            setTimeout(() => {
                errorDiv.style.display = 'none';
            }, 3000);
        }
    }
}

// Initialize on page load
let trinityVoice;

window.addEventListener('DOMContentLoaded', () => {
    trinityVoice = new TrinityVoiceVR();

    // Button to enter VR mode
    document.getElementById('enter-vr')?.addEventListener('click', async () => {
        await trinityVoice.initializeXR();
    });
});
```

#### 2. VR HTML Interface Enhancements

```html
<!-- trinity_vr_workspace_voice.html -->
<!DOCTYPE html>
<html>
<head>
    <title>Trinity VR - Voice Enabled</title>
    <meta charset="utf-8">
    <style>
        /* VR Overlay Styles */
        #vr-activation-overlay {
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 300px;
            padding: 30px;
            background: rgba(0, 50, 100, 0.9);
            border: 2px solid #00ffff;
            border-radius: 20px;
            text-align: center;
            display: none;
            z-index: 9999;
            box-shadow: 0 0 30px rgba(0, 255, 255, 0.6);
        }

        .pulse-animation {
            animation: pulse 1s infinite;
        }

        @keyframes pulse {
            0%, 100% {
                box-shadow: 0 0 30px rgba(0, 255, 255, 0.6);
                transform: translate(-50%, -50%) scale(1);
            }
            50% {
                box-shadow: 0 0 50px rgba(0, 255, 255, 1);
                transform: translate(-50%, -50%) scale(1.05);
            }
        }

        #vr-activation-overlay h2 {
            color: #00ffff;
            margin: 0;
            font-size: 24px;
            text-shadow: 0 0 10px rgba(0, 255, 255, 0.8);
        }

        #vr-response-text {
            position: fixed;
            bottom: 100px;
            left: 50%;
            transform: translateX(-50%);
            max-width: 600px;
            padding: 20px;
            background: rgba(0, 0, 0, 0.8);
            color: #00ffff;
            border: 1px solid #00ffff;
            border-radius: 10px;
            display: none;
            z-index: 9998;
            font-size: 18px;
            text-align: center;
        }

        #vr-error {
            position: fixed;
            top: 100px;
            left: 50%;
            transform: translateX(-50%);
            padding: 15px 30px;
            background: rgba(200, 0, 0, 0.9);
            color: white;
            border: 2px solid #ff0000;
            border-radius: 10px;
            display: none;
            z-index: 9999;
            font-size: 16px;
        }

        .jarvis-indicator {
            width: 60px;
            height: 60px;
            margin: 0 auto 15px;
            border-radius: 50%;
            background: radial-gradient(circle, #00ffff, #0088ff, transparent);
            animation: jarvis-pulse 1.5s infinite;
        }

        @keyframes jarvis-pulse {
            0%, 100% {
                opacity: 1;
                transform: scale(1);
            }
            50% {
                opacity: 0.6;
                transform: scale(1.2);
            }
        }
    </style>
</head>
<body>
    <!-- VR Activation Overlay -->
    <div id="vr-activation-overlay">
        <div class="jarvis-indicator"></div>
        <h2>JARVIS LISTENING</h2>
        <p style="color: #88ddff; margin: 10px 0 0 0;">Speak your command</p>
    </div>

    <!-- Response Text Display -->
    <div id="vr-response-text"></div>

    <!-- Error Display -->
    <div id="vr-error"></div>

    <!-- Enter VR Button -->
    <button id="enter-vr" style="position: absolute; top: 20px; left: 20px; padding: 15px 30px; font-size: 18px; background: #0088ff; color: white; border: none; border-radius: 8px; cursor: pointer;">
        Enter VR Mode
    </button>

    <!-- Include voice controller script -->
    <script src="/js/trinity_vr_voice.js"></script>

    <!-- Existing VR workspace scripts -->
    <script src="/js/vr_workspace.js"></script>
</body>
</html>
```

#### 3. Server-Side Voice Endpoint (Python)

```python
# vr_server.py additions
from fastapi import WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
import asyncio
import aiohttp

# Voice activation endpoint
@app.post("/api/voice/activate")
async def activate_voice(request: dict):
    """Handle voice activation from VR"""
    device = request.get("device", "unknown")
    timestamp = request.get("timestamp")

    logger.info(f"🎤 Voice activated from {device} at {timestamp}")

    # Forward to main Trinity server
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "http://localhost:8001/voice/activate",
            json={
                "device": device,
                "timestamp": timestamp,
                "source": "vr_workspace"
            },
            headers={"Authorization": f"Bearer {TRINITY_PASSWORD}"}
        ) as response:
            return await response.json()

# WebSocket for audio streaming
@app.websocket("/voice/stream")
async def voice_stream(websocket: WebSocket):
    """Stream audio bidirectionally with client"""
    await websocket.accept()

    logger.info("🔌 Voice stream WebSocket connected")

    try:
        # Create connection to main Trinity server
        async with aiohttp.ClientSession() as session:
            ws_url = "ws://localhost:8001/voice/stream"
            async with session.ws_connect(ws_url) as trinity_ws:

                # Bidirectional relay
                async def client_to_server():
                    while True:
                        # Receive from VR client
                        data = await websocket.receive_bytes()
                        # Forward to Trinity
                        await trinity_ws.send_bytes(data)

                async def server_to_client():
                    while True:
                        # Receive from Trinity
                        msg = await trinity_ws.receive()
                        # Forward to VR client
                        if msg.type == aiohttp.WSMsgType.BINARY:
                            await websocket.send_bytes(msg.data)
                        elif msg.type == aiohttp.WSMsgType.TEXT:
                            await websocket.send_text(msg.data)

                # Run both directions concurrently
                await asyncio.gather(
                    client_to_server(),
                    server_to_client()
                )

    except WebSocketDisconnect:
        logger.info("🔌 Voice stream disconnected")
    except Exception as e:
        logger.error(f"❌ Voice stream error: {e}")
```

### Native Quest App Alternative (Advanced)

For even better performance, a native Quest app can be built using Unity + OVRInput:

```csharp
// TrinityVoiceController.cs (Unity)
using UnityEngine;
using Oculus.Platform;

public class TrinityVoiceController : MonoBehaviour
{
    private bool isActivated = false;

    void Update()
    {
        // Check for A button press on right controller
        if (OVRInput.GetDown(OVRInput.Button.One, OVRInput.Controller.RTouch) && !isActivated)
        {
            ActivateJarvis();
        }
    }

    async void ActivateJarvis()
    {
        isActivated = true;

        // Haptic feedback
        OVRInput.SetControllerVibration(0.5f, 0.5f, OVRInput.Controller.RTouch);

        // Visual feedback
        ShowActivationUI();

        // Network call to Trinity server
        await TrinityAPI.ActivateVoice("meta_quest");

        // Start voice recording
        StartVoiceRecording();
    }

    void ShowActivationUI()
    {
        // Show glowing UI overlay
        GameObject.Find("ActivationOverlay").SetActive(true);
    }
}
```

### Power Management

- **Idle Impact:** 0% (no background process)
- **Active Session:** ~5% battery per interaction
  - Controller input: 0%
  - Audio recording: 2%
  - Network: 1%
  - Audio playback: 2%
- **Thermal:** Minimal (audio processing offloaded to server)

---

## Server Communication Protocol

### Trinity Server Enhancements

Add voice activation endpoints to main Trinity server (`main.py`):

```python
# main.py additions
from fastapi import WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.responses import StreamingResponse
import asyncio
import io
import wave
import azure.cognitiveservices.speech as speechsdk
from trinity_router import TrinityRouter

# Azure Speech Service configuration
AZURE_SPEECH_KEY = os.getenv("AZURE_SPEECH_KEY")
AZURE_SPEECH_REGION = os.getenv("AZURE_SPEECH_REGION", "eastus")

# Voice activation tracking
active_voice_sessions = {}

class VoiceSession:
    def __init__(self, session_id: str, device: str):
        self.session_id = session_id
        self.device = device
        self.started_at = datetime.now()
        self.audio_buffer = io.BytesIO()
        self.is_active = True

    def add_audio(self, audio_data: bytes):
        self.audio_buffer.write(audio_data)

    def get_audio(self) -> bytes:
        return self.audio_buffer.getvalue()

# Voice activation endpoint
@app.post("/voice/activate")
async def activate_voice(
    request: dict,
    background_tasks: BackgroundTasks,
    auth: bool = Depends(verify_password)
):
    """
    Activate Trinity voice assistant

    Request:
    {
        "device": "iphone|macbook|meta_quest",
        "timestamp": "2026-02-05T10:30:00Z",
        "source": "optional_source"
    }
    """
    device = request.get("device", "unknown")
    timestamp = request.get("timestamp")
    source = request.get("source", "direct")

    # Generate session ID
    session_id = f"{device}_{timestamp}_{os.urandom(4).hex()}"

    # Create voice session
    session = VoiceSession(session_id, device)
    active_voice_sessions[session_id] = session

    logger.info(f"🎤 Voice activated: {device} (session: {session_id})")

    # Schedule session cleanup after 30 seconds
    background_tasks.add_task(cleanup_voice_session, session_id, delay=30)

    return {
        "status": "activated",
        "session_id": session_id,
        "device": device,
        "timestamp": datetime.now().isoformat(),
        "message": "Trinity Jarvis listening..."
    }

# WebSocket for audio streaming
@app.websocket("/voice/stream")
async def voice_stream(websocket: WebSocket):
    """
    Bidirectional audio streaming with speech processing

    Client sends: Raw PCM audio data
    Server sends: Processed audio responses
    """
    await websocket.accept()

    session_id = None
    audio_buffer = io.BytesIO()

    logger.info("🔌 Voice stream WebSocket connected")

    try:
        # Speech recognition setup
        speech_config = speechsdk.SpeechConfig(
            subscription=AZURE_SPEECH_KEY,
            region=AZURE_SPEECH_REGION
        )
        speech_config.speech_recognition_language = "en-US"

        # Start continuous recognition
        async def process_audio_stream():
            nonlocal audio_buffer

            while True:
                # Receive audio data from client
                data = await websocket.receive_bytes()
                audio_buffer.write(data)

                # Check if we have enough audio to process (~1 second)
                if audio_buffer.tell() >= 16000 * 2:  # 16kHz, 16-bit
                    # Process accumulated audio
                    await process_voice_command(audio_buffer.getvalue(), websocket)
                    audio_buffer = io.BytesIO()  # Reset buffer

        await process_audio_stream()

    except WebSocketDisconnect:
        logger.info("🔌 Voice stream disconnected")
    except Exception as e:
        logger.error(f"❌ Voice stream error: {e}")
    finally:
        if session_id and session_id in active_voice_sessions:
            del active_voice_sessions[session_id]

async def process_voice_command(audio_data: bytes, websocket: WebSocket):
    """Process voice command through Speech-to-Text and AI"""
    try:
        # Convert audio to text using Azure Speech Service
        text = await speech_to_text(audio_data)

        if not text:
            return

        logger.info(f"🗣️  User said: {text}")

        # Send text back to client for display
        await websocket.send_text(f"You said: {text}")

        # Route to Trinity AI
        response = await trinity.process_message(text, mode="auto")

        logger.info(f"🤖 Trinity response: {response}")

        # Convert response to speech
        audio_response = await text_to_speech(response)

        # Send audio back to client
        await websocket.send_bytes(audio_response)

    except Exception as e:
        logger.error(f"❌ Voice processing error: {e}")
        await websocket.send_text(f"Error: {str(e)}")

async def speech_to_text(audio_data: bytes) -> str:
    """Convert speech to text using Azure Cognitive Services"""
    try:
        # Create audio configuration from bytes
        speech_config = speechsdk.SpeechConfig(
            subscription=AZURE_SPEECH_KEY,
            region=AZURE_SPEECH_REGION
        )
        speech_config.speech_recognition_language = "en-US"

        # Create audio stream from bytes
        audio_stream = speechsdk.audio.PushAudioInputStream()
        audio_stream.write(audio_data)
        audio_stream.close()

        audio_config = speechsdk.audio.AudioConfig(stream=audio_stream)

        # Create speech recognizer
        speech_recognizer = speechsdk.SpeechRecognizer(
            speech_config=speech_config,
            audio_config=audio_config
        )

        # Recognize speech
        result = speech_recognizer.recognize_once()

        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            return result.text
        elif result.reason == speechsdk.ResultReason.NoMatch:
            logger.warning("No speech recognized")
            return ""
        else:
            logger.error(f"Speech recognition error: {result.reason}")
            return ""

    except Exception as e:
        logger.error(f"❌ Speech-to-text error: {e}")
        return ""

async def text_to_speech(text: str) -> bytes:
    """Convert text to speech using Azure Cognitive Services"""
    try:
        speech_config = speechsdk.SpeechConfig(
            subscription=AZURE_SPEECH_KEY,
            region=AZURE_SPEECH_REGION
        )

        # Use AVA neural voice
        speech_config.speech_synthesis_voice_name = "en-US-AvaMultilingualNeural"

        # Create synthesizer with in-memory output
        audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=False)
        synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=speech_config,
            audio_config=None  # Return audio data
        )

        # Synthesize with SSML for better control
        ssml = f"""
        <speak version='1.0' xml:lang='en-US'>
            <voice name='en-US-AvaMultilingualNeural'>
                <prosody rate='1.0' pitch='0%'>
                    {text}
                </prosody>
            </voice>
        </speak>
        """

        result = synthesizer.speak_ssml_async(ssml).get()

        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            return result.audio_data
        else:
            logger.error(f"TTS error: {result.reason}")
            return b""

    except Exception as e:
        logger.error(f"❌ Text-to-speech error: {e}")
        return b""

async def cleanup_voice_session(session_id: str, delay: int = 0):
    """Clean up inactive voice session"""
    if delay > 0:
        await asyncio.sleep(delay)

    if session_id in active_voice_sessions:
        session = active_voice_sessions[session_id]
        if session.is_active:
            session.is_active = False
            del active_voice_sessions[session_id]
            logger.info(f"🧹 Voice session cleaned up: {session_id}")

# Health check for voice system
@app.get("/voice/health")
async def voice_health():
    """Check voice system health"""
    azure_configured = bool(AZURE_SPEECH_KEY)

    return {
        "status": "operational" if azure_configured else "degraded",
        "azure_configured": azure_configured,
        "active_sessions": len(active_voice_sessions),
        "timestamp": datetime.now().isoformat()
    }
```

### Network Protocol Specifications

#### 1. Activation Request (HTTP POST)

```http
POST /voice/activate HTTP/1.1
Host: 192.168.1.216:8001
Authorization: Bearer pineapple9devices
Content-Type: application/json

{
    "device": "iphone",
    "timestamp": "2026-02-05T10:30:00Z",
    "source": "action_button"
}
```

**Response:**
```json
{
    "status": "activated",
    "session_id": "iphone_2026-02-05T10:30:00Z_a3f9d2c1",
    "device": "iphone",
    "timestamp": "2026-02-05T10:30:00.123Z",
    "message": "Trinity Jarvis listening..."
}
```

#### 2. Audio Streaming (WebSocket)

```
WebSocket URL: ws://192.168.1.216:8001/voice/stream

Client → Server: Binary frames (PCM audio, 16kHz, 16-bit, mono)
Server → Client: Binary frames (MP3/Opus audio responses)
Server → Client: Text frames (transcription, status updates)
```

**Frame Format:**
- **Audio Data:** Raw PCM bytes
- **Sample Rate:** 16000 Hz
- **Bit Depth:** 16-bit
- **Channels:** Mono
- **Frame Size:** 4096 bytes (~128ms of audio)

#### 3. Error Handling

```json
// Server error response
{
    "error": "speech_recognition_failed",
    "message": "Could not recognize speech. Please try again.",
    "retry_after": 2
}
```

### Latency Budget

| Stage | Target | Notes |
|-------|--------|-------|
| **Button Press → Haptic** | <50ms | Local device feedback |
| **Network Request** | <100ms | LAN, <20ms typical |
| **Server Processing** | <50ms | Session setup |
| **Total Activation** | <200ms | User perceives instant |
| **Speech Recognition** | <500ms | Azure STT |
| **AI Processing** | <1000ms | JARVIS/NEXUS |
| **Speech Synthesis** | <500ms | Azure TTS |
| **Audio Playback Start** | <100ms | Streaming begins |
| **Total Response** | <2000ms | Complete interaction |

---

## Power Management

### Battery Impact Analysis

#### iPhone 17

**Baseline (No Trinity):** 100% battery over 24 hours
**With Trinity Idle:** 99.5% battery over 24 hours (-0.5%)
**With 10 Activations/Day:** 98% battery over 24 hours (-2%)

**Breakdown per Activation (30 seconds):**
- Microphone capture: 0.05%
- Network transmission: 0.02%
- Audio playback: 0.03%
- Background service: 0.01%
- **Total:** ~0.11% per 30-second interaction

**Daily Usage Scenarios:**
- Light (5 interactions): -0.5% + (5 × 0.11%) = -1.05%
- Medium (10 interactions): -0.5% + (10 × 0.11%) = -1.6%
- Heavy (20 interactions): -0.5% + (20 × 0.11%) = -2.7%

#### MacBook

**Impact:** Negligible
- Background daemon: <0.1% CPU idle
- Memory: 5-20 MB
- Battery: <0.1% per day (plugged in most of the time)

#### Meta Quest

**Impact:** Moderate during VR sessions
- No background service (browser-based)
- Per activation: ~5% battery
- 10 activations in 2-hour VR session: ~50% battery (typical VR usage already consumes 40-50%/hour)

### Optimization Strategies

#### 1. Adaptive Quality

```python
# Low battery mode
if battery_level < 20:
    audio_quality = "low"  # 8kHz sampling
    buffer_size = 8192     # Larger buffers, less frequent transmission
    compression = "opus"   # More efficient codec
else:
    audio_quality = "high" # 16kHz sampling
    buffer_size = 4096
    compression = "pcm"
```

#### 2. Network Optimization

```python
# Use WiFi when available, fallback to cellular
if network_type == "wifi":
    stream_continuously = True
else:  # Cellular
    stream_in_chunks = True  # Batch audio data
```

#### 3. Background Task Scheduling

```python
# iOS Background Task (rare keep-alive)
import BackgroundTasks

func scheduleKeepAlive() {
    let request = BGAppRefreshTaskRequest(identifier: "com.trinity.jarvis.keepalive")
    request.earliestBeginDate = Date(timeIntervalSinceNow: 15 * 60)  # 15 minutes

    try? BGTaskScheduler.shared.submit(request)
}
```

---

## Implementation Roadmap

### Phase 1: Core Infrastructure (Week 1-2)

**Milestone:** Server-side voice processing ready

- [ ] Add `/voice/activate` endpoint to main.py
- [ ] Add `/voice/stream` WebSocket endpoint
- [ ] Integrate Azure Speech Services (STT/TTS)
- [ ] Test with curl/Postman
- [ ] Add voice system health check
- [ ] Update `.env` with Azure credentials

**Success Criteria:**
- Server responds to activation requests
- WebSocket accepts audio streams
- Speech-to-text works with test audio
- Text-to-speech generates AVA voice responses

### Phase 2: MacBook Integration (Week 2-3)

**Milestone:** F5 key activates Trinity on Mac

- [ ] Create Swift hotkey monitor binary
- [ ] Create LaunchAgent plist
- [ ] Build installation script
- [ ] Test F5 key capture
- [ ] Add activation overlay UI
- [ ] Test audio streaming Mac → Server
- [ ] Test audio playback Server → Mac
- [ ] Handle Accessibility permissions

**Success Criteria:**
- F5 press detected system-wide
- Activation overlay appears
- Voice recorded and sent to server
- Response played through Mac speakers
- <500ms activation latency

### Phase 3: iPhone Integration (Week 3-4)

**Milestone:** Action button activates Trinity on iPhone

- [ ] Create iOS app (TrinityJarvis)
- [ ] Implement AppIntent for Action button
- [ ] Configure background audio session
- [ ] Build API client with WebSocket
- [ ] Add activation haptics and sound
- [ ] Test on iPhone 17
- [ ] Submit to TestFlight
- [ ] Configure Action button shortcut

**Success Criteria:**
- Action button triggers app
- Microphone captures voice
- Audio streams to server
- Response plays on iPhone
- Works in background
- Battery impact <2% per day

### Phase 4: Meta Quest Integration (Week 4-5)

**Milestone:** Controller button activates Trinity in VR

- [ ] Add WebXR controller input to VR workspace
- [ ] Create activation overlay UI for VR
- [ ] Add spatial audio positioning
- [ ] Implement WebRTC audio streaming
- [ ] Add haptic feedback
- [ ] Test in Quest browser
- [ ] Optimize for VR performance

**Success Criteria:**
- Controller button detected
- Haptic feedback works
- Voice captured in VR
- Response in spatial audio
- <500ms activation latency
- No VR frame drops

### Phase 5: Testing & Refinement (Week 5-6)

**Milestone:** All platforms working reliably

- [ ] Cross-platform testing
- [ ] Battery impact measurements
- [ ] Latency optimization
- [ ] Error handling edge cases
- [ ] Network resilience testing
- [ ] User experience refinement
- [ ] Documentation completion

**Success Criteria:**
- 99% activation success rate
- <500ms average response time
- <2% battery impact on mobile
- Graceful degradation on poor network
- Complete user documentation

### Phase 6: Advanced Features (Week 6+)

**Milestone:** Enhanced Jarvis-like capabilities

- [ ] Context-aware responses (knows which device)
- [ ] Multi-turn conversations
- [ ] Background task execution ("Remind me in 10 minutes")
- [ ] Device handoff ("Continue on Mac")
- [ ] Offline mode with local STT/TTS
- [ ] Custom wake word training
- [ ] Voice biometrics (recognize Ty)

---

## Testing Plan

### Unit Tests

#### Server-Side

```python
# test_voice_activation.py
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_voice_activation_endpoint():
    """Test voice activation endpoint"""
    response = client.post(
        "/voice/activate",
        json={
            "device": "test_device",
            "timestamp": "2026-02-05T10:00:00Z"
        },
        headers={"Authorization": "Bearer pineapple9devices"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "activated"
    assert "session_id" in data

def test_voice_activation_requires_auth():
    """Test authentication required"""
    response = client.post(
        "/voice/activate",
        json={"device": "test"}
    )

    assert response.status_code == 401

def test_speech_to_text():
    """Test STT with sample audio"""
    # Load test audio file
    with open("test_audio.wav", "rb") as f:
        audio_data = f.read()

    text = await speech_to_text(audio_data)
    assert len(text) > 0
    assert "hello" in text.lower()

def test_text_to_speech():
    """Test TTS generation"""
    audio_data = await text_to_speech("Hello, this is Trinity")
    assert len(audio_data) > 0
    assert audio_data[:4] == b'RIFF'  # WAV file header
```

#### Client-Side (iOS)

```swift
// TrinityAPIClientTests.swift
import XCTest
@testable import TrinityJarvis

class TrinityAPIClientTests: XCTestCase {
    var client: TrinityAPIClient!

    override func setUp() {
        super.setUp()
        client = TrinityAPIClient.shared
    }

    func testActivation() async throws {
        // Test activation request
        try await client.activateVoiceMode()

        // Verify WebSocket connected
        XCTAssertNotNil(client.webSocket)
    }

    func testAudioStreaming() async throws {
        // Create test audio buffer
        let buffer = createTestAudioBuffer()

        // Stream to server
        await client.streamAudio(buffer: buffer)

        // Should not throw
    }

    func testErrorHandling() async {
        // Simulate server unavailable
        // Should throw ActivationError.serverUnavailable
    }
}
```

### Integration Tests

#### Cross-Platform Activation

```bash
#!/bin/bash
# test_all_platforms.sh

echo "Testing Trinity Activation System..."

# Test 1: Server health
echo "1. Testing server health..."
curl -s http://192.168.1.216:8001/voice/health | jq

# Test 2: Activation from Mac
echo "2. Testing Mac activation..."
curl -X POST http://192.168.1.216:8001/voice/activate \
  -H "Authorization: Bearer pineapple9devices" \
  -H "Content-Type: application/json" \
  -d '{"device":"macbook","timestamp":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"}'

# Test 3: WebSocket connection
echo "3. Testing WebSocket..."
wscat -c ws://192.168.1.216:8001/voice/stream

# Test 4: Battery impact (iOS)
echo "4. Checking iOS battery stats..."
# Run on device, capture battery logs

# Test 5: Latency measurement
echo "5. Measuring latency..."
for i in {1..10}; do
  start=$(date +%s%N)
  curl -s -X POST http://192.168.1.216:8001/voice/activate \
    -H "Authorization: Bearer pineapple9devices" \
    -H "Content-Type: application/json" \
    -d '{"device":"test","timestamp":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"}' > /dev/null
  end=$(date +%s%N)
  latency=$(( (end - start) / 1000000 ))
  echo "  Attempt $i: ${latency}ms"
done
```

### Performance Tests

#### Latency Test

```python
# test_latency.py
import asyncio
import time
import aiohttp

async def measure_activation_latency(iterations=100):
    """Measure average activation latency"""
    latencies = []

    async with aiohttp.ClientSession() as session:
        for i in range(iterations):
            start = time.perf_counter()

            async with session.post(
                "http://192.168.1.216:8001/voice/activate",
                json={
                    "device": "test",
                    "timestamp": datetime.now().isoformat()
                },
                headers={"Authorization": "Bearer pineapple9devices"}
            ) as response:
                await response.json()

            end = time.perf_counter()
            latency_ms = (end - start) * 1000
            latencies.append(latency_ms)

            await asyncio.sleep(0.1)  # Brief pause between tests

    avg_latency = sum(latencies) / len(latencies)
    p95_latency = sorted(latencies)[int(len(latencies) * 0.95)]
    p99_latency = sorted(latencies)[int(len(latencies) * 0.99)]

    print(f"Activation Latency Results ({iterations} iterations):")
    print(f"  Average: {avg_latency:.2f}ms")
    print(f"  P95: {p95_latency:.2f}ms")
    print(f"  P99: {p99_latency:.2f}ms")
    print(f"  Target: <200ms ({'✅ PASS' if avg_latency < 200 else '❌ FAIL'})")

asyncio.run(measure_activation_latency())
```

#### Battery Test (iOS)

```swift
// BatteryTestViewController.swift
import UIKit
import os.log

class BatteryTestViewController: UIViewController {
    func runBatteryImpactTest() {
        // Record initial battery level
        UIDevice.current.isBatteryMonitoringEnabled = true
        let initialLevel = UIDevice.current.batteryLevel
        let startTime = Date()

        // Perform 50 activations over 1 hour
        var activationCount = 0
        Timer.scheduledTimer(withTimeInterval: 72, repeats: true) { timer in
            Task {
                try? await TrinityAPIClient.shared.activateVoiceMode()
                activationCount += 1

                if activationCount >= 50 {
                    timer.invalidate()
                    self.completeBatteryTest(
                        initialLevel: initialLevel,
                        startTime: startTime
                    )
                }
            }
        }
    }

    func completeBatteryTest(initialLevel: Float, startTime: Date) {
        let finalLevel = UIDevice.current.batteryLevel
        let duration = Date().timeIntervalSince(startTime)
        let batteryDrop = (initialLevel - finalLevel) * 100

        let report = """
        Battery Impact Test Results:
        Duration: \(duration / 3600) hours
        Activations: 50
        Battery drop: \(batteryDrop)%
        Per activation: \(batteryDrop / 50)%
        Extrapolated daily (10 activations): ~\((batteryDrop / 50) * 10)%
        """

        print(report)
        os_log("%{public}@", log: .default, type: .info, report)
    }
}
```

### User Acceptance Tests

#### Test Scenarios

1. **Instant Activation**
   - Press button
   - Expect: Haptic/sound within 50ms
   - Expect: "Listening" UI within 200ms
   - PASS/FAIL: _____

2. **Voice Recognition**
   - Say: "What's the weather today?"
   - Expect: Accurate transcription
   - Expect: Relevant response
   - PASS/FAIL: _____

3. **Background Reliability**
   - Activate with other apps open
   - Expect: Works in any app
   - Expect: No crashes
   - PASS/FAIL: _____

4. **Network Resilience**
   - Test on WiFi, 5G, poor connection
   - Expect: Graceful degradation
   - Expect: Error message on failure
   - PASS/FAIL: _____

5. **Battery Impact**
   - Use normally for 1 day
   - Measure battery drain
   - Expect: <2% additional drain
   - PASS/FAIL: _____

---

## Fallback Mechanisms

### Network Failure Handling

#### Offline Mode (Local Processing)

```python
# offline_voice.py
import pyttsx3  # Local TTS
import speech_recognition as sr  # Local STT

class OfflineVoiceSystem:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.tts_engine = pyttsx3.init()
        self.tts_engine.setProperty('voice', 'com.apple.speech.synthesis.voice.samantha')

    def process_offline(self, audio_data):
        """Process voice command offline"""
        try:
            # Local speech recognition (uses CMU Sphinx)
            text = self.recognizer.recognize_sphinx(audio_data)

            # Simple keyword-based responses
            response = self.simple_command_handler(text)

            # Local TTS
            self.tts_engine.say(response)
            self.tts_engine.runAndWait()

        except sr.UnknownValueError:
            self.tts_engine.say("I didn't understand that")
            self.tts_engine.runAndWait()

    def simple_command_handler(self, text: str) -> str:
        """Handle simple commands offline"""
        text_lower = text.lower()

        if "time" in text_lower:
            return f"The time is {datetime.now().strftime('%I:%M %p')}"
        elif "date" in text_lower:
            return f"Today is {datetime.now().strftime('%A, %B %d, %Y')}"
        elif "battery" in text_lower:
            # Check device battery
            return f"Battery is at {self.get_battery_level()}%"
        else:
            return "I need an internet connection for that request"

    def get_battery_level(self) -> int:
        # Platform-specific battery check
        return 80  # Placeholder
```

#### Retry Logic

```python
# client retry logic
async def activate_with_retry(max_retries=3):
    """Activate with exponential backoff"""
    for attempt in range(max_retries):
        try:
            await TrinityAPIClient.shared.activateVoiceMode()
            return
        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                await asyncio.sleep(wait_time)
            else:
                # Final fallback: offline mode
                await activate_offline_mode()
```

### Server Failure Handling

#### Graceful Degradation

```python
@app.post("/voice/activate")
async def activate_voice(request: dict):
    """Activation with fallback"""
    try:
        # Try Azure Speech Services
        return await activate_with_azure(request)
    except AzureError:
        # Fallback to local TTS/STT
        return await activate_with_local(request)
    except Exception as e:
        # Ultimate fallback
        return {
            "status": "degraded",
            "message": "Voice system in limited mode",
            "error": str(e)
        }
```

#### Health Monitoring

```python
# health_monitor.py
async def monitor_voice_system():
    """Continuous health monitoring"""
    while True:
        try:
            # Check Azure Speech Service
            azure_healthy = await check_azure_health()

            # Check server resources
            cpu_usage = psutil.cpu_percent()
            memory_usage = psutil.virtual_memory().percent

            # Check active sessions
            session_count = len(active_voice_sessions)

            health_status = {
                "azure_healthy": azure_healthy,
                "cpu_usage": cpu_usage,
                "memory_usage": memory_usage,
                "active_sessions": session_count,
                "status": "healthy" if azure_healthy and cpu_usage < 80 else "degraded"
            }

            logger.info(f"Voice system health: {health_status}")

        except Exception as e:
            logger.error(f"Health check failed: {e}")

        await asyncio.sleep(60)  # Check every minute
```

### Client-Side Error Handling

```swift
// ErrorHandler.swift
class VoiceErrorHandler {
    func handleActivationError(_ error: Error) {
        switch error {
        case ActivationError.serverUnavailable:
            showAlert("Trinity server is offline. Try again later.")
            playErrorSound()

        case ActivationError.networkError:
            showAlert("Network connection lost. Check your WiFi.")
            // Retry with offline mode
            activateOfflineMode()

        case ActivationError.audioSessionFailed:
            showAlert("Microphone access required. Check Settings.")
            openSettings()

        default:
            showAlert("Activation failed. Please try again.")
        }
    }

    func activateOfflineMode() {
        // Limited functionality without server
        let offlineVoice = OfflineVoiceSystem()
        offlineVoice.start()
    }
}
```

---

## Security Considerations

### Authentication

All voice activation requests require Trinity password authentication:

```http
Authorization: Bearer pineapple9devices
```

### Privacy

- **No Recording Without Activation:** Microphone only active when button pressed
- **Local Processing Option:** Can run with local STT/TTS (no cloud)
- **Session Timeouts:** Automatic cleanup after 30 seconds
- **Audio Not Stored:** No server-side recording storage

### Network Security

- **Local Network Only:** Server on private IP (192.168.1.216)
- **Consider HTTPS:** Add SSL/TLS for production
- **WebSocket Security:** Token-based authentication
- **Rate Limiting:** Prevent abuse

```python
# rate_limiting.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/voice/activate")
@limiter.limit("30/minute")  # Max 30 activations per minute
async def activate_voice(request: Request):
    # ... activation logic
```

---

## Cost Analysis

### Azure Speech Services

**Pricing (as of 2026):**
- Speech-to-Text: $1.00 per hour
- Text-to-Speech (Neural): $16.00 per 1M characters

**Usage Estimates:**

| Scenario | Daily Cost | Monthly Cost | Annual Cost |
|----------|-----------|--------------|-------------|
| Light (5 interactions/day, 30s avg) | $0.02 | $0.60 | $7.20 |
| Medium (10 interactions/day) | $0.04 | $1.20 | $14.40 |
| Heavy (20 interactions/day) | $0.08 | $2.40 | $28.80 |

**Cost Savings with Local Processing:**
- Use local STT/TTS for simple commands
- Reserve Azure for complex queries
- Estimated savings: 50-70%

### Alternative: Free/Local Options

**Mozilla DeepSpeech (STT):**
- Free, open-source
- Runs locally
- Lower accuracy than Azure

**Coqui TTS (TTS):**
- Free, open-source
- Neural voices
- Requires local GPU

**Recommendation:** Start with Azure for best quality, migrate to local for cost reduction at scale.

---

## Future Enhancements

### Phase 7: Advanced Features

1. **Context Awareness**
   - "Continue on Mac" → Seamless device handoff
   - "Show on screen" → Display visual results
   - Location-aware responses

2. **Proactive Assistance**
   - "Remind me in 10 minutes"
   - "Alert me when Ty gets home"
   - Calendar integration

3. **Multi-User Support**
   - Voice biometrics to identify Ty vs others
   - Personalized responses
   - User-specific permissions

4. **Custom Wake Word**
   - Train "Hey Jarvis" wake word
   - On-device wake word detection
   - No button press required

5. **Advanced Audio**
   - Real-time translation
   - Background noise cancellation
   - Voice activity detection (VAD)

6. **Offline Intelligence**
   - Local LLM (Llama 3.3)
   - On-device knowledge base
   - Works without internet

---

## Conclusion

This Trinity Jarvis Activation System design provides a comprehensive, production-ready architecture for activating a voice assistant via hardware buttons across three platforms. The system is designed to be:

- **Fast:** <500ms activation latency
- **Efficient:** <2% daily battery impact
- **Reliable:** 99.9% success rate
- **Private:** No constant microphone listening
- **Scalable:** Ready for additional features

The implementation roadmap provides a clear 6-week path to full deployment, with testing and fallback mechanisms ensuring robust operation.

**Next Steps:**
1. Review and approve architecture
2. Set up Azure Speech Services
3. Begin Phase 1 implementation
4. Test iteratively on each platform

---

## References

### Documentation Sources

- [Apple Developer Documentation - Action Button](https://developer.apple.com/documentation/appintents/actionbutton)
- [Apple Support - Run shortcuts with Action button](https://support.apple.com/guide/shortcuts/run-shortcuts-with-the-action-button-apdfea15680b/ios)
- [GitHub - HotKey: Simple global shortcuts in macOS](https://github.com/soffes/HotKey)
- [Creating Launch Daemons and Agents - Apple Developer](https://developer.apple.com/library/archive/documentation/MacOSX/Conceptual/BPSystemStartup/Chapters/CreatingLaunchdJobs.html)
- [Meta Quest Controller Input and Tracking Overview](https://developers.meta.com/horizon/documentation/unity/unity-ovrinput/)
- [Meta XR SDKs - Input Overview](https://developers.meta.com/horizon/documentation/unity/unity-input-overview/)
- [Real-Time vs Turn-Based Voice Agent Architecture](https://softcery.com/lab/ai-voice-agents-real-time-vs-turn-based-tts-stt-architecture)
- [Engineering Low-Latency Voice Agents - Sierra AI](https://sierra.ai/blog/voice-latency)
- [Complete Guide to Wake Word Detection - Picovoice](https://picovoice.ai/blog/complete-guide-to-wake-word/)
- [iOS Background Audio Capabilities - Apple Developer Forums](https://developer.apple.com/forums/thread/106415)
- [macOS LaunchAgent Tutorial - launchd.info](https://www.launchd.info/)

---

**Document Version:** 1.0
**Last Updated:** February 5, 2026
**Author:** Claude (Trinity AI)
**Status:** ✅ Design Complete - Ready for Implementation
