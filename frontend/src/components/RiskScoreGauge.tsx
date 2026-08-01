'use client';

import React from 'react';

interface RiskScoreGaugeProps {
  score: number;
  decision: string;
}

export default function RiskScoreGauge({ score, decision }: RiskScoreGaugeProps) {
  // Radius of the circle
  const radius = 60;
  const strokeWidth = 10;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (score / 100) * circumference;

  // Determine colors based on risk severity
  const getRiskColors = (val: number) => {
    if (val <= 25) {
      return {
        text: 'text-emerald-400',
        stroke: 'stroke-emerald-500',
        bg: 'bg-emerald-500/10',
        glow: 'shadow-emerald-500/20',
        label: 'Low Risk'
      };
    } else if (val <= 55) {
      return {
        text: 'text-amber-400',
        stroke: 'stroke-amber-500',
        bg: 'bg-amber-500/10',
        glow: 'shadow-amber-500/20',
        label: 'Medium Risk'
      };
    } else if (val <= 80) {
      return {
        text: 'text-orange-400',
        stroke: 'stroke-orange-500',
        bg: 'bg-orange-500/10',
        glow: 'shadow-orange-500/20',
        label: 'High Risk'
      };
    } else {
      return {
        text: 'text-rose-400',
        stroke: 'stroke-rose-500',
        bg: 'bg-rose-500/10',
        glow: 'shadow-rose-500/20',
        label: 'Critical Risk'
      };
    }
  };

  const colors = getRiskColors(score);

  return (
    <div className="flex flex-col items-center justify-center p-4 bg-slate-900/30 border border-slate-800 rounded-xl relative overflow-hidden select-none">
      {/* Label indicator */}
      <span className="text-xs uppercase tracking-widest text-slate-500 font-bold mb-3">
        Risk Assessment
      </span>

      {/* SVG Circular Dial */}
      <div className="relative w-36 h-36 flex items-center justify-center">
        <svg className="w-full h-full transform -rotate-90" viewBox="0 0 140 140">
          {/* Background circle track */}
          <circle
            cx="70"
            cy="70"
            r={radius}
            className="stroke-slate-800 fill-none"
            strokeWidth={strokeWidth}
          />
          {/* Animated score progress ring */}
          <circle
            cx="70"
            cy="70"
            r={radius}
            className={`${colors.stroke} fill-none transition-all duration-1000 ease-out`}
            strokeWidth={strokeWidth}
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
          />
        </svg>

        {/* Center overlay texts */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className={`text-3xl font-extrabold font-mono tracking-tight ${colors.text}`}>
            {score}
          </span>
          <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider mt-0.5">
            / 100
          </span>
        </div>
      </div>

      {/* Tiers indicator */}
      <div className="mt-4 text-center">
        <div className={`text-sm font-extrabold tracking-wide uppercase ${colors.text} px-2.5 py-0.5 rounded-full ${colors.bg} inline-block border border-current/10`}>
          {colors.label}
        </div>
        <p className="text-xs text-slate-400 font-medium mt-2 max-w-[200px] leading-relaxed truncate">
          Recommendation: {decision}
        </p>
      </div>
    </div>
  );
}
