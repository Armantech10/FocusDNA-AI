'use client';

import React from 'react';
import { Target, Zap, ShieldCheck } from 'lucide-react';

interface FocusScoreGaugeProps {
  score?: number | null;
  evaluationType?: string;
  explanation?: string;
  hasData?: boolean;
}

export function FocusScoreGauge({
  score = null,
  evaluationType = 'heuristic',
  explanation = 'Start a focus session or log activity to compute your rule-based focus score.',
  hasData = false
}: FocusScoreGaugeProps) {
  if (!hasData || score === null) {
    return (
      <div className="flex flex-col items-center justify-center p-6 rounded-3xl glass-panel border border-border/80 text-center space-y-4">
        <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-gray-900 border border-gray-800 text-gray-500">
          <Zap className="h-8 w-8" />
        </div>
        <div className="space-y-1">
          <div className="text-xl font-bold text-white">No Focus Score Yet</div>
          <p className="text-xs text-gray-400 max-w-xs">{explanation}</p>
        </div>
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[11px] font-mono bg-gray-900 text-gray-400 border border-gray-800">
          <span>Engine: Rule-Based Heuristic</span>
        </div>
      </div>
    );
  }

  let strokeColor = '#10b981'; // Green
  let statusLabel = 'Optimal Focus';
  if (score < 60) {
    strokeColor = '#f43f5e'; // Red
    statusLabel = 'Attention Loss Risk';
  } else if (score < 75) {
    strokeColor = '#f59e0b'; // Amber
    statusLabel = 'Moderate Focus';
  }

  const radius = 75;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (score / 100) * circumference;

  return (
    <div className="flex flex-col items-center justify-center p-6 rounded-3xl glass-panel border border-border/80 text-center">
      <div className="relative flex items-center justify-center w-48 h-48">
        <svg className="w-full h-full transform -rotate-90" viewBox="0 0 200 200">
          <circle
            cx="100"
            cy="100"
            r={radius}
            stroke="rgba(255, 255, 255, 0.08)"
            strokeWidth="14"
            fill="transparent"
          />
          <circle
            cx="100"
            cy="100"
            r={radius}
            stroke={strokeColor}
            strokeWidth="14"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            fill="transparent"
            className="transition-all duration-1000 ease-out"
          />
        </svg>

        <div className="absolute flex flex-col items-center justify-center">
          <span className="text-4xl font-black tracking-tight text-white">{score}</span>
          <span className="text-xs uppercase font-mono tracking-widest text-gray-400 mt-0.5">/ 100</span>
          <span className="mt-2 text-[11px] font-semibold px-2.5 py-0.5 rounded-full" style={{ backgroundColor: `${strokeColor}20`, color: strokeColor }}>
            {statusLabel}
          </span>
        </div>
      </div>

      <div className="mt-4 space-y-2 max-w-xs">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[11px] font-mono bg-gray-900/80 text-gray-300 border border-gray-800">
          <span className="w-2 h-2 rounded-full bg-primary animate-pulse" />
          <span>Engine: <strong className="text-white uppercase">{evaluationType}</strong></span>
        </div>
        <p className="text-xs text-gray-400 italic leading-relaxed">
          {explanation}
        </p>
      </div>
    </div>
  );
}
