'use client';

import React from 'react';
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip } from 'recharts';
import { EmptyState } from '../EmptyState';
import { Repeat } from 'lucide-react';

interface SwitchData {
  time: string;
  switches: number;
}

interface AppSwitchingChartProps {
  data?: SwitchData[];
}

export function AppSwitchingChart({ data = [] }: AppSwitchingChartProps) {
  if (!data || data.length === 0) {
    return (
      <EmptyState
        icon={Repeat}
        title="No App Switch Data"
        description="App switching frequency graph will appear once background collector telemetry is active."
        actionText="View Privacy Settings"
        actionHref="/settings"
      />
    );
  }

  return (
    <div className="h-64 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data}>
          <XAxis dataKey="time" stroke="#6b7280" fontSize={12} tickLine={false} />
          <YAxis stroke="#6b7280" fontSize={12} tickLine={false} />
          <Tooltip contentStyle={{ backgroundColor: '#111827', borderColor: '#1f2937', borderRadius: '12px' }} />
          <Line type="monotone" dataKey="switches" stroke="#06b6d4" strokeWidth={3} dot={{ r: 4 }} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
