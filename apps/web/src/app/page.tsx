'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { supabase } from '@/lib/supabase/client';
import { Zap, ArrowRight, ShieldCheck, LayoutDashboard, Lock, Mail, Sparkles, CheckCircle2 } from 'lucide-react';

type ThemeColor = 'INDIGO' | 'CRIMSON' | 'EMERALD' | 'AMBER' | 'VIOLET';

const THEMES: Record<ThemeColor, {
  label: string;
  studioTag: string;
  headline: string;
  subhead: string;
  gradientClass: string;
  accentText: string;
  badgeBg: string;
}> = {
  EMERALD: {
    label: 'EMERALD',
    studioTag: 'FOCUSDNA ATTENTION STUDIO',
    headline: 'Lighting that sells the scene',
    subhead: 'Dial in contrast, depth, and atmosphere across every focus session.',
    gradientClass: 'bg-gradient-to-br from-emerald-950/80 via-teal-950/60 to-slate-950',
    accentText: 'text-emerald-400',
    badgeBg: 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400',
  },
  INDIGO: {
    label: 'INDIGO',
    studioTag: 'PREDICTIVE ML MODEL',
    headline: 'Predicting distraction before flow breaks',
    subhead: 'Supervised Gradient Boosted Trees detecting context-switching fatigue in real time.',
    gradientClass: 'bg-gradient-to-br from-indigo-950/90 via-slate-950 to-slate-950',
    accentText: 'text-indigo-400',
    badgeBg: 'bg-indigo-500/10 border-indigo-500/30 text-indigo-400',
  },
  CRIMSON: {
    label: 'CRIMSON',
    studioTag: 'AI NUDGE INTERVENTIONS',
    headline: 'Momentum engineered for deep work',
    subhead: 'Personalized Gemini AI recommendations delivered precisely at peak cognitive fatigue.',
    gradientClass: 'bg-gradient-to-br from-rose-950/80 via-pink-950/60 to-slate-950',
    accentText: 'text-rose-400',
    badgeBg: 'bg-rose-500/10 border-rose-500/30 text-rose-400',
  },
  AMBER: {
    label: 'AMBER',
    studioTag: 'ZERO-KEYSTROKE PRIVACY',
    headline: 'Absolute privacy by architectural design',
    subhead: '100% private process telemetry. Zero keystrokes, raw text, or screenshots captured.',
    gradientClass: 'bg-gradient-to-br from-amber-950/80 via-orange-950/60 to-slate-950',
    accentText: 'text-amber-400',
    badgeBg: 'bg-amber-500/10 border-amber-500/30 text-amber-400',
  },
  VIOLET: {
    label: 'VIOLET',
    studioTag: 'BEHAVIORAL PROFILE ENGINE',
    headline: 'Decode your personal attention DNA',
    subhead: 'Understand peak productivity windows, session stamina, and top distraction triggers.',
    gradientClass: 'bg-gradient-to-br from-violet-950/80 via-purple-950/60 to-slate-950',
    accentText: 'text-violet-400',
    badgeBg: 'bg-violet-500/10 border-violet-500/30 text-violet-400',
  },
};

export default function LandingPage() {
  const router = useRouter();
  const [activeTheme, setActiveTheme] = useState<ThemeColor>('EMERALD');
  const [isDemoLoading, setIsDemoLoading] = useState(false);

  const themeConfig = THEMES[activeTheme];

  const handleQuickDemoSession = () => {
    setIsDemoLoading(true);
    document.cookie = `focusdna-session=active; path=/; max-age=86400; SameSite=Lax`;
    localStorage.setItem('focusdna_user', JSON.stringify({
      email: 'demo@focusdna.ai',
      full_name: 'Demo User',
      user_id: 'demo_session_guest'
    }));
    setTimeout(() => {
      router.push('/dashboard');
    }, 400);
  };

  return (
    <div className="min-h-screen w-full bg-[#08080C] text-white flex flex-col lg:flex-row overflow-hidden font-sans">
      {/* LEFT SECTION (50% Split) - Minimalist Auth & Branding */}
      <div className="w-full lg:w-1/2 flex flex-col justify-between p-8 sm:p-14 lg:p-20 bg-[#08080C] z-10 border-r border-white/5 min-h-[50vh] lg:min-h-screen">
        {/* Top Header Logo */}
        <div className="flex items-center gap-3">
          <Link href="/" className="flex items-center gap-2.5 group">
            <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-gradient-to-tr from-violet-600 via-primary to-cyan-400 shadow-lg shadow-primary/30 group-hover:scale-105 transition-transform">
              <Zap className="h-5 w-5 text-white" />
            </div>
            <span className="text-xl font-bold tracking-tight text-white">
              Focus<span className="text-primary font-black">DNA</span>
              <span className="ml-2 text-[10px] font-mono uppercase tracking-widest bg-primary/20 text-primary px-2 py-0.5 rounded-full border border-primary/30">
                AI
              </span>
            </span>
          </Link>
        </div>

        {/* Middle Content - Auth / Welcome Card */}
        <div className="max-w-md w-full mx-auto my-auto py-8 space-y-8 text-center">
          {/* Logo Brand Icon Centered */}
          <div className="inline-flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-tr from-violet-600 to-indigo-500 shadow-xl shadow-indigo-500/20">
            <Zap className="h-7 w-7 text-white" />
          </div>

          <div className="space-y-2">
            <h1 className="text-3xl sm:text-4xl font-bold tracking-tight text-white">
              Welcome to FocusDNA AI
            </h1>
            <p className="text-xs text-gray-400 leading-relaxed max-w-sm mx-auto">
              Privacy-first attention intelligence platform learning digital behavior without raw text or keystrokes.
            </p>
          </div>

          {/* Action Buttons */}
          <div className="space-y-3 pt-2">
            {/* Primary Action Button - Sign In */}
            <Link
              href="/login"
              className="w-full py-3.5 px-6 rounded-2xl bg-gray-900/90 border border-gray-800 text-white font-medium text-sm hover:bg-gray-800/90 hover:border-gray-700 transition-all flex items-center justify-center gap-3 shadow-lg group"
            >
              <Mail className="h-4 w-4 text-gray-400 group-hover:text-white transition-colors" />
              <span>Continue with Email & Password</span>
            </Link>

            {/* Quick Demo Access Button */}
            <button
              onClick={handleQuickDemoSession}
              disabled={isDemoLoading}
              className="w-full py-3.5 px-6 rounded-2xl bg-gradient-to-r from-primary via-indigo-600 to-cyan-500 text-white font-bold text-sm hover:opacity-95 transition-all shadow-xl shadow-primary/25 flex items-center justify-center gap-2.5 cursor-pointer"
            >
              <LayoutDashboard className="h-4 w-4" />
              <span>{isDemoLoading ? 'Launching Live App...' : 'Explore Live Dashboard'}</span>
              <ArrowRight className="h-4 w-4" />
            </button>

            {/* Register Link */}
            <Link
              href="/signup"
              className="w-full py-3 px-6 rounded-2xl bg-transparent border border-transparent text-gray-400 font-semibold text-xs hover:text-white hover:border-gray-800 transition-all flex items-center justify-center gap-2"
            >
              <span>Don't have an account? <strong className="text-primary hover:underline">Create an account</strong></span>
            </Link>
          </div>

          {/* Privacy Terms Notice */}
          <p className="text-[11px] text-gray-500 leading-relaxed pt-4">
            By proceeding, you acknowledge our{' '}
            <Link href="/privacy" className="underline hover:text-gray-300 transition-colors">
              Privacy Policy
            </Link>{' '}
            and agree to the{' '}
            <Link href="/privacy" className="underline hover:text-gray-300 transition-colors">
              Terms & Conditions
            </Link>.
          </p>
        </div>

        {/* Bottom Status Badge */}
        <div className="flex items-center justify-between text-xs text-gray-500 border-t border-white/5 pt-6">
          <span className="flex items-center gap-2">
            <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
            Zero-Keystroke Architecture
          </span>
          <span className="font-mono text-[11px]">v1.0.0</span>
        </div>
      </div>

      {/* RIGHT SECTION (50% Split) - Atmospheric Studio Gradient & Interactive Themes */}
      <div className={`w-full lg:w-1/2 relative min-h-[50vh] lg:min-h-screen flex flex-col justify-between p-8 sm:p-14 lg:p-20 transition-all duration-700 ease-in-out ${themeConfig.gradientClass}`}>
        {/* Subtle Ambient Light Glow Orbs */}
        <div className="absolute top-1/4 right-1/4 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute bottom-1/4 left-1/4 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl pointer-events-none" />

        {/* Top Studio Category Tag */}
        <div className="relative z-10">
          <span className="text-[11px] font-mono tracking-widest uppercase text-gray-400 font-semibold">
            {themeConfig.studioTag}
          </span>
        </div>

        {/* Middle Big Typography Section */}
        <div className="relative z-10 max-w-xl my-auto py-12 space-y-6">
          <h2 className="text-4xl sm:text-5xl lg:text-6xl font-semibold tracking-tight text-white leading-tight">
            {themeConfig.headline}
          </h2>
          <p className="text-sm sm:text-base text-gray-300 leading-relaxed font-normal max-w-lg">
            {themeConfig.subhead}
          </p>

          <div className="pt-4 flex items-center gap-4 text-xs text-gray-400 font-medium">
            <div className={`px-3 py-1 rounded-full border ${themeConfig.badgeBg} flex items-center gap-1.5`}>
              <Sparkles className="h-3.5 w-3.5" />
              <span>Gradient Boosted Trees (F1: 0.9776)</span>
            </div>
            <div className="hidden sm:flex items-center gap-1.5 text-gray-400">
              <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />
              <span>Google Gemini AI</span>
            </div>
          </div>
        </div>

        {/* Bottom Right Interactive Theme Switcher Bar */}
        <div className="relative z-10 flex flex-wrap items-center justify-end gap-6 pt-8 border-t border-white/10">
          {(Object.keys(THEMES) as ThemeColor[]).map((themeKey) => {
            const isActive = activeTheme === themeKey;
            return (
              <button
                key={themeKey}
                onClick={() => setActiveTheme(themeKey)}
                className={`text-xs sm:text-sm font-mono tracking-wider transition-all relative py-1 cursor-pointer ${
                  isActive
                    ? 'text-white font-bold'
                    : 'text-gray-400 hover:text-gray-200'
                }`}
              >
                <span>{themeKey}</span>
                {isActive && (
                  <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-white rounded-full transition-all" />
                )}
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
}
