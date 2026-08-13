# FocusDNA AI Security & Privacy Architecture Policy

This document details the security design, threat mitigations, privacy safeguards, and vulnerability disclosure process for the FocusDNA AI platform across the FastAPI backend, Next.js web application, Chrome Extension, and macOS Electron Desktop Agent.

---

## 1. Core Security Safeguards & Threat Mitigations

| Security Vector | Implementation Mechanism | Verification Status |
| :--- | :--- | :---: |
| **Authentication** | Supabase JWT Token verification via Bearer headers on FastAPI backend routes. | ✅ Verified |
| **Authorization & Tenant Isolation** | All SQL queries & in-memory database calls strictly filter by `user_id = current_user.id`. | ✅ Verified |
| **Supabase RLS Policies** | Row Level Security enabled on `focus_sessions`, `activity_events`, `user_profiles`, and `user_privacy`. | ✅ Verified |
| **Input Validation** | Pydantic model type & numeric range constraints on all FastAPI request payloads. | ✅ Verified |
| **CORS Configuration** | Restricted CORS middleware allowing explicit origins (`http://localhost:3000`, `http://127.0.0.1:3000`). | ✅ Verified |
| **Rate Limiting** | Sliding window rate limiters (e.g. max 10 requests/min per user on AI recommendation routes). | ✅ Verified |
| **Secrets Management** | `GEMINI_API_KEY` and database credentials stored exclusively in server environment variables (`.env`). | ✅ Verified |
| **SQL Injection Defense** | Parameterized query execution via Supabase ORM / SQLAlchemy. Zero raw SQL string concatenation. | ✅ Verified |
| **XSS Defense** | React JSX automatic HTML string escaping. Strict Content-Security-Policy (CSP) headers. | ✅ Verified |
| **CSRF Defense** | Session cookies set with `SameSite=Lax`. Authorization header API tokens. | ✅ Verified |
| **Chrome Extension Security** | Minimum manifest permissions (`activeTab`, `storage`, `alarms`). Zero host permissions for private pages. | ✅ Verified |
| **Electron Desktop Security** | `contextIsolation: true`, `nodeIntegration: false`, secure ContextBridge IPC handlers. | ✅ Verified |

---

## 2. Supabase Row-Level Security (RLS) Policy Specifications

```sql
-- 1. Enable RLS on focus_sessions
ALTER TABLE focus_sessions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can only read their own focus_sessions"
  ON focus_sessions FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can only insert their own focus_sessions"
  ON focus_sessions FOR INSERT
  WITH CHECK (auth.uid() = user_id);

-- 2. Enable RLS on activity_events
ALTER TABLE activity_events ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can only read their own activity_events"
  ON activity_events FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can only insert their own activity_events"
  ON activity_events FOR INSERT
  WITH CHECK (auth.uid() = user_id);
```

---

## 3. Truthful Telemetry Disclosure

### What FocusDNA Collects (Metadata Only):
- Active application name & domain name (e.g., "Xcode", "github.com")
- Session start time, end time, and duration
- App & browser switch counts per 5-minute window
- System idle duration (seconds)

### What FocusDNA STRICTLY PROHIBITS (Never Collected):
- 🚫 **Passwords / Form Credentials**: Zero form input capturing.
- 🚫 **Keystrokes / Typing Content**: Zero keylogger code.
- 🚫 **Private Message Content**: Emails, Slack text, and chat messages are never read.
- 🚫 **Screenshots by Default**: Zero screen capture code.
- 🚫 **Clipboard Content**: Zero clipboard access.

---

## 4. User Privacy Rights Implementation

- **Export My Data**: Endpoint `GET /api/privacy/export` downloads complete JSON dump of user data.
- **Delete My Data**: Endpoint `POST /api/privacy/purge` permanently deletes all user activity records and sessions.
- **Pause Tracking**: Endpoint `PUT /api/privacy` toggles telemetry tracking pause state.
- **Revoke Consent**: Endpoint `POST /api/privacy/revoke` revokes tracking consent and clears active session cookies.

---

## 5. Vulnerability Disclosure Policy

If you discover a security vulnerability within FocusDNA AI, please report it directly to:
**`security@focusdna.ai`**

Reports receive an initial response within 24 hours. Please include step-by-step reproduction instructions.
