'use client';

import React, { useState } from 'react';
import { Sidebar } from '@/components/Sidebar';
import { Activity, Server, RefreshCw, CheckCircle2, AlertCircle } from 'lucide-react';

export default function StatusPage() {
  const [healthResult, setHealthResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const checkHealth = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch('http://localhost:8000/health');
      if (!res.ok) {
        throw new Error(`HTTP error! Status: ${res.status}`);
      }
      const data = await res.json();
      setHealthResult(data);
    } catch (err: any) {
      setError(err.message || 'Failed to connect to FastAPI backend');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-[calc(100vh-4rem)]">
      <Sidebar />

      <div className="flex-1 p-8 space-y-8 overflow-y-auto">
        <div>
          <h1 className="text-3xl font-extrabold text-white tracking-tight">API Health Endpoint Tester</h1>
          <p className="text-sm text-gray-400 mt-1">
            Tests cross-origin request from Next.js (`http://localhost:3000`) to FastAPI `GET http://localhost:8000/health`.
          </p>
        </div>

        <div className="p-6 rounded-3xl glass-panel border border-border/80 space-y-4 max-w-xl">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 font-mono text-xs text-gray-300">
              <Server className="h-4 w-4 text-emerald-400" />
              <span>Target: GET http://localhost:8000/health</span>
            </div>

            <button
              onClick={checkHealth}
              disabled={loading}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-primary text-white text-xs font-semibold hover:bg-primary-hover transition-all"
            >
              <RefreshCw className={`h-3.5 w-3.5 ${loading ? 'animate-spin' : ''}`} />
              <span>Send Request</span>
            </button>
          </div>

          {healthResult && (
            <div className="p-4 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-mono space-y-1">
              <div className="flex items-center gap-2 font-bold">
                <CheckCircle2 className="h-4 w-4" />
                <span>Response Status 200 OK</span>
              </div>
              <pre className="bg-gray-900/80 p-3 rounded-xl text-gray-200 mt-2">
                {JSON.stringify(healthResult, null, 2)}
              </pre>
            </div>
          )}

          {error && (
            <div className="p-4 rounded-2xl bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs font-mono space-y-1">
              <div className="flex items-center gap-2 font-bold">
                <AlertCircle className="h-4 w-4" />
                <span>Connection Error</span>
              </div>
              <p className="text-gray-300 mt-1">{error}</p>
              <p className="text-[11px] text-gray-400 mt-2">
                Ensure FastAPI backend is running via `python3 -m uvicorn main:app --reload --port 8000` inside `apps/api/`.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
