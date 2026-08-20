'use client';

import React, { useState, useEffect } from 'react';
import { Sidebar } from '@/components/Sidebar';
import { supabase } from '@/lib/supabase/client';
import { 
  Target, 
  Play, 
  Pause, 
  Square, 
  Shield, 
  CheckCircle2, 
  XCircle, 
  History, 
  Zap, 
  Award,
  AlertTriangle
} from 'lucide-react';

interface SessionRecord {
  id?: string;
  session_name: string;
  target_duration_minutes: number;
  actual_duration_minutes: number;
  status: string;
  distraction_count: number;
  started_at: string;
  heuristic_score?: number;
}

export default function FocusSessionPage() {
  const [targetMinutes, setTargetMinutes] = useState(25);
  const [secondsLeft, setSecondsLeft] = useState(25 * 60);
  const [sessionState, setSessionState] = useState<'idle' | 'active' | 'paused'>('idle');
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [distractionCount, setDistractionCount] = useState(0);
  
  // Completed Summary Modal State
  const [summaryData, setSummaryData] = useState<{
    sessionName: string;
    plannedMinutes: number;
    actualMinutes: number;
    distractions: number;
    status: string;
    heuristicScore: number;
    explanation: string;
  } | null>(null);

  const [sessionHistory, setSessionHistory] = useState<SessionRecord[]>([]);

  const loadHistory = async () => {
    try {
      const { data: { user } } = await supabase.auth.getUser();
      if (user) {
        const { data } = await supabase
          .from('focus_sessions')
          .select('*')
          .eq('user_id', user.id)
          .order('started_at', { ascending: false });

        if (data && data.length > 0) {
          setSessionHistory(data);
          return;
        }
      }
    } catch (e) {
      // Fallback
    }

    const localStr = localStorage.getItem('focusdna_sessions');
    if (localStr) {
      setSessionHistory(JSON.parse(localStr));
    }
  };

  useEffect(() => {
    loadHistory();
  }, []);

  useEffect(() => {
    let interval: any = null;
    if (sessionState === 'active' && secondsLeft > 0) {
      interval = setInterval(() => {
        setSecondsLeft((prev) => prev - 1);
      }, 1000);
    } else if (secondsLeft === 0 && sessionState === 'active') {
      handleFinishSession();
    }
    return () => clearInterval(interval);
  }, [sessionState, secondsLeft]);

  const broadcastExtensionMessage = async (type: string, sessionId?: string) => {
    try {
      const { data: { session } } = await supabase.auth.getSession();
      const token = session?.access_token || localStorage.getItem('supabase.auth.token') || null;

      // 1. PostMessage bridge for content script / background worker
      window.postMessage({
        source: 'FOCUSDNA_WEB_APP',
        type,
        session_id: sessionId,
        token
      }, '*');

      // 2. Direct Chrome Extension message if available
      if (typeof window !== 'undefined' && (window as any).chrome && (window as any).chrome.runtime && (window as any).chrome.runtime.sendMessage) {
        try {
          (window as any).chrome.runtime.sendMessage({
            type,
            session_id: sessionId,
            token
          });
        } catch (e) {
          // Ignore if extension ID not registered
        }
      }
    } catch (e) {
      // Ignore
    }
  };

  const handleStartSession = async (mins: number = targetMinutes) => {
    setTargetMinutes(mins);
    setSecondsLeft(mins * 60);
    setDistractionCount(0);
    setSessionState('active');
    setSummaryData(null);

    const newId = `session_${Date.now()}`;
    setActiveSessionId(newId);

    // Broadcast session start to Chrome extension
    await broadcastExtensionMessage('FOCUSDNA_SESSION_START', newId);

    try {
      const { data: { user } } = await supabase.auth.getUser();
      if (user) {
        await supabase.from('focus_sessions').insert({
          id: newId,
          user_id: user.id,
          session_name: `${mins}m Focus Session`,
          target_duration_minutes: mins,
          actual_duration_minutes: 0,
          status: 'active',
          distraction_count: 0,
          started_at: new Date().toISOString()
        });
      }
    } catch (e) {
      // Local dev fallback
    }
  };

  const handlePauseSession = () => {
    setSessionState('paused');
  };

  const handleResumeSession = () => {
    setSessionState('active');
  };

  const handleFinishSession = async () => {
    setSessionState('idle');
    const elapsedMinutes = Math.max(1, Math.round((targetMinutes * 60 - secondsLeft) / 60));

    // Broadcast session end to Chrome extension
    await broadcastExtensionMessage('FOCUSDNA_SESSION_END', activeSessionId || undefined);

    let recordedEvents: any[] = [];
    try {
      const { data: { user } } = await supabase.auth.getUser();
      if (user && activeSessionId) {
        const { data: eventsData } = await supabase
          .from('activity_events')
          .select('*')
          .eq('focus_session_id', activeSessionId);

        if (eventsData && eventsData.length > 0) {
          recordedEvents = eventsData;
        }
      }
    } catch (e) {
      // Ignore
    }

    const hasRealTelemetry = recordedEvents.length > 0;
    const tabSwitches = recordedEvents.reduce((acc, e) => acc + (e.browser_switch_count || 0) + (e.app_switch_count || 0), 0);
    const totalDistractions = recordedEvents.filter(e => e.category === 'social_media' || e.category === 'entertainment').length;
    const effectiveDistractions = Math.max(distractionCount, totalDistractions);

    // Transparent Heuristic Score calculation
    const completionRatio = elapsedMinutes / targetMinutes;
    const penalty = effectiveDistractions * 8 + (tabSwitches > 5 ? (tabSwitches - 5) * 2 : 0);
    const heuristicScore = Math.max(0, Math.min(100, Math.round(100 * completionRatio - penalty)));

    const explanationText = hasRealTelemetry
      ? `Evaluated from ${recordedEvents.length} Chrome extension telemetry events (${tabSwitches} tab switches, ${effectiveDistractions} distraction domain triggers).`
      : `Calculated from ${Math.round(completionRatio * 100)}% time completion. (No telemetry events captured for this session).`;

    const summary = {
      sessionName: `${targetMinutes}m Focus Session`,
      plannedMinutes: targetMinutes,
      actualMinutes: elapsedMinutes,
      distractions: effectiveDistractions,
      status: 'completed',
      heuristicScore: heuristicScore,
      explanation: explanationText
    };
    setSummaryData(summary);

    const record: SessionRecord = {
      id: activeSessionId || `session_${Date.now()}`,
      session_name: summary.sessionName,
      target_duration_minutes: targetMinutes,
      actual_duration_minutes: elapsedMinutes,
      status: 'completed',
      distraction_count: effectiveDistractions,
      started_at: new Date().toISOString(),
      heuristic_score: heuristicScore
    };

    try {
      const { data: { user } } = await supabase.auth.getUser();
      if (user && activeSessionId) {
        await supabase
          .from('focus_sessions')
          .update({
            actual_duration_minutes: elapsedMinutes,
            status: 'completed',
            ended_at: new Date().toISOString(),
            distraction_count: effectiveDistractions
          })
          .eq('id', activeSessionId);
      }
    } catch (e) {
      // Ignore
    }

    const currentHistory = [record, ...sessionHistory];
    setSessionHistory(currentHistory);
    localStorage.setItem('focusdna_sessions', JSON.stringify(currentHistory));
  };

  const handleCancelSession = async () => {
    setSessionState('idle');
    const elapsedMinutes = Math.max(1, Math.round((targetMinutes * 60 - secondsLeft) / 60));

    // Broadcast session end to Chrome extension
    await broadcastExtensionMessage('FOCUSDNA_SESSION_END', activeSessionId || undefined);

    const summary = {
      sessionName: `${targetMinutes}m Focus Session`,
      plannedMinutes: targetMinutes,
      actualMinutes: elapsedMinutes,
      distractions: distractionCount,
      status: 'canceled',
      heuristicScore: 35,
      explanation: 'Session was canceled before target duration was reached.'
    };
    setSummaryData(summary);

    const record: SessionRecord = {
      id: activeSessionId || `session_${Date.now()}`,
      session_name: summary.sessionName,
      target_duration_minutes: targetMinutes,
      actual_duration_minutes: elapsedMinutes,
      status: 'canceled',
      distraction_count: distractionCount,
      started_at: new Date().toISOString(),
      heuristic_score: 35
    };

    try {
      const { data: { user } } = await supabase.auth.getUser();
      if (user && activeSessionId) {
        await supabase
          .from('focus_sessions')
          .update({
            actual_duration_minutes: elapsedMinutes,
            status: 'canceled',
            ended_at: new Date().toISOString()
          })
          .eq('id', activeSessionId);
      }
    } catch (e) {
      // Ignore
    }

    const currentHistory = [record, ...sessionHistory];
    setSessionHistory(currentHistory);
    localStorage.setItem('focusdna_sessions', JSON.stringify(currentHistory));
  };

  const formatTime = (totalSeconds: number) => {
    const mins = Math.floor(totalSeconds / 60);
    const secs = totalSeconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="flex min-h-[calc(100vh-4rem)]">
      <Sidebar />

      <div className="flex-1 p-6 sm:p-8 space-y-8 overflow-y-auto">
        <div>
          <h1 className="text-3xl font-extrabold text-white tracking-tight">Focus Session Engine</h1>
          <p className="text-sm text-gray-400 mt-1">Start, pause, finish, or cancel deep work sessions with heuristic scoring.</p>
        </div>

        {/* Main Session Timer Controls */}
        <div className="max-w-2xl mx-auto flex flex-col items-center justify-center p-8 sm:p-12 rounded-3xl glass-panel border border-border/80 text-center space-y-8">
          <div className="flex items-center gap-3">
            {[15, 25, 45, 60].map((mins) => (
              <button
                key={mins}
                onClick={() => handleStartSession(mins)}
                disabled={sessionState !== 'idle'}
                className={`px-4 py-2 rounded-xl text-xs font-mono font-semibold transition-all ${
                  targetMinutes === mins && sessionState !== 'idle'
                    ? 'bg-primary text-white shadow-lg shadow-primary/30'
                    : 'glass-panel text-gray-400 hover:text-white disabled:opacity-50'
                }`}
              >
                {mins}m Session
              </button>
            ))}
          </div>

          {/* Big Timer Display */}
          <div className="text-7xl sm:text-8xl font-black font-mono tracking-tighter text-white">
            {formatTime(secondsLeft)}
          </div>

          {/* Lifecycle Action Buttons */}
          <div className="flex flex-wrap items-center justify-center gap-3">
            {sessionState === 'idle' && (
              <button
                onClick={() => handleStartSession(targetMinutes)}
                className="inline-flex items-center gap-2 px-8 py-4 rounded-2xl bg-primary text-white font-bold text-sm shadow-xl shadow-primary/30 hover:bg-primary-hover transition-all"
              >
                <Play className="h-5 w-5" />
                <span>Start Session</span>
              </button>
            )}

            {sessionState === 'active' && (
              <>
                <button
                  onClick={handlePauseSession}
                  className="inline-flex items-center gap-2 px-6 py-3.5 rounded-2xl bg-amber-500 text-white font-bold text-sm shadow-lg shadow-amber-500/30 hover:bg-amber-600 transition-all"
                >
                  <Pause className="h-5 w-5" />
                  <span>Pause Session</span>
                </button>

                <button
                  onClick={handleFinishSession}
                  className="inline-flex items-center gap-2 px-6 py-3.5 rounded-2xl bg-emerald-500 text-white font-bold text-sm shadow-lg shadow-emerald-500/30 hover:bg-emerald-600 transition-all"
                >
                  <CheckCircle2 className="h-5 w-5" />
                  <span>Finish Session</span>
                </button>

                <button
                  onClick={handleCancelSession}
                  className="inline-flex items-center gap-2 px-4 py-3.5 rounded-2xl glass-panel text-rose-400 hover:text-white hover:bg-rose-500/10 border border-rose-500/30 text-xs font-semibold transition-all"
                >
                  <XCircle className="h-4 w-4" />
                  <span>Cancel</span>
                </button>
              </>
            )}

            {sessionState === 'paused' && (
              <>
                <button
                  onClick={handleResumeSession}
                  className="inline-flex items-center gap-2 px-6 py-3.5 rounded-2xl bg-primary text-white font-bold text-sm shadow-lg shadow-primary/30 hover:bg-primary-hover transition-all"
                >
                  <Play className="h-5 w-5" />
                  <span>Resume Session</span>
                </button>

                <button
                  onClick={handleFinishSession}
                  className="inline-flex items-center gap-2 px-6 py-3.5 rounded-2xl bg-emerald-500 text-white font-bold text-sm shadow-lg shadow-emerald-500/30 hover:bg-emerald-600 transition-all"
                >
                  <CheckCircle2 className="h-5 w-5" />
                  <span>Finish Session</span>
                </button>

                <button
                  onClick={handleCancelSession}
                  className="inline-flex items-center gap-2 px-4 py-3.5 rounded-2xl glass-panel text-rose-400 hover:text-white hover:bg-rose-500/10 border border-rose-500/30 text-xs font-semibold transition-all"
                >
                  <XCircle className="h-4 w-4" />
                  <span>Cancel</span>
                </button>
              </>
            )}
          </div>

          <div className="w-full pt-6 border-t border-border/60 grid grid-cols-2 gap-4 text-xs">
            <div className="p-3.5 rounded-2xl bg-gray-900/60 border border-gray-800 text-left">
              <div className="text-gray-400">Shield Status</div>
              <div className="font-bold text-emerald-400 flex items-center gap-1.5 mt-0.5">
                <Shield className="h-3.5 w-3.5" />
                <span>Active Shield</span>
              </div>
            </div>

            <div className="p-3.5 rounded-2xl bg-gray-900/60 border border-gray-800 text-left">
              <div className="text-gray-400">Session Distractions</div>
              <div className="font-bold text-white mt-0.5">{distractionCount} Interruptions</div>
            </div>
          </div>
        </div>

        {/* Finished Session Statistics Summary */}
        {summaryData && (
          <div className="max-w-2xl mx-auto p-6 rounded-3xl bg-gradient-to-br from-card via-card to-primary/10 border border-primary/40 space-y-4 shadow-2xl">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-emerald-400 font-bold text-base">
                <Award className="h-5 w-5" />
                <span>Session Summary</span>
              </div>
              <span className="text-xs font-mono uppercase bg-primary/20 text-primary px-3 py-1 rounded-full border border-primary/30 font-semibold">
                Status: {summaryData.status}
              </span>
            </div>

            <div className="grid grid-cols-3 gap-4 text-center">
              <div className="p-3 rounded-2xl bg-gray-900/80 border border-gray-800">
                <div className="text-[11px] text-gray-400">Planned</div>
                <div className="text-lg font-extrabold text-white">{summaryData.plannedMinutes}m</div>
              </div>
              <div className="p-3 rounded-2xl bg-gray-900/80 border border-gray-800">
                <div className="text-[11px] text-gray-400">Actual</div>
                <div className="text-lg font-extrabold text-white">{summaryData.actualMinutes}m</div>
              </div>
              <div className="p-3 rounded-2xl bg-gray-900/80 border border-gray-800">
                <div className="text-[11px] text-gray-400">Distractions</div>
                <div className="text-lg font-extrabold text-white">{summaryData.distractions}</div>
              </div>
            </div>

            {/* Heuristic Focus Score Card */}
            <div className="p-4 rounded-2xl bg-gray-900/90 border border-gray-800 flex items-center justify-between">
              <div>
                <div className="text-xs font-mono uppercase text-primary font-bold">
                  Heuristic Focus Score
                </div>
                <div className="text-[11px] text-gray-400 mt-0.5">
                  {summaryData.explanation}
                </div>
              </div>
              <div className="text-3xl font-black text-white font-mono">
                {summaryData.heuristicScore} <span className="text-xs text-gray-400 font-normal">/ 100</span>
              </div>
            </div>
          </div>
        )}

        {/* Session History Section */}
        <div className="max-w-4xl mx-auto space-y-4">
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <History className="h-5 w-5 text-primary" />
            <span>Session History</span>
          </h2>

          {sessionHistory.length === 0 ? (
            <div className="p-8 text-center rounded-3xl glass-panel border border-border/80 text-xs text-gray-400">
              No focus sessions recorded yet. Start your first session above!
            </div>
          ) : (
            <div className="rounded-3xl glass-panel border border-border/80 overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="bg-gray-900/60 text-gray-400 uppercase font-mono">
                    <tr>
                      <th className="px-6 py-3">Session</th>
                      <th className="px-6 py-3">Duration</th>
                      <th className="px-6 py-3">Status</th>
                      <th className="px-6 py-3">Distractions</th>
                      <th className="px-6 py-3">Heuristic Score</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border/40 text-gray-300">
                    {sessionHistory.map((s, idx) => (
                      <tr key={s.id || idx} className="hover:bg-gray-800/30 transition-colors">
                        <td className="px-6 py-4 font-semibold text-white">{s.session_name}</td>
                        <td className="px-6 py-4 font-mono">{s.actual_duration_minutes || s.target_duration_minutes} mins</td>
                        <td className="px-6 py-4">
                          <span className={`px-2 py-0.5 rounded-full font-mono uppercase text-[10px] ${
                            s.status === 'completed' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-rose-500/20 text-rose-400'
                          }`}>
                            {s.status}
                          </span>
                        </td>
                        <td className="px-6 py-4 font-mono">{s.distraction_count || 0}</td>
                        <td className="px-6 py-4 font-bold font-mono">
                          {s.heuristic_score ?? 85} / 100
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
    </div>
  );
}
