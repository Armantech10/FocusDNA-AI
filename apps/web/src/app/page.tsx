import React from 'react';
import Link from 'next/link';
import { Zap, ShieldCheck, ArrowRight, LayoutDashboard, Server } from 'lucide-react';

export default function LandingPage() {
  return (
    <div className="flex flex-col min-h-[calc(100vh-4rem)]">
      {/* Hero Section */}
      <section className="relative overflow-hidden pt-24 pb-16 px-6 text-center">
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-96 h-96 bg-primary/20 rounded-full blur-3xl pointer-events-none" />
        
        <div className="max-w-4xl mx-auto space-y-6 relative z-10">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-primary/10 border border-primary/30 text-primary text-xs font-semibold tracking-wide">
            <Zap className="h-4 w-4" />
            <span>Phase 1 Project Foundation</span>
          </div>

          <h1 className="text-5xl sm:text-6xl font-extrabold tracking-tight text-white leading-tight">
            Predictive Attention Intelligence <br className="hidden sm:inline" />
            <span className="bg-gradient-to-r from-primary via-cyan-400 to-emerald-400 bg-clip-text text-transparent">
              FocusDNA AI
            </span>
          </h1>

          <p className="text-lg text-gray-300 max-w-2xl mx-auto leading-relaxed">
            Privacy-first digital wellness platform shell. Designed for explicit behavioral learning without capturing raw text, keystrokes, or private content.
          </p>

          <div className="flex flex-wrap items-center justify-center gap-4 pt-4">
            <Link
              href="/dashboard"
              className="inline-flex items-center gap-2 px-6 py-3.5 rounded-2xl bg-primary text-white font-semibold shadow-lg shadow-primary/30 hover:bg-primary-hover transition-all"
            >
              <LayoutDashboard className="h-4 w-4" />
              <span>Open Dashboard Shell</span>
              <ArrowRight className="h-4 w-4" />
            </Link>

            <Link
              href="/status"
              className="inline-flex items-center gap-2 px-6 py-3.5 rounded-2xl glass-panel text-gray-300 font-semibold hover:text-white hover:border-gray-600 transition-all"
            >
              <Server className="h-4 w-4 text-emerald-400" />
              <span>Test API Health Endpoint</span>
            </Link>
          </div>
        </div>
      </section>

      {/* Principles Section */}
      <section className="max-w-5xl mx-auto px-6 py-12 grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="p-6 rounded-3xl glass-panel border border-border/80 space-y-3">
          <div className="h-10 w-10 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400 font-bold">
            01
          </div>
          <h3 className="text-lg font-bold text-white">Clean Monorepo Shell</h3>
          <p className="text-sm text-gray-400 leading-relaxed">
            Architected under `apps/web` and `apps/api` with structured placeholders for Chrome extension and Electron desktop agent.
          </p>
        </div>

        <div className="p-6 rounded-3xl glass-panel border border-border/80 space-y-3">
          <div className="h-10 w-10 rounded-xl bg-primary/10 border border-primary/30 flex items-center justify-center text-primary font-bold">
            02
          </div>
          <h3 className="text-lg font-bold text-white">FastAPI Backend</h3>
          <p className="text-sm text-gray-400 leading-relaxed">
            Standardized Python API framework with CORS middleware for local development and clean error handling.
          </p>
        </div>

        <div className="p-6 rounded-3xl glass-panel border border-border/80 space-y-3">
          <div className="h-10 w-10 rounded-xl bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400 font-bold">
            03
          </div>
          <h3 className="text-lg font-bold text-white">No Fake Analytics</h3>
          <p className="text-sm text-gray-400 leading-relaxed">
            Pure foundational structure. No fake metrics, mock predictions, or synthetic data placeholders generated prematurely.
          </p>
        </div>
      </section>
    </div>
  );
}
