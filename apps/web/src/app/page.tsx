'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { supabase } from '@/lib/supabase/client';
import { 
  Zap, 
  ArrowRight, 
  ShieldCheck, 
  LayoutDashboard, 
  Mail, 
  Sparkles, 
  CheckCircle2, 
  Brain, 
  Activity,
  LogOut,
  User,
  SlidersHorizontal,
  Layers
} from 'lucide-react';

type ThemeColor = 'INDIGO' | 'CRIMSON' | 'EMERALD' | 'AMBER' | 'VIOLET';

const THEMES: Record<ThemeColor, {
  label: string;
  studioTag: string;
  headlineMain: string;
  headlineGradient: string;
  subhead: string;
  gradientClass: string;
  accentText: string;
  badge1Bg: string;
  badge1Text: string;
  badge1Label: string;
  badge2Label: string;
  glowOrbClass: string;
}> = {
  INDIGO: {
    label: 'INDIGO',
    studioTag: 'ATTENTION INTELLIGENCE ENGINE',
    headlineMain: 'Predict distraction before it derails',
    headlineGradient: 'your momentum',
    subhead: 'Real-time behavioral telemetry that learns your focus windows, context-switch fatigue, and peak cognitive stamina.',
    gradientClass: 'bg-gradient-to-br from-[#0D0B26] via-[#090A1A] to-[#05050C]',
    accentText: 'text-indigo-400',
    badge1Bg: 'bg-indigo-500/15 border-indigo-500/30 text-indigo-300',
    badge1Text: 'text-indigo-400',
    badge1Label: 'Supervised ML Classifier • F1 0.9776',
    badge2Label: 'Real-Time Telemetry',
    glowOrbClass: 'from-indigo-600/30 via-purple-600/20 to-transparent'
  },
  CRIMSON: {
    label: 'CRIMSON',
    studioTag: 'GENERATIVE AI REASONING',
    headlineMain: 'Hyper-personalized nudges when focus',
    headlineGradient: 'begins to slip',
    subhead: 'Contextual Google Gemini AI recommendations delivered precisely when cognitive fatigue peaks, keeping deep work intact.',
    gradientClass: 'bg-gradient-to-br from-[#260B18] via-[#1A0912] to-[#0C0509]',
    accentText: 'text-rose-400',
    badge1Bg: 'bg-rose-500/15 border-rose-500/30 text-rose-300',
    badge1Text: 'text-rose-400',
    badge1Label: 'Google Gemini 1.5 Integration',
    badge2Label: 'Real-Time Telemetry',
    glowOrbClass: 'from-rose-600/30 via-pink-600/20 to-transparent'
  },
  EMERALD: {
    label: 'EMERALD',
    studioTag: 'BEHAVIORAL TELEMETRY MODEL',
    headlineMain: 'Optimal focus stamina tailored to',
    headlineGradient: 'your natural rhythm',
    subhead: 'Learn your typical session duration, peak cognitive hours, and context-switching dynamics without raw text or keystrokes.',
    gradientClass: 'bg-gradient-to-br from-[#0B261A] via-[#091A13] to-[#050C08]',
    accentText: 'text-emerald-400',
    badge1Bg: 'bg-emerald-500/15 border-emerald-500/30 text-emerald-300',
    badge1Text: 'text-emerald-400',
    badge1Label: 'Zero-Keystroke Architecture',
    badge2Label: 'Real-Time Telemetry',
    glowOrbClass: 'from-emerald-600/30 via-teal-600/20 to-transparent'
  },
  AMBER: {
    label: 'AMBER',
    studioTag: 'ANOMALY DETECTION SYSTEM',
    headlineMain: 'Detect unusual distraction spikes before',
    headlineGradient: 'they derail your day',
    subhead: 'Unsupervised Isolation Forest anomaly detection flagging sudden behavioral deviations over baseline patterns.',
    gradientClass: 'bg-gradient-to-br from-[#261B0B] via-[#1A1309] to-[#0C0905]',
    accentText: 'text-amber-400',
    badge1Bg: 'bg-amber-500/15 border-amber-500/30 text-amber-300',
    badge1Text: 'text-amber-400',
    badge1Label: 'Isolation Forest Anomaly Detector',
    badge2Label: 'Real-Time Telemetry',
    glowOrbClass: 'from-amber-600/30 via-orange-600/20 to-transparent'
  },
  VIOLET: {
    label: 'VIOLET',
    studioTag: 'BEHAVIORAL PROFILE ENGINE',
    headlineMain: 'Decode your personal digital attention',
    headlineGradient: 'focus fingerprint',
    subhead: 'Comprehensive FocusDNA behavioral profile engine mapping consistency score, stamina curves, and top distraction triggers.',
    gradientClass: 'bg-gradient-to-br from-[#200B26] via-[#15091A] to-[#0A050C]',
    accentText: 'text-violet-400',
    badge1Bg: 'bg-violet-500/15 border-violet-500/30 text-violet-300',
    badge1Text: 'text-violet-400',
    badge1Label: 'Personalized FocusDNA Profile Engine',
    badge2Label: 'Real-Time Telemetry',
    glowOrbClass: 'from-violet-600/30 via-purple-600/20 to-transparent'
  },
};

export default function LandingPage() {
  const router = useRouter();
  const [activeTheme, setActiveTheme] = useState<ThemeColor>('INDIGO');
  const [userEmail, setUserEmail] = useState<string | null>(null);
  const [displayName, setDisplayName] = useState<string | null>(null);
  const [isDemoLoading, setIsDemoLoading] = useState(false);

  useEffect(() => {
    // Check if user is authenticated
    supabase.auth.getUser().then(({ data: { user } }) => {
      if (user) {
        setUserEmail(user.email || null);
        setDisplayName(user.user_metadata?.full_name || user.email?.split('@')[0] || 'User');
      } else {
        const devUserStr = localStorage.getItem('focusdna_user');
        if (devUserStr) {
          try {
            const devUser = JSON.parse(devUserStr);
            setUserEmail(devUser.email || null);
            setDisplayName(devUser.full_name || devUser.email?.split('@')[0] || 'User');
          } catch (e) {
            setUserEmail(null);
            setDisplayName(null);
          }
        }
      }
    });
  }, []);

  const themeConfig = THEMES[activeTheme];

  const handleLogout = async () => {
    try {
      await supabase.auth.signOut();
    } catch (e) {
      // Ignore network error on logout
    }
    localStorage.removeItem('focusdna_user');
    document.cookie = 'focusdna-session=; path=/; expires=Thu, 01 Jan 1970 00:00:01 GMT;';
    setUserEmail(null);
    setDisplayName(null);
    router.refresh();
  };

  const handleGoogleOAuth = async () => {
    try {
      const { error } = await supabase.auth.signInWithOAuth({
        provider: 'google',
        options: {
          redirectTo: `${window.location.origin}/dashboard`
        }
      });
      if (error) {
        router.push('/login');
      }
    } catch (e) {
      router.push('/login');
    }
  };

  const handleAppleOAuth = async () => {
    try {
      const { error } = await supabase.auth.signInWithOAuth({
        provider: 'apple',
        options: {
          redirectTo: `${window.location.origin}/dashboard`
        }
      });
      if (error) {
        router.push('/login');
      }
    } catch (e) {
      router.push('/login');
    }
  };

  return (
    <div className="min-h-screen w-full bg-[#08080D] text-white flex flex-col font-sans selection:bg-indigo-500/30 selection:text-white">
      {/* MINIMAL TOP HEADER */}
      <header className="w-full z-40 px-6 sm:px-12 py-5 flex items-center justify-between border-b border-white/5 bg-[#08080D]/80 backdrop-blur-md">
        {/* Left: FocusDNA Logo & AI Badge */}
        <Link href="/" className="flex items-center gap-2.5 group">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-tr from-indigo-600 via-violet-600 to-purple-500 shadow-md shadow-indigo-500/25 group-hover:scale-105 transition-transform">
            <Zap className="h-5 w-5 text-white" />
          </div>
          <span className="text-xl font-bold tracking-tight text-white flex items-center gap-1.5">
            Focus<span className="text-indigo-400 font-black">DNA</span>
            <span className="text-[10px] font-mono uppercase tracking-wider bg-indigo-500/20 text-indigo-300 px-2 py-0.5 rounded-full border border-indigo-500/30 ml-0.5">
              AI
            </span>
          </span>
        </Link>

        {/* Right: Architecture Badge & Auth Status */}
        <div className="flex items-center gap-3.5">
          <div className="hidden sm:flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-medium">
            <ShieldCheck className="h-3.5 w-3.5" />
            <span>Zero-Keystroke Architecture</span>
          </div>

          {userEmail ? (
            <div className="flex items-center gap-2.5">
              <Link href="/dashboard" className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-indigo-600/20 border border-indigo-500/30 text-xs font-semibold text-indigo-300 hover:text-white transition-all">
                <User className="h-3.5 w-3.5" />
                <span>{displayName}</span>
              </Link>
              <button
                onClick={handleLogout}
                className="inline-flex items-center gap-1 px-3 py-1.5 rounded-xl bg-gray-900/80 hover:bg-rose-500/10 text-gray-400 hover:text-rose-400 border border-gray-800 text-xs font-semibold transition-all"
              >
                <LogOut className="h-3.5 w-3.5" />
                <span>Logout</span>
              </button>
            </div>
          ) : (
            <Link
              href="/login"
              className="inline-flex items-center gap-1.5 px-4 py-1.5 rounded-xl bg-gray-900/80 border border-gray-800 text-xs text-gray-300 hover:text-white hover:border-gray-700 font-semibold transition-all shadow-sm"
            >
              <LogOut className="h-3.5 w-3.5 text-gray-400 rotate-180" />
              <span>Login</span>
            </Link>
          )}
        </div>
      </header>

      {/* MAIN SPLIT-SCREEN LAYOUT (45% Left / 55% Right on Desktop, Responsive Stack on Mobile) */}
      <main className="flex-1 flex flex-col lg:flex-row w-full overflow-hidden">
        
        {/* LEFT PANEL (45% Width on Desktop) - Near-Black Minimal Auth Interface */}
        <div className="w-full lg:w-[45%] flex flex-col justify-between p-8 sm:p-12 lg:p-16 bg-[#08080D] border-r border-white/5 min-h-[500px] lg:min-h-[calc(100vh-4.25rem)]">
          
          <div className="max-w-md w-full mx-auto my-auto py-6 space-y-7 text-center">
            
            {/* Glowing Brain/AI Icon */}
            <div className="inline-flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-tr from-indigo-600 via-violet-600 to-purple-500 shadow-xl shadow-indigo-500/30">
              <Brain className="h-7 w-7 text-white" />
            </div>

            {/* Title & Description */}
            <div className="space-y-2.5">
              <h1 className="text-3xl sm:text-4xl font-bold tracking-tight text-white">
                Welcome to <span className="bg-gradient-to-r from-indigo-400 via-violet-400 to-purple-400 bg-clip-text text-transparent">FocusDNA AI</span>
              </h1>
              <p className="text-xs text-gray-400 leading-relaxed max-w-sm mx-auto font-normal">
                Privacy-first attention intelligence platform learning digital behavior without raw text or keystrokes.
              </p>
            </div>

            {/* Authentication Buttons & Actions */}
            <div className="space-y-3.5 pt-2">
              
              {/* OAuth Google Button */}
              <button
                onClick={handleGoogleOAuth}
                className="w-full py-3 px-5 rounded-2xl bg-[#11111A] border border-gray-800/90 text-white font-medium text-xs sm:text-sm hover:bg-[#161624] hover:border-gray-700 transition-all flex items-center justify-center gap-3 shadow-md group cursor-pointer"
              >
                <svg className="h-4 w-4 shrink-0" viewBox="0 0 24 24">
                  <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                  <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                  <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"/>
                  <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"/>
                </svg>
                <span>Continue with Google</span>
              </button>

              {/* OAuth Apple Button */}
              <button
                onClick={handleAppleOAuth}
                className="w-full py-3 px-5 rounded-2xl bg-[#11111A] border border-gray-800/90 text-white font-medium text-xs sm:text-sm hover:bg-[#161624] hover:border-gray-700 transition-all flex items-center justify-center gap-3 shadow-md group cursor-pointer"
              >
                <svg className="h-4 w-4 shrink-0 fill-current text-white" viewBox="0 0 24 24">
                  <path d="M18.71 19.5c-.83 1.24-1.71 2.45-3.05 2.47-1.34.03-1.77-.79-3.29-.79-1.53 0-2 .77-3.27.82-1.31.05-2.3-1.32-3.14-2.53C4.25 17 2.94 12.45 4.7 9.39c.87-1.52 2.43-2.48 4.12-2.51 1.28-.02 2.5.87 3.29.87.78 0 2.26-1.07 3.81-.91.65.03 2.47.26 3.64 1.98-.09.06-2.17 1.28-2.15 3.81.03 3.02 2.65 4.03 2.68 4.04-.03.07-.42 1.44-1.38 2.83M15.97 6.32c.67-.82 1.13-1.96.99-3.1-.97.04-2.17.65-2.86 1.46-.61.71-1.15 1.87-.99 2.99 1.09.08 2.21-.53 2.86-1.35Z"/>
                </svg>
                <span>Continue with Apple</span>
              </button>

              {/* Divider */}
              <div className="relative flex items-center justify-center my-3">
                <div className="border-t border-gray-800/80 w-full" />
                <span className="bg-[#08080D] px-3 text-[11px] font-mono text-gray-500 uppercase tracking-wider">or</span>
              </div>

              {/* Primary Email CTA Button */}
              <Link
                href="/login"
                className="w-full py-3.5 px-6 rounded-2xl bg-gradient-to-r from-indigo-600 via-violet-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white font-bold text-xs sm:text-sm shadow-lg shadow-indigo-600/30 transition-all flex items-center justify-center gap-2.5 cursor-pointer"
              >
                <Mail className="h-4 w-4" />
                <span>Continue with Email</span>
              </Link>
            </div>

            {/* Account Switcher Link */}
            <div className="text-xs text-gray-400 pt-1">
              Already have an account?{' '}
              <Link href="/login" className="text-indigo-400 font-semibold hover:underline">
                Login
              </Link>
            </div>

            {/* Legal Links */}
            <p className="text-[11px] text-gray-500 leading-relaxed pt-2">
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

          {/* Footer Badge */}
          <div className="flex items-center justify-between text-xs text-gray-500 border-t border-white/5 pt-4">
            <span className="flex items-center gap-2 text-[11px]">
              <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
              Zero-Keystroke Architecture
            </span>
            <span className="font-mono text-[11px]">v1.0.0</span>
          </div>
        </div>

        {/* RIGHT PANEL (55% Width on Desktop) - Atmospheric Indigo Hero & Feature Indicators */}
        <div className={`w-full lg:w-[55%] relative min-h-[550px] lg:min-h-[calc(100vh-4.25rem)] flex flex-col justify-between p-8 sm:p-14 lg:p-20 transition-all duration-700 ease-in-out ${themeConfig.gradientClass}`}>
          
          {/* Subtle Ambient Radial Light Orb & Curved Background Glow */}
          <div className={`absolute top-0 right-0 w-[550px] h-[550px] rounded-full bg-gradient-to-br ${themeConfig.glowOrbClass} blur-3xl opacity-60 pointer-events-none`} />
          <div className="absolute bottom-10 left-10 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl opacity-40 pointer-events-none" />
          
          {/* Abstract Subtle Curved Circle Line */}
          <div className="absolute top-1/2 -right-32 w-[600px] h-[600px] rounded-full border border-white/5 pointer-events-none" />

          {/* Top Category Badge */}
          <div className="relative z-10">
            <span className="text-[11px] font-mono tracking-widest uppercase text-indigo-400 font-semibold">
              {themeConfig.studioTag}
            </span>
          </div>

          {/* Hero Typography & Feature Badges */}
          <div className="relative z-10 max-w-xl my-auto py-10 space-y-6">
            <h2 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight text-white leading-[1.1]">
              {themeConfig.headlineMain} <br className="hidden sm:inline" />
              <span className="bg-gradient-to-r from-blue-400 via-indigo-400 to-purple-400 bg-clip-text text-transparent">
                {themeConfig.headlineGradient}
              </span>
            </h2>

            <p className="text-sm sm:text-base text-gray-300 leading-relaxed font-normal max-w-lg">
              {themeConfig.subhead}
            </p>

            {/* Feature Badges */}
            <div className="pt-3 flex flex-wrap items-center gap-3 text-xs font-medium">
              <div className={`px-4 py-2 rounded-full border ${themeConfig.badge1Bg} flex items-center gap-2 shadow-sm`}>
                <Sparkles className="h-3.5 w-3.5" />
                <span>{themeConfig.badge1Label}</span>
              </div>
              <div className="flex items-center gap-2 text-gray-300 bg-black/40 backdrop-blur-md px-4 py-2 rounded-full border border-white/10 shadow-sm">
                <Activity className="h-3.5 w-3.5 text-cyan-400" />
                <span>{themeConfig.badge2Label}</span>
              </div>
            </div>
          </div>

          {/* Bottom Interactive Theme Indicators */}
          <div className="relative z-10 flex flex-wrap items-center justify-end gap-6 pt-6 border-t border-white/10">
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

      </main>
    </div>
  );
}
