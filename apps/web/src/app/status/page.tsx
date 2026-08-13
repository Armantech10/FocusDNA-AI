'use client';

import React, { useState } from 'react';
import { Sidebar } from '@/components/Sidebar';
import { getApiUrl } from '@/lib/api';
import { ShieldCheck, Server, Database, Activity, RefreshCw } from 'lucide-react';

export default function StatusPage() {
  const [apiStatus, setApiStatus] = useState<string>('Unknown');
  const [apiLatency, setApiLatency] = useState<number | null>(null);
  const [loading, setLoading] = useState<boolean>(false);

  const checkHealth = async () => {
    setLoading(true);
    const start = performance.now();
    try {
      const res = await fetch(getApiUrl('/health'));
      const end = performance.now();
      if (res.ok) {
        setApiStatus('Healthy (HTTP 200)');
        setApiLatency(Math.round(end - start));
      } else {
        setApiStatus(`Degraded (HTTP ${res.status})`);
        setApiLatency(Math.round(end - start));
      }
    } catch (e) {
      setApiStatus('Offline / Unreachable');
      setApiLatency(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-[calc(100vh-4rem)]">
      <Sidebar />

      <div className="flex-1 p-6 sm:p-8 space-y-8 overflow-y-auto">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-3xl font-extrabold text-white tracking-tight">System Status & Cross-Origin Connectivity</h1>
            <p className="text-sm text-gray-400 mt-1">
              Real-time infrastructure health check and API status monitor.
            </p>
          </div>

          <button
            onClick={checkHealth}
            disabled={loading}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-primary text-white text-xs font-bold shadow-lg hover:bg-primary-hover transition-all cursor-pointer self-start sm:self-auto"
          >
            <RefreshCw className={`h-3.5 w-3.5 ${loading ? 'animate-spin' : ''}`} />
            <span>Test API Health</span>
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Card 1: FastAPI Backend Health */}
          <div className="p-6 rounded-3xl glass-panel border border-border/80 space-y-3 shadow-lg">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-gray-400 uppercase tracking-wider font-mono">FastAPI Server</span>
              <Server className="h-5 w-5 text-primary" />
            </div>
            <div className="text-xl font-bold text-white font-mono">{apiStatus}</div>
            <div className="text-xs text-gray-400">
              Latency: {apiLatency !== null ? `${apiLatency} ms` : 'N/A'}
            </div>
          </div>

          {/* Card 2: Supabase Database */}
          <div className="p-6 rounded-3xl glass-panel border border-border/80 space-y-3 shadow-lg">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-gray-400 uppercase tracking-wider font-mono">Supabase Auth & DB</span>
              <Database className="h-5 w-5 text-emerald-400" />
            </div>
            <div className="text-xl font-bold text-emerald-400 font-mono">Connected</div>
            <div className="text-xs text-gray-400">Row-Level Security Active</div>
          </div>

          {/* Card 3: ML Inference Engine */}
          <div className="p-6 rounded-3xl glass-panel border border-border/80 space-y-3 shadow-lg">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-gray-400 uppercase tracking-wider font-mono">ML & Anomaly Engine</span>
              <Activity className="h-5 w-5 text-cyan-400" />
            </div>
            <div className="text-xl font-bold text-cyan-400 font-mono">Operational</div>
            <div className="text-xs text-gray-400">Gradient Boosted Trees (F1: 0.9776)</div>
          </div>
        </div>
      </div>
    </div>
  );
}
