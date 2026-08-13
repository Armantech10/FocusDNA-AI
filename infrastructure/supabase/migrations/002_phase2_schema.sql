-- =======================================================
-- FocusDNA AI Database Schema & Row Level Security (RLS)
-- Supabase PostgreSQL Migration 002
-- =======================================================

-- Enable UUID Extension if not already present
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Profiles Table
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT UNIQUE NOT NULL,
    display_name TEXT,
    timezone TEXT DEFAULT 'UTC',
    avatar_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Privacy Settings Table
CREATE TABLE IF NOT EXISTS public.privacy_settings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID UNIQUE NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    is_tracking_paused BOOLEAN DEFAULT FALSE,
    collect_app_names BOOLEAN DEFAULT TRUE,
    collect_web_domains BOOLEAN DEFAULT TRUE,
    collect_typing_speed BOOLEAN DEFAULT TRUE,
    auto_purge_days INT DEFAULT 90,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Focus Sessions Table
CREATE TABLE IF NOT EXISTS public.focus_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    session_name TEXT DEFAULT 'Focus Session',
    target_duration_minutes INT NOT NULL,
    actual_duration_minutes INT DEFAULT 0,
    status TEXT DEFAULT 'active', -- active, completed, interrupted, abandoned
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ended_at TIMESTAMPTZ,
    distraction_count INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. Activity Events Table (Strictly NO raw text or keystrokes stored)
CREATE TABLE IF NOT EXISTS public.activity_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    application_name TEXT,
    website_domain TEXT,
    session_duration INT DEFAULT 0,
    app_switch_count INT DEFAULT 0,
    browser_switch_count INT DEFAULT 0,
    notification_count INT DEFAULT 0,
    idle_seconds INT DEFAULT 0,
    typing_activity_level TEXT DEFAULT 'low',
    device_type TEXT DEFAULT 'desktop',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. Distraction Events Table
CREATE TABLE IF NOT EXISTS public.distraction_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    focus_session_id UUID REFERENCES public.focus_sessions(id) ON DELETE SET NULL,
    trigger_type TEXT NOT NULL,
    source_name TEXT,
    severity TEXT DEFAULT 'medium',
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

-- 6. Focus Scores Table
CREATE TABLE IF NOT EXISTS public.focus_scores (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    score_value FLOAT NOT NULL CHECK (score_value >= 0 AND score_value <= 100),
    evaluation_type TEXT NOT NULL DEFAULT 'heuristic',
    factors_breakdown JSONB DEFAULT '{}'::jsonb,
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

-- 7. ML Features Table
CREATE TABLE IF NOT EXISTS public.ml_features (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    window_start TIMESTAMPTZ NOT NULL,
    window_end TIMESTAMPTZ NOT NULL,
    app_switch_density FLOAT NOT NULL,
    social_media_ratio FLOAT NOT NULL,
    idle_ratio FLOAT NOT NULL,
    notification_density FLOAT NOT NULL,
    typing_variance FLOAT NOT NULL,
    context_switch_frequency FLOAT NOT NULL,
    target_label INT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 8. ML Predictions Table
CREATE TABLE IF NOT EXISTS public.ml_predictions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    model_name TEXT NOT NULL,
    model_version TEXT NOT NULL DEFAULT '1.0.0',
    predicted_label INT NOT NULL,
    probability FLOAT NOT NULL,
    is_anomaly BOOLEAN DEFAULT FALSE,
    anomaly_score FLOAT,
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

-- 9. User Feedback Table
CREATE TABLE IF NOT EXISTS public.user_feedback (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    target_type TEXT NOT NULL,
    target_id UUID NOT NULL,
    rating INT CHECK (rating >= 1 AND rating <= 5),
    was_accurate BOOLEAN,
    feedback_notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 10. AI Recommendations Table
CREATE TABLE IF NOT EXISTS public.ai_recommendations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    trigger_reason TEXT NOT NULL,
    action_type TEXT DEFAULT 'behavioral_nudge',
    applied_status BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Temporal Query Indexing
CREATE INDEX IF NOT EXISTS idx_activity_events_user ON public.activity_events(user_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_focus_scores_user ON public.focus_scores(user_id, timestamp DESC);

-- =======================================================
-- Row Level Security (RLS) Configuration
-- Strictly enforces auth.uid() = user_id for isolation
-- =======================================================

ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.privacy_settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.focus_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.activity_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.distraction_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.focus_scores ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.ml_features ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.ml_predictions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_feedback ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.ai_recommendations ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if re-running
DROP POLICY IF EXISTS "User isolated profile access" ON public.profiles;
DROP POLICY IF EXISTS "User isolated privacy access" ON public.privacy_settings;
DROP POLICY IF EXISTS "User isolated sessions access" ON public.focus_sessions;
DROP POLICY IF EXISTS "User isolated activity access" ON public.activity_events;
DROP POLICY IF EXISTS "User isolated distraction access" ON public.distraction_events;
DROP POLICY IF EXISTS "User isolated scores access" ON public.focus_scores;
DROP POLICY IF EXISTS "User isolated ml features access" ON public.ml_features;
DROP POLICY IF EXISTS "User isolated ml predictions access" ON public.ml_predictions;
DROP POLICY IF EXISTS "User isolated feedback access" ON public.user_feedback;
DROP POLICY IF EXISTS "User isolated recommendations access" ON public.ai_recommendations;

-- User Isolation Policies
CREATE POLICY "User isolated profile access" ON public.profiles FOR ALL USING (auth.uid() = id);
CREATE POLICY "User isolated privacy access" ON public.privacy_settings FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "User isolated sessions access" ON public.focus_sessions FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "User isolated activity access" ON public.activity_events FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "User isolated distraction access" ON public.distraction_events FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "User isolated scores access" ON public.focus_scores FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "User isolated ml features access" ON public.ml_features FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "User isolated ml predictions access" ON public.ml_predictions FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "User isolated feedback access" ON public.user_feedback FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "User isolated recommendations access" ON public.ai_recommendations FOR ALL USING (auth.uid() = user_id);

-- Automatic Profile Creation Trigger on Auth Signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.profiles (id, email, display_name)
  VALUES (new.id, new.email, new.raw_user_meta_data->>'full_name');

  INSERT INTO public.privacy_settings (user_id)
  VALUES (new.id);

  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE PROCEDURE public.handle_new_user();
