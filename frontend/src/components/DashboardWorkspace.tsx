'use client';

import React, { useState, useEffect } from 'react';
import { FileText, Award, Clock, Download, ChevronRight, FileCode, LogOut, Check, ShieldCheck, Zap, Brain } from 'lucide-react';
import confetti from 'canvas-confetti';

import { DocumentAnalysisResponse, Coordinate } from '../types';
import { getBackendUrl } from '../lib/api';
import PdfViewer from './PdfViewer';
import RiskScoreGauge from './RiskScoreGauge';
import RiskRegister from './RiskRegister';
import ClauseAnalysis from './ClauseAnalysis';
import EntityGrid from './EntityGrid';
import AiChat from './AiChat';
import HindsightMemoryInspector from './HindsightMemoryInspector';

interface DashboardWorkspaceProps {
  data: DocumentAnalysisResponse;
  onReset: () => void;
  apiKey: string;
}

export default function DashboardWorkspace({ data, onReset, apiKey }: DashboardWorkspaceProps) {
  const [activeTab, setActiveTab] = useState<'summary' | 'memory' | 'risks' | 'clauses' | 'entities' | 'compliance' | 'chat'>('summary');
  const [activeHighlightId, setActiveHighlightId] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState(0);

  const BACKEND_URL = getBackendUrl();

  // Helper to download report files (now inside component scope)
  async function downloadReport(format: 'pdf' | 'csv' | 'json') {
    const url = `${BACKEND_URL}/api/download/${data.document_id}/report?format=${format}`;
    try {
      const response = await fetch(url);
      if (!response.ok) throw new Error('Network response was not ok');
      const blob = await response.blob();
      const fileName = `${data.filename || 'report'}.${format}`;
      const link = document.createElement('a');
      link.href = window.URL.createObjectURL(blob);
      link.download = fileName;
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      console.error('Download failed:', err);
      alert('Failed to download the report. Please try again later.');
    }
  }

  useEffect(() => {
    // If the final recommendation is Proceed or Proceed after Negotiation, trigger celebratory confetti!
    if (data.decision === 'Proceed' || data.decision === 'Proceed after Negotiation') {
      confetti({
        particleCount: 80,
        spread: 60,
        origin: { y: 0.8 },
        colors: ['#6366f1', '#10b981', '#a855f7']
      });
    }
  }, [data.decision]);

  // Aggregate highlights for the PDF viewer
  // We collect coordinates from risks, clauses, and negotiation items and group them
  const highlights = [
    ...data.clauses.map((c) => ({
      id: c.name,
      name: c.name,
      severity: (data.risk_flags.find((r) => r.clause_name === c.name)?.severity || 'Safe') as 'Critical' | 'High' | 'Medium' | 'Low' | 'Safe',
      coordinates: c.coordinates || []
    })),
    ...data.risk_flags
      .filter((r) => !data.clauses.some((c) => c.name === r.clause_name)) // Avoid duplicates
      .map((r, idx) => ({
        id: `${r.clause_name}-risk-${idx}`,
        name: r.category,
        severity: r.severity,
        coordinates: r.coordinates || []
      }))
  ];

  // Callback when user clicks "Locate in Document" on child grids
  const handleLocateCoordinate = (coordinates: Coordinate[], id: string) => {
    if (coordinates && coordinates.length > 0) {
      setCurrentPage(coordinates[0].page);
      setActiveHighlightId(id);
      
      // Auto-clear active highlights outline after a few seconds so it doesn't clutter the page
      setTimeout(() => {
        setActiveHighlightId(null);
      }, 5000);
    }
  };

  // Helper mapping for decision color
  const getDecisionBadge = (decision: string) => {
    switch (decision) {
      case 'Proceed':
        return 'bg-emerald-500/10 border-emerald-500/25 text-emerald-400';
      case 'Proceed after Negotiation':
        return 'bg-amber-500/10 border-amber-500/25 text-amber-400';
      case 'Requires Legal Review':
        return 'bg-orange-500/10 border-orange-500/25 text-orange-400';
      case 'Reject':
        return 'bg-red-500/10 border-red-500/25 text-red-400';
      default:
        return 'bg-slate-500/10 border-slate-500/25 text-slate-400';
    }
  };

  return (
    <div className="max-w-[1600px] mx-auto px-4 py-6 flex flex-col gap-6">
      {/* Top Navigation / Action Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-4 select-none">
        <div>
          <h2 className="text-xl font-bold text-slate-200 flex items-center gap-2">
            <FileText className="w-5.5 h-5.5 text-indigo-400" />
            <span>DocPilot Analytics Console</span>
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            File: <span className="text-slate-400 font-medium font-mono">{data.filename}</span> &bull; ID: <span className="text-slate-500 font-mono">{data.document_id.substring(0, 8)}...</span>
          </p>
        </div>

        {/* Action button groupings */}
        <div className="flex items-center gap-2">
          {/* Download Buttons */}
          <div className="flex gap-2">
            <button
              onClick={() => downloadReport('pdf')}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-indigo-650 hover:bg-indigo-550 text-white text-xs font-semibold rounded-lg transition-colors cursor-pointer shadow-lg shadow-indigo-500/10"
            >
              <Download className="w-3.5 h-3.5" /> PDF Report
            </button>
            <button
              onClick={() => downloadReport('csv')}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-900 hover:bg-slate-800 border border-slate-800 hover:border-slate-700 text-slate-300 text-xs font-semibold rounded-lg transition-colors cursor-pointer"
            >
              <Download className="w-3.5 h-3.5" /> Risks CSV
            </button>
            <button
              onClick={() => downloadReport('json')}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-900 hover:bg-slate-800 border border-slate-800 hover:border-slate-700 text-slate-300 text-xs font-semibold rounded-lg transition-colors cursor-pointer"
            >
              <FileCode className="w-3.5 h-3.5" /> Full JSON
            </button>
          </div>

          <div className="w-px h-6 bg-slate-800 mx-1"></div>

          {/* Reset button */}
          <button
            onClick={onReset}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-red-600/10 hover:bg-red-600/25 border border-red-500/25 text-red-400 text-xs font-bold rounded-lg transition-all cursor-pointer"
          >
            <LogOut className="w-3.5 h-3.5" /> Close Analysis
          </button>
        </div>
      </div>

      {/* Summary Metrics Row */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-4">
        {/* Risk score gauge card */}
        <div className="col-span-2 lg:col-span-1">
          <RiskScoreGauge score={data.overall_risk_score} decision={data.decision} />
        </div>

        {/* Decision Recommendations Card */}
        <div className="glass-panel p-4 rounded-xl flex flex-col justify-between border border-slate-850">
          <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest block mb-2">
            AI Recommendation Decision
          </span>
          <div>
            <div className={`inline-block px-3 py-1 text-xs font-extrabold tracking-wide uppercase rounded-full border ${getDecisionBadge(data.decision)}`}>
              {data.decision}
            </div>
            <p className="text-xs text-slate-400 mt-3 leading-relaxed font-sans line-clamp-4">
              {data.recommendations[0] || 'Requires minor adjustments to cap liability clauses.'}
            </p>
          </div>
          <div className="text-[10px] text-indigo-400 font-bold tracking-wide uppercase mt-2 flex items-center">
            View Actions below <ChevronRight className="w-3.5 h-3.5" />
          </div>
        </div>

        {/* Document Metadata Card */}
        <div className="glass-panel p-4 rounded-xl flex flex-col justify-between border border-slate-850">
          <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest block mb-1">
            Pipeline Analytics
          </span>
          <div className="space-y-2 mt-2">
            <div className="flex justify-between text-xs">
              <span className="text-slate-400">Doc Type</span>
              <span className="text-slate-200 font-semibold">{data.document_type}</span>
            </div>
            <div className="flex justify-between text-xs">
              <span className="text-slate-400">Class Confidence</span>
              <span className="text-slate-200 font-semibold font-mono">{Math.round(data.confidence * 100)}%</span>
            </div>
            <div className="flex justify-between text-xs">
              <span className="text-slate-400">Total Pages</span>
              <span className="text-slate-200 font-semibold font-mono">{data.pages_count} page(s)</span>
            </div>
            <div className="flex justify-between text-xs">
              <span className="text-slate-400">Analysis Duration</span>
              <span className="text-slate-200 font-semibold font-mono">{data.processing_time_sec}s</span>
            </div>
          </div>
          <div className="text-[9px] text-slate-500 font-mono border-t border-slate-900 pt-1 mt-2">
            Processor: Gemini-2.5-Flash
          </div>
        </div>

        {/* Extraction Audit Card */}
        <div className="glass-panel p-4 rounded-xl flex flex-col justify-between border border-slate-850">
          <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest block mb-1">
            Extraction audit
          </span>
          <div className="space-y-2 mt-2">
            <div className="flex justify-between text-xs">
              <span className="text-slate-400">Entities Extracted</span>
              <span className="text-slate-200 font-semibold font-mono">
                {(data.entities?.company_names?.length || 0) + (data.entities?.person_names?.length || 0) + (data.entities?.jurisdiction ? 1 : 0)}
              </span>
            </div>
            <div className="flex justify-between text-xs">
              <span className="text-slate-400">Critical Risks Flagged</span>
              <span className={`font-semibold font-mono ${data.risk_flags.filter(r => r.severity === 'Critical').length > 0 ? 'text-red-400' : 'text-slate-200'}`}>
                {data.risk_flags.filter((r) => r.severity === 'Critical').length}
              </span>
            </div>
            <div className="flex justify-between text-xs">
              <span className="text-slate-400">Compliance Gaps</span>
              <span className={`font-semibold font-mono ${data.missing_clauses.filter(m => !m.is_present).length > 0 ? 'text-amber-400' : 'text-slate-200'}`}>
                {data.missing_clauses.filter((m) => !m.is_present).length}
              </span>
            </div>
          </div>
          <div className="text-[9px] text-slate-500 font-mono border-t border-slate-900 pt-1 mt-2">
            Verbatim Snippet Matches Verified
          </div>
        </div>

        {/* Business Value Saved Card */}
        <div className="glass-panel p-4 rounded-xl flex flex-col justify-between border border-indigo-500/10 bg-indigo-500/5 col-span-2 md:col-span-4 lg:col-span-1">
          <span className="text-[10px] font-bold text-indigo-400 uppercase tracking-widest block mb-2">
            Efficiency metric
          </span>
          <div>
            <div className="flex items-baseline gap-1 text-slate-200">
              <span className="text-3xl font-extrabold font-mono tracking-tight text-indigo-300">
                ~{(
                  Math.max(0.5, (data.pages_count * 0.4) + (data.clauses.length * 0.15) + (data.risk_flags.length * 0.1))
                ).toFixed(1)}
              </span>
              <span className="text-xs font-semibold text-slate-400">Hours Saved</span>
            </div>
            <p className="text-[11px] text-slate-400 mt-2 font-sans leading-relaxed">
              Based on {data.pages_count} page(s), {data.clauses.length} clause(s), and {data.risk_flags.length} risk flag(s) vs. standard manual analyst review.
            </p>
          </div>
          <div className="flex items-center gap-1 text-[10px] text-emerald-400 font-semibold mt-2">
            <Clock className="w-3.5 h-3.5" /> High-speed review
          </div>
        </div>

      </div>

      {/* Main Workspace split panel */}
      <div className="grid lg:grid-cols-12 gap-6 items-start">
        {/* Left Side: PDF viewer (5 columns) */}
        <div className="lg:col-span-5 h-[580px] lg:h-[650px] shrink-0 sticky top-4">
          <PdfViewer
            docId={data.document_id}
            pagesCount={data.pages_count}
            highlights={highlights}
            activeHighlightId={activeHighlightId}
            onHighlightClick={(id) => {
              setActiveHighlightId(id);
              // Auto focus to corresponding Tab
              if (data.clauses.some((c) => c.name === id)) {
                setActiveTab('clauses');
              } else {
                setActiveTab('risks');
              }
            }}
            currentPage={currentPage}
            setCurrentPage={setCurrentPage}
          />
        </div>

        {/* Right Side: Tabbed Details (7 columns) */}
        <div className="lg:col-span-7 flex flex-col h-[580px] lg:h-[650px] bg-slate-900/10 border border-slate-800 rounded-2xl overflow-hidden">
          {/* Tab Selector buttons */}
          <div className="flex border-b border-slate-800 bg-slate-950/40 select-none overflow-x-auto">
            {([
              { id: 'summary', label: 'Executive Summary' },
              { id: 'memory', label: '🧠 Hindsight Memory Engine' },
              { id: 'risks', label: 'Risk Register' },
              { id: 'clauses', label: 'Clause Inspector' },
              { id: 'entities', label: 'Extracted Entities' },
              { id: 'compliance', label: 'Compliance & Impact' },
              { id: 'chat', label: 'AI Q&A Chat' }
            ] as const).map((tab) => {
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`px-5 py-3 text-xs font-bold border-b-2 transition-all cursor-pointer whitespace-nowrap ${
                    isActive
                      ? 'border-indigo-500 text-indigo-400 bg-indigo-500/5'
                      : 'border-transparent text-slate-400 hover:text-slate-200'
                  }`}
                >
                  {tab.label}
                </button>
              );
            })}
          </div>

          {/* Tab Content window */}
          <div className="flex-1 p-6 overflow-y-auto bg-slate-950/15">
            {activeTab === 'summary' && (
              <div className="space-y-6 text-xs text-slate-300">
                {/* Hindsight Memory Recalled Callout Banner */}
                {data.recalled_memories && data.recalled_memories.length > 0 && (
                  <div className="flex items-center justify-between p-3.5 rounded-xl border border-indigo-500/30 bg-indigo-950/30 text-xs">
                    <div className="flex items-center gap-2.5">
                      <div className="w-7 h-7 rounded-lg bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center shrink-0">
                        <Brain className="w-4 h-4 text-indigo-400" />
                      </div>
                      <div>
                        <span className="font-bold text-indigo-300">
                          Hindsight Memory Active:
                        </span>{' '}
                        <span className="text-slate-300">
                          Recalled {data.recalled_memories.length} historical corporate precedents for {data.filename}.
                        </span>
                      </div>
                    </div>
                    <button
                      onClick={() => setActiveTab('memory')}
                      className="px-2.5 py-1 bg-indigo-600 hover:bg-indigo-500 text-white text-[11px] font-bold rounded-md transition cursor-pointer shadow-md shadow-indigo-600/20 shrink-0"
                    >
                      View Memory Engine →
                    </button>
                  </div>
                )}

                {/* Business Overview */}
                <div>
                  <span className="font-bold text-slate-400 uppercase tracking-widest text-[10px] block mb-2">
                    Business Overview
                  </span>
                  <p className="leading-relaxed font-sans text-slate-300 bg-slate-950/40 p-4 rounded-xl border border-slate-900">
                    {data.summary}
                  </p>
                </div>

                <div className="grid md:grid-cols-2 gap-6">
                  {/* Key Findings */}
                  <div>
                    <span className="font-bold text-slate-400 uppercase tracking-widest text-[10px] block mb-2">
                      Key Findings
                    </span>
                    <ul className="space-y-2 bg-slate-950/30 p-4 rounded-xl border border-slate-900 min-h-[140px] leading-relaxed">
                      {data.recommendations.map((rec, i) => (
                        <li key={i} className="flex gap-2 items-start font-sans">
                          <Check className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                          <span>{rec}</span>
                        </li>
                      ))}
                    </ul>
                  </div>

                  {/* Risks overview */}
                  <div>
                    <span className="font-bold text-slate-400 uppercase tracking-widest text-[10px] block mb-2">
                      Exposures / Critical Risks
                    </span>
                    <ul className="space-y-2 bg-slate-950/30 p-4 rounded-xl border border-slate-900 min-h-[140px] leading-relaxed">
                      {data.risk_flags.slice(0, 4).map((risk, i) => (
                        <li key={i} className="flex gap-2 items-start text-red-400 font-sans">
                          <Award className="w-4 h-4 shrink-0 mt-0.5" />
                          <span>
                            <strong className="text-slate-200">{risk.category}</strong>: {risk.suggested_action}
                          </span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>

                {/* Timeline dates */}
                {data.timeline && data.timeline.length > 0 && (
                  <div>
                    <span className="font-bold text-slate-400 uppercase tracking-widest text-[10px] block mb-3">
                      Key Timeline & Dates
                    </span>
                    <div className="grid sm:grid-cols-2 md:grid-cols-3 gap-3">
                      {data.timeline.map((item, idx) => (
                        <div key={idx} className="bg-slate-950/40 p-3 rounded-lg border border-slate-900 flex flex-col justify-between">
                          <span className="font-bold text-indigo-400 text-xs font-mono">{item.date}</span>
                          <span className="text-[10px] text-slate-400 font-medium mt-1 leading-normal truncate" title={item.event}>
                            {item.event}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {activeTab === 'risks' && (
              <RiskRegister
                risks={data.risk_flags}
                onLocate={handleLocateCoordinate}
                activeRiskId={activeHighlightId}
              />
            )}

            {activeTab === 'clauses' && (
              <ClauseAnalysis
                clauses={data.clauses}
                negotiations={data.negotiation_suggestions}
                onLocate={handleLocateCoordinate}
                activeClauseId={activeHighlightId}
              />
            )}

            {activeTab === 'entities' && (
              <EntityGrid entities={data.entities} />
            )}

            {activeTab === 'compliance' && (
              <div className="space-y-6">
                {/* Compliance Audit Checklist */}
                <div>
                  <h4 className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-3 flex items-center gap-1.5">
                    <ShieldCheck className="w-3.5 h-3.5 text-indigo-400" /> Mandatory Standard Provisions Audit
                  </h4>
                  <div className="grid sm:grid-cols-2 gap-3">
                    {data.missing_clauses.map((item, idx) => (
                      <div key={idx} className="bg-slate-950/30 border border-slate-850 p-4 rounded-xl flex flex-col justify-between">
                        <div className="flex items-center justify-between gap-2 mb-2">
                          <span className="font-bold text-slate-200 text-xs">{item.clause_name}</span>
                          <span className={`px-2 py-0.5 rounded text-[9px] font-bold border ${item.is_present ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400' : 'bg-red-500/10 border-red-500/20 text-red-400'}`}>
                            {item.is_present ? 'Present' : 'Missing'}
                          </span>
                        </div>
                        <p className="text-xs text-slate-400 font-sans leading-relaxed">
                          {item.recommendation}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Business Impact Insights */}
                {data.business_impact && data.business_impact.length > 0 && (
                  <div className="border-t border-slate-900 pt-6">
                    <h4 className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-3 flex items-center gap-1.5">
                      <Zap className="w-3.5 h-3.5 text-purple-400" /> Operational & Financial Impact Analysis
                    </h4>
                    <div className="grid sm:grid-cols-2 gap-3">
                      {data.business_impact.map((item, idx) => (
                        <div key={idx} className="bg-slate-950/30 border border-slate-850 p-4 rounded-xl flex flex-col justify-between">
                          <div className="flex items-center justify-between gap-2 mb-2">
                            <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 font-mono">
                              Exposure: {item.exposure}
                            </span>
                            <span className={`px-2 py-0.5 rounded text-[9px] font-bold border ${item.priority === 'Critical' || item.priority === 'High' ? 'bg-red-500/10 border-red-500/20 text-red-400' : 'bg-amber-500/10 border-amber-500/20 text-amber-400'}`}>
                              Priority: {item.priority}
                            </span>
                          </div>
                          <p className="text-xs text-slate-300 font-sans leading-relaxed">
                            {item.explanation}
                          </p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {activeTab === 'memory' && (
              <HindsightMemoryInspector
                data={data}
                apiKey={apiKey}
              />
            )}

            {activeTab === 'chat' && (
              <AiChat
                documentId={data.document_id}
                apiKey={apiKey}
                onLocate={handleLocateCoordinate}
              />
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

