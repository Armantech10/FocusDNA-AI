'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { supabase } from '@/lib/supabase/client';
import { Mail, ArrowRight, CheckCircle2, AlertCircle } from 'lucide-react';

export default function ResetPasswordPage() {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleReset = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage(null);
    setSuccessMessage(null);
    setLoading(true);

    try {
      const { error } = await supabase.auth.resetPasswordForEmail(email, {
        redirectTo: `${window.location.origin}/update-password`,
      });

      if (error) {
        setErrorMessage(error.message);
      } else {
        setSuccessMessage('Password reset link sent! Check your inbox.');
      }
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to send reset email.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-[calc(100vh-4rem)] items-center justify-center p-6">
      <div className="w-full max-w-md p-8 rounded-3xl glass-panel border border-border/80 space-y-6 shadow-2xl">
        <div className="text-center space-y-2">
          <h2 className="text-2xl font-bold text-white tracking-tight">Reset Password</h2>
          <p className="text-xs text-gray-400">Enter your account email to receive a password reset link.</p>
        </div>

        {successMessage && (
          <div className="p-3.5 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs flex items-center gap-2">
            <CheckCircle2 className="h-4 w-4 shrink-0" />
            <span>{successMessage}</span>
          </div>
        )}

        {errorMessage && (
          <div className="p-3.5 rounded-2xl bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs flex items-center gap-2">
            <AlertCircle className="h-4 w-4 shrink-0" />
            <span>{errorMessage}</span>
          </div>
        )}

        <form onSubmit={handleReset} className="space-y-4">
          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-gray-300">Email Address</label>
            <div className="relative">
              <Mail className="absolute left-3.5 top-3 h-4 w-4 text-gray-500" />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="user@example.com"
                className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-gray-900/80 border border-gray-800 text-sm text-white focus:outline-none focus:border-primary transition-colors"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 rounded-xl bg-primary text-white font-bold text-sm shadow-lg shadow-primary/30 hover:bg-primary-hover transition-all flex items-center justify-center gap-2"
          >
            <span>{loading ? 'Sending Request...' : 'Send Reset Link'}</span>
            <ArrowRight className="h-4 w-4" />
          </button>
        </form>

        <div className="text-center text-xs text-gray-400">
          Remember your password?{' '}
          <Link href="/login" className="text-primary font-semibold hover:underline">
            Back to Sign in
          </Link>
        </div>
      </div>
    </div>
  );
}
