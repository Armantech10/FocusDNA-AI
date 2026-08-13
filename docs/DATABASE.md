# FocusDNA AI — Supabase Database Documentation

This document specifies the PostgreSQL database schema and Row-Level Security (RLS) policies managed via Supabase.

---

## 1. Relational Schema Architecture

```
                    ┌─────────────────────────┐
                    │      user_profiles      │
                    ├─────────────────────────┤
                    │ PK  user_id (UUID/TEXT) │
                    │     email               │
                    │     display_name        │
                    │     timezone            │
                    └────────────┬────────────┘
                                 │ 1
                                 │
                   ┌─────────────┴──────────────┐
                   │                            │
                   ▼ N                          ▼ N
       ┌───────────────────────┐   ┌──────────────────────────┐
       │    focus_sessions     │   │     activity_events      │
       ├───────────────────────┤   ├──────────────────────────┤
       │ PK  id (UUID)         │   │ PK  id (UUID)            │
       │ FK  user_id (TEXT)    │   │ FK  user_id (TEXT)       │
       │     session_name      │   │     application_name     │
       │     planned_duration  │   │     website_domain       │
       │     actual_duration   │   │     category             │
       │     status            │   │     session_duration     │
       │     distraction_count │   │     app_switch_count     │
       │     started_at        │   │     idle_seconds         │
       └───────────────────────┘   └──────────────────────────┘
```

---

## 2. Table Specifications

### A. `focus_sessions` Table
Stores pomodoro and focus session metadata.

| Column | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | PRIMARY KEY, DEFAULT `gen_random_uuid()` | Unique session identifier |
| `user_id` | `TEXT` | NOT NULL | Owner user ID (Supabase Auth UID) |
| `session_name` | `TEXT` | NOT NULL | Human-readable session title |
| `planned_duration_minutes` | `INT` | NOT NULL | Targeted session duration |
| `actual_duration_minutes` | `INT` | DEFAULT `0` | Elapsed duration completed |
| `status` | `TEXT` | DEFAULT `'active'` | Status (`active`, `completed`, `cancelled`) |
| `distraction_count` | `INT` | DEFAULT `0` | Total distraction alerts triggered |
| `app_switch_count` | `INT` | DEFAULT `0` | Process context switches during session |
| `started_at` | `TIMESTAMPTZ` | DEFAULT `NOW()` | Session start timestamp |
| `completed_at` | `TIMESTAMPTZ` | NULLABLE | Session completion timestamp |

---

### B. `activity_events` Table
Stores 5-minute aggregated activity telemetry window metadata.

| Column | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | PRIMARY KEY, DEFAULT `gen_random_uuid()` | Unique event identifier |
| `user_id` | `TEXT` | NOT NULL | Owner user ID |
| `application_name` | `TEXT` | NULLABLE | Active application process name (e.g. `Xcode`) |
| `website_domain` | `TEXT` | NULLABLE | Active domain category (e.g. `github.com`) |
| `category` | `TEXT` | NULLABLE | Categorized activity type (`Work`, `Social`, etc.) |
| `session_duration` | `INT` | DEFAULT `0` | Telemetry window duration (seconds) |
| `app_switch_count` | `INT` | DEFAULT `0` | App switches during window |
| `browser_switch_count` | `INT` | DEFAULT `0` | Browser tab switches during window |
| `idle_seconds` | `INT` | DEFAULT `0` | System idle seconds |
| `timestamp` | `TIMESTAMPTZ` | DEFAULT `NOW()` | Telemetry timestamp |

---

## 3. Supabase Row-Level Security (RLS) Policies

Row-Level Security (RLS) guarantees complete tenant data isolation. Users can **ONLY** view or modify records where `auth.uid() = user_id`.

```sql
-- 1. Enable RLS on focus_sessions
ALTER TABLE public.focus_sessions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can only read their own focus_sessions"
  ON public.focus_sessions FOR SELECT
  USING (auth.uid()::text = user_id);

CREATE POLICY "Users can only insert their own focus_sessions"
  ON public.focus_sessions FOR INSERT
  WITH CHECK (auth.uid()::text = user_id);

-- 2. Enable RLS on activity_events
ALTER TABLE public.activity_events ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can only read their own activity_events"
  ON public.activity_events FOR SELECT
  USING (auth.uid()::text = user_id);

CREATE POLICY "Users can only insert their own activity_events"
  ON public.activity_events FOR INSERT
  WITH CHECK (auth.uid()::text = user_id);
```
