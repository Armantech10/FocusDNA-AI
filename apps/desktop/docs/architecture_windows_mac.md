# FocusDNA Desktop Agent — Cross-Platform Architecture Specification (macOS & Windows)

This document specifies the software architecture for the FocusDNA Desktop Agent, highlighting how active application telemetry is captured on **macOS**, how **Windows** support will be seamlessly plugged in via the `PlatformTracker` interface abstraction, and how **Offline Event Queueing** ensures reliability without compromising user privacy.

---

## 1. Core Architecture & Platform Abstraction Layer

```
                          ┌──────────────────────────┐
                          │    Electron Main         │
                          │   (IPC & Queue Sync)     │
                          └─────────────┬────────────┘
                                        │
                         ┌──────────────┴─────────────┐
                         │  PlatformTracker Interface │
                         └──────────────┬─────────────┘
                                        │
                 ┌──────────────────────┴──────────────────────┐
                 │                                             │
      ┌──────────┴───────────┐                      ┌──────────┴───────────┐
      │   macOS Implementation│                      │ Windows Implementation│
      │  (NSWorkspace /      │                      │  (win32 User32.dll / │
      │   osascript)         │                      │   GetForegroundWindow)│
      └──────────────────────┘                      └──────────────────────┘
```

---

## 2. Platform Trackers Breakdown

### macOS Implementation (`src/tracking/macos_tracker.js`)
- **Native APIs**: Uses AppleScript (`osascript`) and `NSWorkspace.sharedWorkspace.frontmostApplication`.
- **Query Mechanism**:
  ```applescript
  tell application "System Events"
    set frontApp to name of first application process whose frontmost is true
    return frontApp
  end tell
  ```
- **Idle Detection**: Calls macOS `ioreg -c IOHIDSystem` to read `HIDIdleTime` (system-wide idle nanoseconds).

### Windows Implementation Spec (`src/tracking/windows_tracker.js`)
To add Windows support in future phases, implement the `PlatformTracker` interface using `ffi-napi` or PowerShell/C# helper binaries:
- **Active App Window API**:
  ```cpp
  HWND hwnd = GetForegroundWindow();
  DWORD processId;
  GetWindowThreadProcessId(hwnd, &processId);
  HANDLE hProcess = OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, FALSE, processId);
  WCHAR processName[MAX_PATH];
  QueryFullProcessImageNameW(hProcess, 0, processName, &dwSize);
  ```
- **Idle Detection**: Calls Windows `GetLastInputInfo` from `User32.dll` to query system idle time in milliseconds.

---

## 3. Privacy Safeguards & Data Collection Boundaries

| Data Field | Collection Status | Rationale |
| :--- | :---: | :--- |
| **Active Application Name** | ✅ **Collected** | Categorized into Work/Social/Entertainment telemetry. |
| **Event Timestamp & Duration** | ✅ **Collected** | Measures session time and fatigue windows. |
| **App Switching Count** | ✅ **Collected** | Measures cognitive fragmentation & context switching. |
| **System Idle Time** | ✅ **Collected** | Measures true active work duration. |
| ❌ **Keystrokes / Typing Content** | 🚫 **PROHIBITED** | Zero keylogger capabilities allowed. |
| ❌ **Passwords / Form Input** | 🚫 **PROHIBITED** | Strict privacy violation safeguard. |
| ❌ **Private Messages / Email Text** | 🚫 **PROHIBITED** | Content text is never inspected or transmitted. |
| ❌ **Screenshots by Default** | 🚫 **PROHIBITED** | Screen capture is disabled by default. |
| ❌ **Clipboard Contents** | 🚫 **PROHIBITED** | Clipboard access is completely blocked. |

---

## 4. Offline Queueing Architecture

1. **Local Queue File**: `apps/desktop/data/offline_queue.json`
2. **Network Interceptor**: Before sending batch telemetry to `POST /api/events`, the desktop agent pings the FastAPI backend `/health` endpoint.
3. **Offline Mode**: If network is disconnected or backend responds with HTTP 5xx:
   - Telemetry payload is serialized and appended to `offline_queue.json`.
   - Desktop UI updates status badge: `Offline (X items queued)`.
4. **Network Re-connection**:
   - Background timer checks connectivity every 30 seconds.
   - Upon reconnection, queued payloads are flushed sequentially to `POST /api/events` and cleared upon HTTP 201 receipt.
