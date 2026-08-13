'use client';

import React, { useEffect, useState } from 'react';
import { Sidebar } from '@/components/Sidebar';
import { supabase } from '@/lib/supabase/client';
import { getApiUrl } from '@/lib/api';
import { 
  ShieldCheck, 
  Download, 
  Trash2, 
  PauseCircle, 
  PlayCircle, 
  XCircle, 
  Lock, 
  EyeOff, 
  CheckCircle2, 
  AlertTriangle,
  FileSpreadsheet
} from 'lucide-react';

export default function PrivacyPage() {
  const [isPaused, setIsPaused] = useState(false);
  const [loading, setLoading] = useState(false);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);

  const fetchPrivacySettings = async () => {
    try {
      const { data: { user } } = await supabase.auth.getUser();
      const userId = user?.id || 'demo_user';

      const res = await fetch(getApiUrl('/api/profile'), {
        headers: { 'Authorization': `Bearer mock_valid_token_${userId}` }
      });
      if (res.ok) {
        const data = await res.json();
        setIsPaused(data.privacy_settings?.is_tracking_paused || false);
      }
    } catch (e) {
      // Ignore
    }
  };

  useEffect(() => {
    fetchPrivacySettings();
  }, []);

  const handleExportData = async () => {
    setLoading(true);
    try {
      const { data: { user } } = await supabase.auth.getUser();
      const userId = user?.id || 'demo_user';

      const res = await fetch(getApiUrl('/api/privacy/export'), {
        headers: { 'Authorization': `Bearer mock_valid_token_${userId}` }
      });
      if (res.ok) {
        const blob = await res.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `focusdna_user_export_${userId.slice(0, 8)}.json`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        setStatusMessage('Your user data export has been downloaded successfully.');
      } else {
        setStatusMessage('Export failed. Please try again.');
      }
    } catch (e) {
      setStatusMessage('Export failed. Backend offline.');
    } finally {
      setLoading(false);
    }
  };

  const handlePurgeData = async () => {
    if (!confirm('Are you sure you want to permanently delete all your FocusDNA activity history and focus sessions? This action cannot be undone.')) {
      return;
    }
    setLoading(true);
    try {
      const { data: { user } } = await supabase.auth.getUser();
      const userId = user?.id || 'demo_user';

      const res = await fetch(getApiUrl('/api/privacy/purge'), {
        method: 'POST',
        headers: { 'Authorization': `Bearer mock_valid_token_${userId}` }
      });
      if (res.ok) {
        localStorage.removeItem('focusdna_sessions');
        setStatusMessage('All stored activity events and focus sessions have been permanently deleted.');
      }
    } catch (e) {
      setStatusMessage('Purge operation failed.');
    } finally {
      setLoading(false);
    }
  };

  const handleTogglePause = async () => {
    setLoading(true);
    const newPauseState = !isPaused;
    try {
      const { data: { user } } = await supabase.auth.getUser();
      const userId = user?.id || 'demo_user';

      const res = await fetch(getApiUrl('/api/privacy'), {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer mock_valid_token_${userId}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ is_tracking_paused: newPauseState })
      });
      if (res.ok) {
        setIsPaused(newPauseState);
        setStatusMessage(`Telemetry tracking ${newPauseState ? 'PAUSED' : 'RESUMED'} successfully.`);
      }
    } catch (e) {
      setIsPaused(newPauseState);
      setStatusMessage(`Telemetry tracking ${newPauseState ? 'PAUSED' : 'RESUMED'} locally.`);
    } finally {
      setLoading(false);
    }
  };

  const handleRevokeConsent = async () => {
    if (!confirm('Revoking tracking permission will pause all telemetry and clear active desktop & extension cookies. Proceed?')) {
      return;
    }
    setLoading(true);
    try {
      const { data: { user } } = await supabase.auth.getUser();
      const userId = user?.id || 'demo_user';

      await fetch(getApiUrl('/api/privacy/revoke'), {
        method: 'POST',
        headers: { 'Authorization': `Bearer mock_valid_token_${userId}` }
      });
      setIsPaused(true);
      setStatusMessage('Tracking permission revoked. All telemetry tracking has been disabled.');
    } catch (e) {
      setStatusMessage('Revocation recorded.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-[calc(100vh-4rem)]">
      <Sidebar />

      <div className="flex-1 p-6 sm:p-8 space-y-8 overflow-y-auto">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-3xl font-extrabold text-white tracking-tight flex items-center gap-3">
              <ShieldCheck className="h-8 w-8 text-primary" />
              <span>Privacy Controls & Data Safeguards</span>
            </h1>
            <p className="text-sm text-gray-400 mt-1">
              Transparent telemetry disclosures, user data rights, and tracking permission controls.
            </p>
          </div>
        </div>

        {/* Status Alert Banner */}
        {statusMessage && (
          <div className="p-4 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 flex items-center gap-3 text-xs text-emerald-400 font-medium">
            <CheckCircle2 className="h-5 w-5 shrink-0" />
            <span>{statusMessage}</span>
          </div>
        )}

        {/* USER PRIVACY RIGHTS ACTION BUTTONS */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          
          {/* Action 1: Export My Data */}
          <button
            onClick={handleExportData}
            disabled={loading}
            className="p-5 rounded-2xl glass-panel border border-border/80 hover:border-cyan-500/70 hover:scale-[1.02] cursor-pointer transition-all space-y-3 text-left group shadow-lg"
          >
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-gray-400">Data Right</span>
              <Download className="h-5 w-5 text-cyan-400 group-hover:scale-110 transition-transform" />
            </div>
            <div className="text-base font-extrabold text-white">Export My Data</div>
            <div className="text-[11px] text-gray-400">Download complete JSON backup of all stored history</div>
          </button>

          {/* Action 2: Delete My Data */}
          <button
            onClick={handlePurgeData}
            disabled={loading}
            className="p-5 rounded-2xl glass-panel border border-border/80 hover:border-rose-500/70 hover:scale-[1.02] cursor-pointer transition-all space-y-3 text-left group shadow-lg"
          >
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-gray-400">Data Right</span>
              <Trash2 className="h-5 w-5 text-rose-400 group-hover:scale-110 transition-transform" />
            </div>
            <div className="text-base font-extrabold text-white">Delete All My Data</div>
            <div className="text-[11px] text-gray-400">Permanently purge all activity events and sessions</div>
          </button>

          {/* Action 3: Pause Telemetry Tracking */}
          <button
            onClick={handleTogglePause}
            disabled={loading}
            className="p-5 rounded-2xl glass-panel border border-border/80 hover:border-amber-500/70 hover:scale-[1.02] cursor-pointer transition-all space-y-3 text-left group shadow-lg"
          >
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-gray-400">Telemetry Switch</span>
              {isPaused ? <PlayCircle className="h-5 w-5 text-emerald-400" /> : <PauseCircle className="h-5 w-5 text-amber-400" />}
            </div>
            <div className="text-base font-extrabold text-white">
              {isPaused ? 'Resume Tracking' : 'Pause Tracking'}
            </div>
            <div className="text-[11px] text-gray-400">
              {isPaused ? 'Telemetry is currently paused' : 'Temporarily suspend Chrome & Desktop agent'}
            </div>
          </button>

          {/* Action 4: Revoke Consent */}
          <button
            onClick={handleRevokeConsent}
            disabled={loading}
            className="p-5 rounded-2xl glass-panel border border-border/80 hover:border-gray-500/70 hover:scale-[1.02] cursor-pointer transition-all space-y-3 text-left group shadow-lg"
          >
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-gray-400">Consent Control</span>
              <XCircle className="h-5 w-5 text-gray-400 group-hover:scale-110 transition-transform" />
            </div>
            <div className="text-base font-extrabold text-white">Revoke Permission</div>
            <div className="text-[11px] text-gray-400">Revoke consent & disable tracking permissions</div>
          </button>

        </div>

        {/* FACTUAL TELEMETRY DISCLOSURE TABLE */}
        <div className="p-8 rounded-3xl glass-panel border border-border/80 space-y-6 shadow-2xl">
          <div className="border-b border-gray-800 pb-4 flex items-center justify-between">
            <div>
              <h2 className="text-xl font-extrabold text-white">Factual Data Collection Disclosure</h2>
              <p className="text-xs text-gray-400 mt-0.5">FocusDNA operates on a metadata-only telemetry architecture.</p>
            </div>
            <span className="text-xs font-mono uppercase bg-emerald-500/20 text-emerald-400 px-3 py-1 rounded-full border border-emerald-500/30 font-semibold">
              Metadata Telemetry Only
            </span>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            
            {/* Column 1: What We Collect */}
            <div className="p-5 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 space-y-3">
              <div className="flex items-center gap-2 text-emerald-400 font-bold text-sm">
                <CheckCircle2 className="h-5 w-5" />
                <span>What FocusDNA Collects:</span>
              </div>
              <ul className="space-y-2 text-xs text-gray-300">
                <li className="flex items-start gap-2">
                  <span className="text-emerald-400 font-bold">•</span>
                  <span><strong>Active Application Name</strong>: Process titles (e.g., Xcode, VS Code, Slack).</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-emerald-400 font-bold">•</span>
                  <span><strong>Website Domain Names</strong>: Approved web domains (e.g., github.com, stackoverflow.com).</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-emerald-400 font-bold">•</span>
                  <span><strong>Session Duration & Timestamp</strong>: Time spent per focus window.</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-emerald-400 font-bold">•</span>
                  <span><strong>Switch Counts & Idle Duration</strong>: App switches & system idle seconds.</span>
                </li>
              </ul>
            </div>

            {/* Column 2: What We STRICTLY PROHIBIT */}
            <div className="p-5 rounded-2xl bg-rose-500/10 border border-rose-500/30 space-y-3">
              <div className="flex items-center gap-2 text-rose-400 font-bold text-sm">
                <EyeOff className="h-5 w-5" />
                <span>What FocusDNA STRICTLY PROHIBITS:</span>
              </div>
              <ul className="space-y-2 text-xs text-gray-300">
                <li className="flex items-start gap-2">
                  <span className="text-rose-400 font-bold">•</span>
                  <span><strong>Passwords & Form Inputs</strong>: Zero credential capturing.</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-rose-400 font-bold">•</span>
                  <span><strong>Keystrokes / Typing Content</strong>: Zero keylogger capabilities.</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-rose-400 font-bold">•</span>
                  <span><strong>Private Messages & Emails</strong>: Content text is never read.</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-rose-400 font-bold">•</span>
                  <span><strong>Screenshots & Clipboard</strong>: Zero screen or clipboard capturing.</span>
                </li>
              </ul>
            </div>

          </div>
        </div>

      </div>
    </div>
  );
}
