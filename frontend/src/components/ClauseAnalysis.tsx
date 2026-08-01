'use client';

import React, { useState } from 'react';
import { FileText, CornerDownRight, MapPin } from 'lucide-react';
import { ClauseItem, NegotiationItem, Coordinate } from '../types';

interface ClauseAnalysisProps {
  clauses: ClauseItem[];
  negotiations: NegotiationItem[];
  onLocate: (coordinates: Coordinate[], id: string) => void;
  activeClauseId: string | null;
}

export default function ClauseAnalysis({
  clauses,
  negotiations,
  onLocate,
  activeClauseId
}: ClauseAnalysisProps) {
  const [userSelectedIdx, setUserSelectedIdx] = useState<number | null>(null);

  const activeIdx = activeClauseId ? clauses.findIndex((c) => c.name === activeClauseId) : -1;
  const selectedIdx = userSelectedIdx !== null 
    ? userSelectedIdx 
    : (activeIdx !== -1 ? activeIdx : 0);

  if (clauses.length === 0) {
    return (
      <div className="p-8 text-center text-xs text-slate-500 bg-slate-900/30 border border-slate-800 rounded-xl">
        No clauses extracted for analysis.
      </div>
    );
  }

  const selectedClause = clauses[selectedIdx];
  const hasCoords = selectedClause.coordinates && selectedClause.coordinates.length > 0;

  // Find cross-referenced negotiation suggestion for this clause
  const negotiation = negotiations.find(
    (n) => n.clause_name.toLowerCase() === selectedClause.name.toLowerCase()
  );

  return (
    <div className="grid md:grid-cols-3 gap-6 h-full bg-slate-900/30 border border-slate-800 rounded-xl p-4">
      {/* Left List of Clauses */}
      <div className="md:col-span-1 border-r border-slate-800/80 pr-4 space-y-1.5 overflow-y-auto max-h-[360px] md:max-h-full">
        <h4 className="text-[10px] font-bold text-slate-500 uppercase tracking-widest px-2 mb-2">
          Extracted Clauses
        </h4>
        {clauses.map((clause, idx) => {
          const isActive = selectedIdx === idx;
          return (
            <button
              key={clause.name}
              onClick={() => setUserSelectedIdx(idx)}
              className={`w-full text-left px-3 py-2 rounded-lg text-xs font-semibold flex items-center gap-2 border transition-all cursor-pointer ${
                isActive
                  ? 'bg-indigo-500/10 border-indigo-500/30 text-indigo-400'
                  : 'bg-slate-900/40 border-slate-800/60 text-slate-400 hover:text-slate-200'
              }`}
            >
              <FileText className="w-3.5 h-3.5 shrink-0" />
              <span className="truncate">{clause.name}</span>
            </button>
          );
        })}
      </div>

      {/* Right Details Panel */}
      <div className="md:col-span-2 space-y-4 text-xs overflow-y-auto max-h-[380px] md:max-h-full">
        {/* Clause Title & Coordinate Locator */}
        <div className="flex items-start justify-between gap-4">
          <div>
            <h3 className="text-sm font-extrabold text-slate-200">{selectedClause.name}</h3>
            <span className="text-[10px] text-slate-500 font-mono">
              Confidence Score: {Math.round(selectedClause.confidence * 100)}%
            </span>
          </div>
          {hasCoords && (
            <button
              onClick={() => onLocate(selectedClause.coordinates!, selectedClause.name)}
              className="flex items-center gap-1.5 px-2 py-1 bg-indigo-500/10 hover:bg-indigo-500/20 border border-indigo-500/20 text-indigo-400 text-[10px] font-bold rounded-lg cursor-pointer transition-all shrink-0"
            >
              <MapPin className="w-3.5 h-3.5" /> Page {selectedClause.coordinates![0].page + 1}
            </button>
          )}
        </div>

        {/* Verbatim snippet */}
        <div>
          <span className="font-semibold text-slate-400 block mb-1">Verbatim Clause Text:</span>
          <div className="border border-slate-800 bg-slate-950/80 p-3 rounded font-mono text-[10px] text-slate-400 break-words leading-relaxed max-h-[120px] overflow-y-auto">
            &quot;{selectedClause.verbatim_text}&quot;
          </div>
        </div>

        {/* Explanation & Impact */}
        <div className="grid md:grid-cols-2 gap-4">
          <div className="bg-slate-950/30 border border-slate-850 p-3 rounded-lg">
            <span className="font-bold text-slate-300 block mb-1">Plain-English Meaning</span>
            <p className="text-slate-400 leading-normal font-sans">
              {selectedClause.reasoning || 'The AI identifies this clause as managing key parameters of the agreement.'}
            </p>
          </div>
          <div className="bg-slate-950/30 border border-slate-850 p-3 rounded-lg">
            <span className="font-bold text-slate-300 block mb-1">Business Context</span>
            <p className="text-slate-400 leading-normal font-sans">
              Provides regulatory, transactional, or legal framing defining liabilities, periods, or terms.
            </p>
          </div>
        </div>

        {/* Cross-referenced Negotiation Proposal */}
        {negotiation && (
          <div className="border border-indigo-500/20 bg-indigo-500/5 p-4 rounded-lg space-y-3">
            <div className="flex items-center justify-between border-b border-indigo-500/10 pb-2">
              <span className="font-bold text-indigo-300 text-xs flex items-center gap-1.5">
                <CornerDownRight className="w-3.5 h-3.5" /> Negotiation Redline Suggestion
              </span>
              <span className="px-2 py-0.5 rounded text-[9px] font-bold bg-indigo-500/20 text-indigo-300 border border-indigo-400/20">
                Risk Reduction: {negotiation.risk_reduction}
              </span>
            </div>

            {/* Side-by-Side Clause Redlining */}
            <div className="grid md:grid-cols-2 gap-3 text-[10px]">
              <div>
                <span className="font-semibold text-red-400/80 block mb-1">Original Provisions</span>
                <div className="bg-red-500/5 border border-red-500/15 p-2 rounded text-slate-400 font-mono break-words leading-relaxed max-h-[100px] overflow-y-auto">
                  &quot;{negotiation.current_clause}&quot;
                </div>
              </div>
              <div>
                <span className="font-semibold text-emerald-400/80 block mb-1">Proposed Redline</span>
                <div className="bg-emerald-500/5 border border-emerald-500/15 p-2 rounded text-slate-300 font-mono break-words leading-relaxed max-h-[100px] overflow-y-auto">
                  &quot;{negotiation.suggested_clause}&quot;
                </div>
              </div>
            </div>

            <div className="text-[10px] text-slate-400 font-sans leading-normal">
              <span className="font-semibold text-slate-300">Strategy Rationale:</span> {negotiation.reason}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
