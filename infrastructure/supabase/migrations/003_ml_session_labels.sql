-- =======================================================
-- FocusDNA AI Database Schema & Row Level Security (RLS)
-- Supabase PostgreSQL Migration 003 — Real Session Labels
-- =======================================================

CREATE TABLE IF NOT EXISTS public.ml_session_labels (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    focus_session_id TEXT NOT NULL,
    user_rating INT NOT NULL CHECK (user_rating BETWEEN 1 AND 5),
    rating_label TEXT NOT NULL CHECK (rating_label IN ('very_focused', 'mostly_focused', 'neutral', 'distracted', 'very_distracted')),
    binary_target INT NOT NULL CHECK (binary_target IN (0, 1)), -- 0 = Focused, 1 = Distracted/Attention Loss
    label_source TEXT DEFAULT 'user_session_rating',
    feature_schema_version TEXT DEFAULT '1.0',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT unique_user_focus_session UNIQUE (user_id, focus_session_id)
);

-- Index for fast user & session query lookups
CREATE INDEX IF NOT EXISTS idx_ml_session_labels_user_id ON public.ml_session_labels(user_id);
CREATE INDEX IF NOT EXISTS idx_ml_session_labels_session_id ON public.ml_session_labels(focus_session_id);

-- Enable Row Level Security
ALTER TABLE public.ml_session_labels ENABLE ROW LEVEL SECURITY;

-- RLS Policies (User Isolation)
CREATE POLICY "Users can insert their own session labels"
    ON public.ml_session_labels FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can select their own session labels"
    ON public.ml_session_labels FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can update their own session labels"
    ON public.ml_session_labels FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own session labels"
    ON public.ml_session_labels FOR DELETE
    USING (auth.uid() = user_id);
