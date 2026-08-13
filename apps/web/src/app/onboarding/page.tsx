'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { supabase } from '@/lib/supabase/client';
import { getApiUrl } from '@/lib/api';
import { ShieldCheck, CheckCircle2, Globe, User, Clock, ArrowRight, Shield } from 'lucide-react';

export default function OnboardingPage() {
  const router = useRouter();
  const [displayName, setDisplayName] = useState('');
  const [timezone, setTimezone] = useState('UTC');
  const [trackingConsent, setTrackingConsent] = useState(true);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // Detect system timezone automatically
    try {
      const userTz = Intl.DateTimeFormat().resolvedOptions().timeZone;
      if (userTz) setTimezone(userTz);
    } catch (e) {
      // Fallback to UTC
    }

    // Load current user profile if available
    supabase.auth.getUser().then(({ data: { user } }) => {
      if (user?.user_metadata?.full_name) {
        setDisplayName(user.user_metadata.full_name);
      }
    });
  }, []);

  const handleCompleteOnboarding = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const { data: { user } } = await supabase.auth.getUser();

      if (user) {
        // Save onboarding details to Supabase profiles
        await supabase.from('profiles').upsert({
          id: user.id,
          email: user.email,
          display_name: displayName,
          timezone: timezone,
        });

        await supabase.from('privacy_settings').upsert({
          user_id: user.id,
          is_tracking_paused: !trackingConsent,
        });
      }

      // Also notify FastAPI backend
      try {
        const { data: { session } } = await supabase.auth.getSession();
        if (session) {
          await fetch(getApiUrl('/api/onboarding'), {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${session.access_token}`
            },
            body: JSON.stringify({
              display_name: displayName,
              timezone: timezone,
              tracking_consent: trackingConsent
            })
          });
        }
      } catch (err) {
        // FastAPI sync optional for fallback
      }

      router.push('/dashboard');
    } catch (err) {
      router.push('/dashboard');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto p-8 space-y-8 my-10">
      <div className="text-center space-y-3">
        <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 text-xs font-semibold">
          <ShieldCheck className="h-4 w-4" />
          <span>User Setup & Privacy Consent</span>
        </div>
        <h1 className="text-4xl font-extrabold text-white">Welcome to FocusDNA AI</h1>
        <p className="text-base text-gray-400 max-w-xl mx-auto">
          Please configure your display preferences and review your data collection scope before launching your dashboard.
        </p>
      </div>

      <form onSubmit={handleCompleteOnboarding} className="space-y-6">
        <div className="p-6 rounded-3xl glass-panel border border-border/80 space-y-6">
          <div className="space-y-2">
            <label className="text-xs font-semibold text-gray-300 flex items-center gap-2">
              <User className="h-4 w-4 text-primary" />
              <span>Display Name</span>
            </label>
            <input
              type="text"
              required
              value={displayName}
              onChange={(e) => setDisplayName(e.target.value)}
              placeholder="Your Preferred Name"
              className="w-full px-4 py-3 rounded-xl bg-gray-900/80 border border-gray-800 text-sm text-white focus:outline-none focus:border-primary transition-colors"
            />
          </div>

          <div className="space-y-2">
            <label className="text-xs font-semibold text-gray-300 flex items-center gap-2">
              <Clock className="h-4 w-4 text-cyan-400" />
              <span>Primary Timezone</span>
            </label>
            <select
              value={timezone}
              onChange={(e) => setTimezone(e.target.value)}
              className="w-full px-4 py-3 rounded-xl bg-gray-900/80 border border-gray-800 text-sm text-white focus:outline-none focus:border-primary transition-colors"
            >
              <option value="UTC">UTC (Coordinated Universal Time)</option>
              <option value="America/New_York">America/New_York (Eastern Time)</option>
              <option value="America/Chicago">America/Chicago (Central Time)</option>
              <option value="America/Los_Angeles">America/Los_Angeles (Pacific Time)</option>
              <option value="Europe/London">Europe/London (GMT/BST)</option>
              <option value="Asia/Tokyo">Asia/Tokyo (JST)</option>
              <option value="Asia/Kolkata">Asia/Kolkata (IST)</option>
            </select>
          </div>

          <div className="pt-2 space-y-3">
            <div className="flex items-center justify-between p-4 rounded-2xl bg-gray-900/60 border border-gray-800">
              <div className="space-y-1">
                <div className="text-sm font-bold text-white flex items-center gap-2">
                  <Globe className="h-4 w-4 text-emerald-400" />
                  <span>Enable Digital Activity Telemetry</span>
                </div>
                <p className="text-xs text-gray-400">
                  Allows collection of application context switches and web domain metadata.
                </p>
              </div>

              <input
                type="checkbox"
                checked={trackingConsent}
                onChange={(e) => setTrackingConsent(e.target.checked)}
                className="h-5 w-5 rounded border-gray-800 bg-gray-900 text-primary focus:ring-primary accent-primary"
              />
            </div>
          </div>
        </div>

        {/* Privacy Explanation Box */}
        <div className="p-6 rounded-3xl glass-panel border border-border/80 space-y-4">
          <h3 className="font-bold text-white text-base flex items-center gap-2">
            <Shield className="h-5 w-5 text-emerald-400" />
            <span>Explicit Zero-Keystroke Data Guarantee</span>
          </h3>
          <ul className="space-y-2 text-xs text-gray-300 leading-relaxed">
            <li className="flex items-start gap-2">
              <CheckCircle2 className="h-4 w-4 text-emerald-400 shrink-0 mt-0.5" />
              <span><strong>NO Typed Text:</strong> FocusDNA AI measures typing speed level, NEVER actual typed text or keystroke values.</span>
            </li>
            <li className="flex items-start gap-2">
              <CheckCircle2 className="h-4 w-4 text-emerald-400 shrink-0 mt-0.5" />
              <span><strong>NO Private Content:</strong> Message bodies, emails, passwords, and private chats are completely excluded.</span>
            </li>
            <li className="flex items-start gap-2">
              <CheckCircle2 className="h-4 w-4 text-emerald-400 shrink-0 mt-0.5" />
              <span><strong>Full User Sovereignty:</strong> You can pause tracking or delete all your data at any time in Privacy Settings.</span>
            </li>
          </ul>
        </div>

        <div className="flex justify-center pt-2">
          <button
            type="submit"
            disabled={loading}
            className="inline-flex items-center gap-2 px-8 py-4 rounded-2xl bg-primary text-white font-bold shadow-xl shadow-primary/30 hover:bg-primary-hover transition-all"
          >
            <span>{loading ? 'Saving Setup...' : 'Complete Onboarding & Open Dashboard'}</span>
            <ArrowRight className="h-5 w-5" />
          </button>
        </div>
      </form>
    </div>
  );
}
