'use client';

import React from 'react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip } from 'recharts';
import { EmptyState } from '../EmptyState';
import { Clock } from 'lucide-react';

interface DataPoint {
  day: string;
  minutes: number;
}

interface FocusTimeChartProps {
  data?: DataPoint[];
}

export function FocusTimeChart({ data = [] }: FocusTimeChartProps) {
  if (!data || data.length === 0) {
    return (
      <EmptyState
        icon={Clock}
        title="No Focus Session Data"
        description="Focus duration per day will appear here after you log your first session."
        actionText="Start Focus Session"
        actionHref="/focus"
      />
    );
  }

  return (
    <div className="h-64 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data}>
          <XAxis dataKey="day" stroke="#6b7280" fontSize={12} tickLine={false} />
          <YAxis stroke="#6b7280" fontSize={12} tickLine={false} unit="m" />
          <Tooltip
            contentStyle={{ backgroundColor: '#111827', borderColor: '#1f2937', borderRadius: '12px', color: '#fff' }}
          />
          <Bar dataKey="minutes" fill="#6366f1" radius={[6, 6, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
