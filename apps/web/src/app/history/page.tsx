'use client';

import React, { useEffect, useState } from 'react';
import { Sidebar } from '@/components/Sidebar';
import { EmptyState } from '@/components/EmptyState';
import { supabase } from '@/lib/supabase/client';
import { History, ShieldCheck, Filter } from 'lucide-react';

export default function HistoryPage() {
  const [events, setEvents] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    supabase.auth.getUser().then(({ data: { user } }) => {
      if (user) {
        supabase
          .from('activity_events')
          .select('*')
          .eq('user_id', user.id)
          .order('timestamp', { ascending: false })
          .then(({ data }) => {
            if (data && data.length > 0) {
              setEvents(data);
            } else {
              setEvents([]);
            }
            setLoading(false);
          });
      } else {
        setEvents([]);
        setLoading(false);
      }
    });
  }, []);

  return (
    <div className="flex min-h-[calc(100vh-4rem)]">
      <Sidebar />

      <div className="flex-1 p-6 sm:p-8 space-y-8 overflow-y-auto">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-extrabold text-white tracking-tight">Activity Audit History</h1>
            <p className="text-sm text-gray-400 mt-1">
              Searchable record of evaluated activity events. Verify zero keystrokes collected.
            </p>
          </div>

          <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 text-xs font-semibold">
            <ShieldCheck className="h-4 w-4" />
            <span>Zero Raw Content Policy Enforced</span>
          </div>
        </div>

        {events.length === 0 ? (
          <EmptyState
            icon={History}
            title="No Activity Events Recorded Yet"
            description="Your audit log will populate as events are captured by background collectors or focus sessions."
            actionText="Start Focus Session"
            actionHref="/focus"
          />
        ) : (
          <div className="rounded-3xl glass-panel border border-border/80 overflow-hidden">
            <div className="p-4 border-b border-border/60 flex items-center justify-between">
              <span className="text-xs font-semibold text-gray-400">Activity Telemetry Log</span>
              <button className="flex items-center gap-1 text-xs text-gray-400 hover:text-white">
                <Filter className="h-3.5 w-3.5" />
                <span>Filter Events</span>
              </button>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-gray-900/60 text-gray-400 uppercase font-mono">
                  <tr>
                    <th className="px-6 py-3">Time</th>
                    <th className="px-6 py-3">Application</th>
                    <th className="px-6 py-3">Domain</th>
                    <th className="px-6 py-3">Switches</th>
                    <th className="px-6 py-3">Typing Level</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border/40 text-gray-300">
                  {events.map((item) => (
                    <tr key={item.id} className="hover:bg-gray-800/30 transition-colors">
                      <td className="px-6 py-4 font-mono">{new Date(item.timestamp).toLocaleTimeString()}</td>
                      <td className="px-6 py-4 font-semibold text-white">{item.application_name || 'System'}</td>
                      <td className="px-6 py-4 font-mono text-gray-400">{item.website_domain || 'N/A'}</td>
                      <td className="px-6 py-4">{item.app_switch_count} switches</td>
                      <td className="px-6 py-4">
                        <span className="px-2 py-0.5 rounded-md bg-gray-800 text-gray-300 font-mono">
                          {item.typing_activity_level}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
