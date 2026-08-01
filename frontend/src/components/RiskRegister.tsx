'use client';

import React, { useState } from 'react';
import { Search, AlertTriangle, AlertCircle, AlertOctagon, HelpCircle, ShieldCheck, ChevronDown, ChevronUp, MapPin } from 'lucide-react';
import { RiskFlagItem, Coordinate } from '../types';

interface RiskRegisterProps {
  risks: RiskFlagItem[];
  onLocate: (coordinates: Coordinate[], id: string) => void;
  activeRiskId: string | null;
}

export default function RiskRegister({ risks, onLocate, activeRiskId }: RiskRegisterProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [severityFilter, setSeverityFilter] = useState<string>('All');
  const [expandedId, setExpandedId] = useState<string | null>(null);

  // Map severity levels to hierarchy numbers for sorting
  const severityValue = { Critical: 4, High: 3, Medium: 2, Low: 1, Safe: 0 };

  const getSeverityIcon = (level: string) => {
    switch (level) {
      case 'Critical':
        return <AlertOctagon className="w-4 h-4 text-red-500 shrink-0" />;
      case 'High':
        return <AlertTriangle className="w-4 h-4 text-orange-400 shrink-0" />;
      case 'Medium':
        return <AlertCircle className="w-4 h-4 text-amber-500 shrink-0" />;
      case 'Low':
        return <HelpCircle className="w-4 h-4 text-emerald-400 shrink-0" />;
      case 'Safe':
        return <ShieldCheck className="w-4 h-4 text-teal-400 shrink-0" />;
      default:
        return <HelpCircle className="w-4 h-4 text-slate-400 shrink-0" />;
    }
  };

  const getSeverityBadge = (level: string) => {
    switch (level) {
      case 'Critical':
        return 'bg-red-500/10 border-red-500/20 text-red-400';
      case 'High':
        return 'bg-orange-500/10 border-orange-500/20 text-orange-400';
      case 'Medium':
        return 'bg-amber-500/10 border-amber-500/20 text-amber-400';
      case 'Low':
        return 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400';
      case 'Safe':
        return 'bg-teal-500/10 border-teal-500/20 text-teal-400';
      default:
        return 'bg-slate-500/10 border-slate-500/20 text-slate-400';
    }
  };

  const toggleRow = (id: string) => {
    setExpandedId(expandedId === id ? null : id);
  };

  // Filter risks based on query and severity selection
  const filteredRisks = risks
    .filter((risk) => {
      const matchesSearch =
        risk.clause_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        risk.category.toLowerCase().includes(searchQuery.toLowerCase()) ||
        risk.reasoning.toLowerCase().includes(searchQuery.toLowerCase()) ||
        risk.text.toLowerCase().includes(searchQuery.toLowerCase());
      
      const matchesSeverity = severityFilter === 'All' || risk.severity === severityFilter;
      
      return matchesSearch && matchesSeverity;
    })
    .sort((a, b) => severityValue[b.severity] - severityValue[a.severity]); // Sort by highest severity first

  return (
    <div className="flex flex-col h-full bg-slate-900/30 border border-slate-800 rounded-xl overflow-hidden">
      {/* Header and filters */}
      <div className="p-4 bg-slate-950/40 border-b border-slate-800 space-y-3">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-bold text-slate-200">Contract Risk Register</h3>
          <span className="text-xs text-slate-500 font-mono">Total Flags: {risks.length}</span>
        </div>

        {/* Search bar */}
        <div className="relative">
          <Search className="absolute left-2.5 top-2.5 w-4 h-4 text-slate-500" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search risks, clauses, or text..."
            className="w-full pl-9 pr-4 py-1.5 text-xs bg-slate-950 border border-slate-800 rounded-lg focus:outline-none focus:border-indigo-500 text-slate-200"
          />
        </div>

        {/* Filter buttons */}
        <div className="flex flex-wrap gap-1.5">
          {['All', 'Critical', 'High', 'Medium', 'Low', 'Safe'].map((level) => {
            const isActive = severityFilter === level;
            return (
              <button
                key={level}
                onClick={() => setSeverityFilter(level)}
                className={`px-2.5 py-0.5 rounded text-[10px] font-semibold border transition-colors cursor-pointer ${
                  isActive
                    ? 'bg-indigo-500/10 border-indigo-500/30 text-indigo-400'
                    : 'bg-slate-900 border-slate-800 text-slate-400 hover:text-slate-200'
                }`}
              >
                {level}
              </button>
            );
          })}
        </div>
      </div>

      {/* Risk list */}
      <div className="flex-1 overflow-y-auto divide-y divide-slate-800/60 max-h-[400px]">
        {filteredRisks.length > 0 ? (
          filteredRisks.map((risk, index) => {
            const riskId = `${risk.clause_name}-${index}`;
            const isExpanded = expandedId === riskId || activeRiskId === riskId;
            const hasCoords = risk.coordinates && risk.coordinates.length > 0;

            return (
              <div
                key={riskId}
                className={`transition-colors duration-150 ${
                  isExpanded ? 'bg-slate-900/40' : 'hover:bg-slate-950/20'
                }`}
              >
                {/* Row Summary */}
                <div
                  onClick={() => toggleRow(riskId)}
                  className="px-4 py-3 flex items-center justify-between cursor-pointer text-xs"
                >
                  <div className="flex items-center gap-3 min-w-0 pr-4">
                    {getSeverityIcon(risk.severity)}
                    <div className="min-w-0">
                      <div className="font-semibold text-slate-200 truncate">
                        {risk.category}
                      </div>
                      <div className="text-[10px] text-slate-400 mt-0.5 truncate">
                        Clause: {risk.clause_name}
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-2 shrink-0">
                    <span className={`px-2 py-0.5 rounded text-[9px] font-bold border ${getSeverityBadge(risk.severity)}`}>
                      {risk.severity}
                    </span>
                    {isExpanded ? <ChevronUp className="w-3.5 h-3.5 text-slate-500" /> : <ChevronDown className="w-3.5 h-3.5 text-slate-500" />}
                  </div>
                </div>

                {/* Expanded Details */}
                {isExpanded && (
                  <div className="px-4 pb-4 pt-1 text-[11px] text-slate-300 space-y-3 bg-slate-950/40 border-t border-slate-900/60">
                    <div>
                      <span className="font-semibold text-slate-400 block mb-1">Reasoning:</span>
                      <p className="leading-relaxed font-sans">{risk.reasoning}</p>
                    </div>

                    <div>
                      <span className="font-semibold text-slate-400 block mb-1">Verbatim Content Snippet:</span>
                      <blockquote className="border-l-2 border-slate-800 bg-slate-950/80 px-2.5 py-1.5 rounded font-mono text-[10px] text-slate-400 break-words leading-normal max-h-[100px] overflow-y-auto">
                        &quot;{risk.text}&quot;
                      </blockquote>
                    </div>

                    <div>
                      <span className="font-semibold text-slate-400 block mb-1">Suggested Mitigation:</span>
                      <p className="leading-relaxed font-sans text-indigo-300">{risk.suggested_action}</p>
                    </div>

                    {/* Meta and Locater */}
                    <div className="flex items-center justify-between pt-2 border-t border-slate-900">
                      <div className="text-[10px] text-slate-500 font-mono">
                        Confidence: {Math.round(risk.confidence * 100)}%
                      </div>
                      {hasCoords && (
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            onLocate(risk.coordinates!, riskId);
                          }}
                          className="flex items-center gap-1.5 px-2.5 py-1 bg-indigo-500/10 hover:bg-indigo-500/20 border border-indigo-500/20 text-indigo-400 text-[10px] font-bold rounded-lg cursor-pointer transition-all"
                        >
                          <MapPin className="w-3 h-3" /> Locate in Document (Page {risk.coordinates![0].page + 1})
                        </button>
                      )}
                    </div>
                  </div>
                )}
              </div>
            );
          })
        ) : (
          <div className="p-8 text-center text-xs text-slate-500">
            No risks found matching criteria.
          </div>
        )}
      </div>
    </div>
  );
}
