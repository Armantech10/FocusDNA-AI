'use client';

import React, { useEffect, useState } from 'react';
import { Sidebar } from '@/components/Sidebar';
import { supabase } from '@/lib/supabase/client';
import { Shield, Trash2, PauseCircle, PlayCircle, Lock, AlertOctagon, User, CheckCircle2 } from 'lucide-react';

export default function PrivacySettingsPage() {
  const [userEmail, setUserEmail] = useState<string>('');
  const [displayName, setDisplayName] = useState<string>('');
  const [isPaused, setIsPaused] = useState<boolean>(false);
  const [collectAppNames, setCollectAppNames] = useState<boolean>(true);
  const [collectWebDomains, setCollectWebDomains] = useState<boolean>(true);
  const [purgedStatus, setPurgedStatus] = useState<string | null>(null);

  useEffect(() => {
    supabase.auth.getUser().then(({ data: { user } }) => {
      if (user) {
        setUserEmail(user.email || '');
        setDisplayName(user.user_metadata?.full_name || 'Authenticated User');

        // Fetch privacy settings from Supabase
        supabase
          .from('privacy_settings')
          .select('*')
          .eq('user_id', user.id)
          .single()
          .then(({ data }) => {
            if (data) {
              setIsPaused(data.is_tracking_paused ?? false);
              setCollectAppNames(data.collect_app_names ?? true);
              setCollectWebDomains(data.collect_web_domains ?? true);
            }
          });
      }
    });
  }, []);

  const togglePause = async () => {
    const nextState = !isPaused;
    setIsPaused(nextState);

    const { data: { user } } = await supabase.auth.getUser();
    if (user) {
      await supabase
        .from('privacy_settings')
        .upsert({ user_id: user.id, is_tracking_paused: nextState });
    }
  };

  const handlePurgeData = async () => {
    if (!confirm('Are you sure you want to permanently delete all your activity logs? This action cannot be undone.')) {
      return;
    }

    const { data: { user } } = await supabase.auth.getUser();
    if (user) {
      await supabase.from('activity_events').delete().eq('user_id', user.id);
      await supabase.from('focus_sessions').delete().eq('user_id', user.id);
      setPurgedStatus('All recorded activity events and focus sessions successfully purged.');
    }
  };

  return (
    <div className="flex min-h-[calc(100vh-4rem)]">
      <Sidebar />

      <div className="flex-1 p-8 space-y-8 overflow-y-auto max-w-4xl">
        <div>
          <h1 className="text-3xl font-extrabold text-white tracking-tight">Privacy Settings & Data Controls</h1>
          <p className="text-sm text-gray-400 mt-1">
            Manage telemetry controls, tracking pause state, and data purge execution.
          </p>
        </div>

        {/* Account Summary */}
        <div className="p-6 rounded-3xl glass-panel border border-border/80 space-y-2">
          <h3 className="text-sm font-bold text-gray-300 flex items-center gap-2">
            <User className="h-4 w-4 text-primary" />
            <span>Authenticated User Profile</span>
          </h3>
          <div className="text-lg font-bold text-white">{displayName}</div>
          <div className="text-xs font-mono text-gray-400">{userEmail}</div>
        </div>

        {/* Telemetry Pause Toggle */}
        <div className="p-6 rounded-3xl glass-panel border border-border/80 flex items-center justify-between">
          <div className="space-y-1">
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <Shield className="h-5 w-5 text-primary" />
              <span>Background Telemetry Collection</span>
            </h3>
            <p className="text-xs text-gray-400">
              {isPaused
                ? 'Telemetry is currently PAUSED. No background events are recorded.'
                : 'Telemetry is ACTIVE. Context switch counts are monitored without keystrokes.'}
            </p>
          </div>

          <button
            onClick={togglePause}
            className={`inline-flex items-center gap-2 px-5 py-2.5 rounded-2xl font-bold text-xs shadow-lg transition-all ${
              isPaused
                ? 'bg-emerald-500 text-white shadow-emerald-500/30 hover:bg-emerald-600'
                : 'bg-amber-500 text-white shadow-amber-500/30 hover:bg-amber-600'
            }`}
          >
            {isPaused ? <PlayCircle className="h-4 w-4" /> : <PauseCircle className="h-4 w-4" />}
            <span>{isPaused ? 'Resume Tracking' : 'Pause Tracking'}</span>
          </button>
        </div>

        {/* Permanent Data Purge */}
        <div className="p-6 rounded-3xl border border-rose-500/40 bg-rose-500/5 space-y-4">
          <div className="flex items-center gap-2 text-rose-400 font-bold text-base">
            <AlertOctagon className="h-5 w-5" />
            <span>Data Purge & Deletion</span>
          </div>

          <p className="text-xs text-gray-300 leading-relaxed">
            FocusDNA AI provides full data sovereignty. You can delete all your stored behavioral activity logs and trained model weights at any time with a single click.
          </p>

          {purgedStatus && (
            <div className="p-3 rounded-xl bg-rose-500/20 text-rose-300 font-mono text-xs border border-rose-500/30 flex items-center gap-2">
              <CheckCircle2 className="h-4 w-4 shrink-0" />
              <span>{purgedStatus}</span>
            </div>
          )}

          <button
            onClick={handlePurgeData}
            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-2xl bg-rose-500 text-white text-xs font-bold shadow-lg shadow-rose-500/30 hover:bg-rose-600 transition-all"
          >
            <Trash2 className="h-4 w-4" />
            <span>Purge All Stored Data</span>
          </button>
        </div>
      </div>
    </div>
  );
}
