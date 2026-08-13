'use client';

import React from 'react';
import { ResponsiveContainer, PieChart, Pie, Cell, Tooltip } from 'recharts';
import { EmptyState } from '../EmptyState';
import { ShieldAlert } from 'lucide-react';

interface DistractionItem {
  name: string;
  count: number;
  color?: string;
}

interface DistractionChartProps {
  data?: DistractionItem[];
}

const DEFAULT_COLORS = ['#f43f5e', '#f59e0b', '#6366f1', '#06b6d4'];

export function DistractionChart({ data = [] }: DistractionChartProps) {
  if (!data || data.length === 0) {
    return (
      <EmptyState
        icon={ShieldAlert}
        title="Zero Distraction Events Recorded"
        description="Great job! No context switch interruptions or distraction events detected."
        actionText="Launch Focus Timer"
        actionHref="/focus"
      />
    );
  }

  return (
    <div className="h-64 w-full flex items-center justify-center">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            innerRadius={55}
            outerRadius={85}
            paddingAngle={4}
            dataKey="count"
          >
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color || DEFAULT_COLORS[index % DEFAULT_COLORS.length]} />
            ))}
          </Pie>
          <Tooltip contentStyle={{ backgroundColor: '#111827', borderColor: '#1f2937', borderRadius: '12px' }} />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
