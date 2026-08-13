'use client';

import React from 'react';
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip } from 'recharts';
import { EmptyState } from '../EmptyState';
import { Activity } from 'lucide-react';

interface ScoreTrendData {
  time: string;
  score: number;
}

interface FocusScoreTrendChartProps {
  data?: ScoreTrendData[];
}

export function FocusScoreTrendChart({ data = [] }: FocusScoreTrendChartProps) {
  if (!data || data.length === 0) {
    return (
      <EmptyState
        icon={Activity}
        title="No Focus Score History"
        description="Focus score trend history over time will be computed as activity events are evaluated."
        actionText="Start Focus Session"
        actionHref="/focus"
      />
    );
  }

  return (
    <div className="h-64 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data}>
          <defs>
            <linearGradient id="scoreGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#6366f1" stopOpacity={0.4}/>
              <stop offset="95%" stopColor="#6366f1" stopOpacity={0}/>
            </linearGradient>
          </defs>
          <XAxis dataKey="time" stroke="#6b7280" fontSize={12} tickLine={false} />
          <YAxis stroke="#6b7280" fontSize={12} domain={[0, 100]} tickLine={false} />
          <Tooltip contentStyle={{ backgroundColor: '#111827', borderColor: '#1f2937', borderRadius: '12px', color: '#fff' }} />
          <Area type="monotone" dataKey="score" stroke="#6366f1" strokeWidth={3} fillOpacity={1} fill="url(#scoreGradient)" />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
