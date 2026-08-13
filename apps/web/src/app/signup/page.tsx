'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { supabase } from '@/lib/supabase/client';
import { Zap, Lock, Mail, User, ArrowRight, ShieldCheck, AlertCircle } from 'lucide-react';

export default function SignupPage() {
  const router = useRouter();
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage(null);

    if (password !== confirmPassword) {
      setErrorMessage('Passwords do not match.');
      return;
    }

    if (password.length < 6) {
      setErrorMessage('Password must be at least 6 characters long.');
      return;
    }

    setLoading(true);

    try {
      // 1. Attempt Supabase Auth Registration
      const { data, error } = await supabase.auth.signUp({
        email,
        password,
        options: {
          data: { full_name: fullName }
        }
      });

      if (error) {
        setErrorMessage(error.message || 'Registration failed.');
        setLoading(false);
        return;
      }

      if (data?.user) {
        document.cookie = `focusdna-session=active; path=/; max-age=86400; SameSite=Lax`;
        const userProfile = {
          email,
          full_name: fullName,
          user_id: data.user.id
        };
        localStorage.setItem('focusdna_user', JSON.stringify(userProfile));
        router.push('/onboarding');
        return;
      } else {
        setErrorMessage('Registration failed. Please check your details.');
        setLoading(false);
        return;
      }
    } catch (err: any) {
      setErrorMessage(err.message || 'Registration failed.');
      setLoading(false);
      return;
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-[calc(100vh-4rem)] items-center justify-center p-6">
      <div className="w-full max-w-md p-8 rounded-3xl glass-panel border border-border/80 space-y-6 shadow-2xl">
        <div className="text-center space-y-2">
          <div className="inline-flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-tr from-primary to-cyan-500 shadow-lg shadow-primary/20 mb-2">
            <Zap className="h-6 w-6 text-white" />
          </div>
          <h2 className="text-2xl font-bold text-white tracking-tight">Create FocusDNA Account</h2>
          <p className="text-xs text-gray-400">Join the Attention Intelligence platform with strict zero-keystroke privacy.</p>
        </div>

        {errorMessage && (
          <div className="p-3.5 rounded-2xl bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs flex items-center gap-2">
            <AlertCircle className="h-4 w-4 shrink-0" />
            <span>{errorMessage}</span>
          </div>
        )}

        <form onSubmit={handleSignup} className="space-y-4">
          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-gray-300">Full Name</label>
            <div className="relative">
              <User className="absolute left-3.5 top-3 h-4 w-4 text-gray-500" />
              <input
                type="text"
                required
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                placeholder="Arman Tech"
                className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-gray-900/80 border border-gray-800 text-sm text-white focus:outline-none focus:border-primary transition-colors"
              />
            </div>
          </div>

          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-gray-300">Email Address</label>
            <div className="relative">
              <Mail className="absolute left-3.5 top-3 h-4 w-4 text-gray-500" />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="ska628480@gmail.com"
                className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-gray-900/80 border border-gray-800 text-sm text-white focus:outline-none focus:border-primary transition-colors"
              />
            </div>
          </div>

          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-gray-300">Password</label>
            <div className="relative">
              <Lock className="absolute left-3.5 top-3 h-4 w-4 text-gray-500" />
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-gray-900/80 border border-gray-800 text-sm text-white focus:outline-none focus:border-primary transition-colors"
              />
            </div>
          </div>

          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-gray-300">Confirm Password</label>
            <div className="relative">
              <Lock className="absolute left-3.5 top-3 h-4 w-4 text-gray-500" />
              <input
                type="password"
                required
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-gray-900/80 border border-gray-800 text-sm text-white focus:outline-none focus:border-primary transition-colors"
              />
            </div>
          </div>

          <div className="p-3 rounded-2xl bg-gray-900/60 border border-gray-800 flex items-start gap-2.5 text-[11px] text-gray-400">
            <ShieldCheck className="h-4 w-4 text-emerald-400 shrink-0 mt-0.5" />
            <span>By signing up, your telemetry is protected by zero-keystroke metadata privacy architecture.</span>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 rounded-xl bg-primary text-white font-bold text-sm shadow-lg shadow-primary/30 hover:bg-primary-hover transition-all flex items-center justify-center gap-2 cursor-pointer"
          >
            <span>{loading ? 'Creating Account...' : 'Register'}</span>
            <ArrowRight className="h-4 w-4" />
          </button>
        </form>

        <div className="text-center text-xs text-gray-400 pt-2">
          Already have an account?{' '}
          <Link href="/signup" className="text-primary font-semibold hover:underline">
            Sign in
          </Link>
        </div>
      </div>
    </div>
  );
}
