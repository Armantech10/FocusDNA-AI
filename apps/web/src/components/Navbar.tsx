'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { supabase } from '@/lib/supabase/client';
import { Zap, ShieldCheck, User, LogOut } from 'lucide-react';

export function Navbar() {
  const pathname = usePathname();
  const router = useRouter();

  if (pathname === '/') {
    return null;
  }

  const [userEmail, setUserEmail] = useState<string | null>(null);
  const [displayName, setDisplayName] = useState<string | null>(null);

  const checkUserSession = () => {
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
        } else {
          setUserEmail(null);
          setDisplayName(null);
        }
      }
    });
  };

  useEffect(() => {
    checkUserSession();

    const { data: { subscription } } = supabase.auth.onAuthStateChange(() => {
      checkUserSession();
    });

    return () => subscription.unsubscribe();
  }, []);

  const handleLogout = async () => {
    try {
      await supabase.auth.signOut();
    } catch (e) {
      // Ignore network errors on logout
    }
    localStorage.removeItem('focusdna_user');
    document.cookie = 'focusdna-session=; path=/; expires=Thu, 01 Jan 1970 00:00:01 GMT;';
    setUserEmail(null);
    setDisplayName(null);
    router.push('/login');
  };

  return (
    <header className="sticky top-0 z-40 w-full border-b border-border/60 bg-background/80 backdrop-blur-md">
      <div className="flex h-16 items-center justify-between px-6">
        <div className="flex items-center gap-3">
          <Link href="/" className="flex items-center gap-2 font-bold text-xl tracking-tight text-white hover:opacity-90 transition-opacity">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-tr from-primary to-cyan-500 shadow-lg shadow-primary/20">
              <Zap className="h-5 w-5 text-white" />
            </div>
            <span>Focus<span className="text-primary font-black">DNA</span> <span className="text-xs font-mono uppercase bg-primary/20 text-primary px-2 py-0.5 rounded-full border border-primary/30 ml-1">AI</span></span>
          </Link>
        </div>

        <div className="flex items-center gap-4">
          <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-medium">
            <ShieldCheck className="h-4 w-4" />
            <span>Zero-Keystroke Architecture</span>
          </div>

          {userEmail ? (
            <div className="flex items-center gap-3">
              <Link href="/settings" className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-gray-900 border border-gray-800 text-xs text-gray-300 hover:text-white transition-all">
                <User className="h-3.5 w-3.5 text-primary" />
                <span className="font-semibold">{displayName}</span>
              </Link>

              <button
                onClick={handleLogout}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-gray-800/80 text-gray-300 hover:text-rose-400 hover:bg-rose-500/10 border border-gray-700 text-xs font-semibold transition-all"
              >
                <LogOut className="h-3.5 w-3.5" />
                <span>Logout</span>
              </button>
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <Link href="/login" className="text-xs font-semibold px-4 py-2 rounded-xl text-gray-300 hover:text-white transition-all">
                Sign In
              </Link>
              <Link href="/signup" className="text-xs font-semibold px-4 py-2 rounded-xl bg-primary text-white hover:bg-primary-hover transition-all shadow-md">
                Register
              </Link>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
