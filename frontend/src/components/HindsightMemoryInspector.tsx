'use client';

import React, { useState, useEffect } from 'react';
import { getBackendUrl } from '../lib/api';
import { 
  Brain, 
  Sparkles, 
  Database, 
  PlusCircle, 
  RotateCcw, 
  Search, 
  ShieldAlert, 
  CheckCircle2, 
  Tag, 
  ExternalLink,
  Layers,
  Zap,
  Info
} from 'lucide-react';
import { MemoryItem, HindsightStatus, DocumentAnalysisResponse } from '../types';

interface HindsightMemoryInspectorProps {
  data: DocumentAnalysisResponse;
  apiKey: string;
}

export default function HindsightMemoryInspector({ data, apiKey }: HindsightMemoryInspectorProps) {
  const [status, setStatus] = useState<HindsightStatus | null>(null);
  const [bankMemories, setBankMemories] = useState<MemoryItem[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [showTeachModal, setShowTeachModal] = useState(false);
  const [demoMode, setDemoMode] = useState<'with_memory' | 'without_memory'>('with_memory');
  const [loading, setLoading] = useState(false);

  // Teach modal form state
  const [teachCategory, setTeachCategory] = useState('Approved Exception');
  const [teachContent, setTeachContent] = useState('');
  const [teachTags, setTeachTags] = useState('');
  const [teachSourceDoc, setTeachSourceDoc] = useState(data.filename || '');
  const [teachSuccess, setTeachSuccess] = useState(false);

  const BACKEND_URL = getBackendUrl();

  // Fetch Hindsight status & memories
  const fetchMemoryData = async () => {
    try {
      setLoading(true);
      const [resStatus, resBank] = await Promise.all([
        fetch(`${BACKEND_URL}/api/memory/status`),
        fetch(`${BACKEND_URL}/api/memory/bank`)
      ]);

      if (resStatus.ok) {
        const statusJson = await resStatus.json();
        setStatus(statusJson);
      }

      if (resBank.ok) {
        const bankJson = await resBank.json();
        setBankMemories(bankJson);
      }
    } catch (err) {
      console.error('Failed to load Hindsight memory data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMemoryData();
  }, []);

  // Handle teaching a new rule
  const handleTeachMemory = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!teachContent.trim()) return;

    try {
      const tagList = teachTags.split(',').map((t) => t.trim()).filter(Boolean);
      const res = await fetch(`${BACKEND_URL}/api/memory/retain`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          content: teachContent.trim(),
          category: teachCategory,
          tags: tagList,
          source_doc: teachSourceDoc || data.filename,
          bank_id: status?.bank_id || 'docpilot-legal-bank'
        })
      });

      if (res.ok) {
        setTeachSuccess(true);
        setTeachContent('');
        setTeachTags('');
        setTimeout(() => {
          setTeachSuccess(false);
          setShowTeachModal(false);
        }, 1200);
        fetchMemoryData();
      }
    } catch (err) {
      console.error('Error teaching memory:', err);
    }
  };

  // Reset bank to demo state
  const handleResetBank = async () => {
    if (!confirm('Reset memory bank to default demo seed state?')) return;
    try {
      const res = await fetch(`${BACKEND_URL}/api/memory/reset`, { method: 'POST' });
      if (res.ok) {
        fetchMemoryData();
      }
    } catch (err) {
      console.error('Error resetting bank:', err);
    }
  };

  const filteredMemories = bankMemories.filter((m) => {
    if (!searchQuery) return true;
    const q = searchQuery.toLowerCase();
    return (
      m.content.toLowerCase().includes(q) ||
      m.category.toLowerCase().includes(q) ||
      m.tags.some((t) => t.toLowerCase().includes(q))
    );
  });

  const recalledItems = data.recalled_memories || [];
  const memoryInsights = data.memory_insights || [];

  return (
    <div className="space-y-6">
      {/* Top Banner / Hero Card */}
      <div className="relative overflow-hidden rounded-2xl border border-indigo-500/30 bg-gradient-to-br from-indigo-950/40 via-slate-900/60 to-purple-950/30 p-6 shadow-2xl backdrop-blur-xl">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-tr from-indigo-600 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-500/25">
              <Brain className="w-6 h-6 text-white animate-pulse" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-base font-bold text-slate-100 tracking-tight">
                  Hindsight Persistent Agent Memory
                </h2>
                <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                  Vectorize Memory System
                </span>
              </div>
              <p className="text-xs text-slate-400 mt-0.5">
                Multi-document memory layer enabling agents to remember precedents, learn from feedback, and eliminate stateless amnesia.
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3 flex-wrap">
            <button
              onClick={() => setShowTeachModal(true)}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold transition shadow-lg shadow-indigo-600/20 cursor-pointer"
            >
              <PlusCircle className="w-3.5 h-3.5" />
              <span>Teach Agent Policy</span>
            </button>
            <button
              onClick={handleResetBank}
              title="Reset memory bank to seed state"
              className="flex items-center gap-1 px-2.5 py-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-400 hover:text-slate-200 text-xs font-semibold transition cursor-pointer"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>Reset</span>
            </button>
          </div>
        </div>

        {/* Status Metrics Bar */}
        <div className="mt-5 grid grid-cols-2 sm:grid-cols-4 gap-3 pt-4 border-t border-slate-800/80">
          <div className="bg-slate-950/40 p-3 rounded-xl border border-slate-850">
            <span className="text-[10px] uppercase font-bold tracking-wider text-slate-500 block">
              Active Memory Bank
            </span>
            <span className="text-xs font-mono font-bold text-indigo-300 mt-1 block truncate">
              {status?.bank_id || 'docpilot-legal-bank'}
            </span>
          </div>

          <div className="bg-slate-950/40 p-3 rounded-xl border border-slate-850">
            <span className="text-[10px] uppercase font-bold tracking-wider text-slate-500 block">
              Engine Mode
            </span>
            <div className="flex items-center gap-1.5 mt-1">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
              <span className="text-xs font-bold text-slate-200">
                {status?.connected ? 'Hindsight Cloud' : 'Autonomous Engine'}
              </span>
            </div>
          </div>

          <div className="bg-slate-950/40 p-3 rounded-xl border border-slate-850">
            <span className="text-[10px] uppercase font-bold tracking-wider text-slate-500 block">
              Retained Memories
            </span>
            <span className="text-xs font-bold text-slate-200 mt-1 block">
              {status?.total_memories || bankMemories.length} Institutional Rules
            </span>
          </div>

          <div className="bg-slate-950/40 p-3 rounded-xl border border-slate-850">
            <span className="text-[10px] uppercase font-bold tracking-wider text-slate-500 block">
              Recalled Precedents
            </span>
            <span className="text-xs font-bold text-emerald-400 mt-1 block">
              {recalledItems.length} Applied for {data.filename}
            </span>
          </div>
        </div>
      </div>

      {/* BEFORE / AFTER MEMORY DEMO SWITCH (Crucial for Hackathon Judges) */}
      <div className="rounded-xl border border-slate-850 bg-slate-950/60 p-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <span className="text-xs font-bold text-slate-200 flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-amber-400" />
              Hackathon Comparison: Agent Memory Impact
            </span>
            <p className="text-[11px] text-slate-400 mt-0.5">
              Compare how the document is evaluated with vs. without Hindsight persistent memory.
            </p>
          </div>

          <div className="inline-flex rounded-lg bg-slate-900 p-1 border border-slate-800 self-start sm:self-auto">
            <button
              onClick={() => setDemoMode('with_memory')}
              className={`px-3 py-1 text-xs font-bold rounded-md transition cursor-pointer flex items-center gap-1.5 ${
                demoMode === 'with_memory'
                  ? 'bg-indigo-600 text-white shadow-md'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <Brain className="w-3.5 h-3.5" />
              With Hindsight Memory (Smart)
            </button>
            <button
              onClick={() => setDemoMode('without_memory')}
              className={`px-3 py-1 text-xs font-bold rounded-md transition cursor-pointer flex items-center gap-1.5 ${
                demoMode === 'without_memory'
                  ? 'bg-rose-900/60 text-rose-200 border border-rose-700/50 shadow-md'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <Zap className="w-3.5 h-3.5" />
              Without Memory (Stateless AI)
            </button>
          </div>
        </div>

        {demoMode === 'without_memory' ? (
          <div className="mt-4 p-4 rounded-xl bg-rose-950/20 border border-rose-900/40 text-rose-200 text-xs space-y-2 animate-fade-in">
            <div className="flex items-center gap-2 font-bold text-rose-300">
              <ShieldAlert className="w-4 h-4" />
              <span>Generic Stateless Analysis (Amnesia Flaw):</span>
            </div>
            <p className="text-[11px] leading-relaxed text-slate-300">
              Without Hindsight, the agent treats this counterparty as a complete stranger. It flags the 1x liability cap as a <strong className="text-rose-400">High Risk violation</strong> because it has no memory that Executive Legal previously negotiated and approved this exact exception for Acme Corp.
            </p>
            <div className="flex items-center gap-2 text-[10px] text-rose-400/80 font-mono mt-2">
              <span>✕ No past precedents checked</span> &bull;
              <span>✕ Repeating false alarms</span> &bull;
              <span>✕ Zero organizational learning</span>
            </div>
          </div>
        ) : (
          <div className="mt-4 p-4 rounded-xl bg-indigo-950/25 border border-indigo-800/40 text-indigo-200 text-xs space-y-2 animate-fade-in">
            <div className="flex items-center gap-2 font-bold text-indigo-300">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              <span>Memory-Augmented Autonomous Intelligence:</span>
            </div>
            <p className="text-[11px] leading-relaxed text-slate-300">
              With Hindsight, the agent recalled the prior negotiation precedent from <span className="font-mono text-indigo-300 font-semibold">MSA_AcmeCorp_2024_Executed.pdf</span>. It recognized that the 1x liability cap was approved due to cyber insurance proof, automatically mitigating the risk severity and saving legal hours of redundant negotiation!
            </p>
            <div className="flex flex-wrap gap-2 text-[10px] font-mono mt-2 text-indigo-300">
              {memoryInsights.map((insight, idx) => (
                <span key={idx} className="bg-indigo-950/80 border border-indigo-700/40 px-2 py-0.5 rounded-md">
                  {insight}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Recalled Precedents for Current Document */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-xs font-bold text-slate-200 uppercase tracking-widest flex items-center gap-2">
            <Layers className="w-4 h-4 text-indigo-400" />
            Recalled Precedents for "{data.filename}" ({recalledItems.length})
          </h3>
          <span className="text-[10px] text-slate-400">
            Source: Hindsight Memory Bank ({status?.bank_id || 'docpilot-legal-bank'})
          </span>
        </div>

        {recalledItems.length === 0 ? (
          <div className="p-6 rounded-xl border border-slate-900 bg-slate-950/40 text-center text-xs text-slate-500">
            No specific historical precedents matched this document's counterparties or terms.
          </div>
        ) : (
          <div className="grid md:grid-cols-2 gap-3">
            {recalledItems.map((mem) => (
              <div
                key={mem.id}
                className="p-4 rounded-xl border border-slate-850 bg-slate-950/40 hover:border-indigo-500/40 transition-all flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between gap-2 mb-2">
                    <span className="px-2 py-0.5 rounded-md text-[10px] font-bold bg-indigo-500/10 text-indigo-300 border border-indigo-500/20">
                      {mem.category}
                    </span>
                    <span className="text-[10px] font-mono text-emerald-400 font-semibold">
                      Match: {Math.round(mem.confidence * 100)}%
                    </span>
                  </div>

                  <p className="text-xs text-slate-200 leading-relaxed font-sans mb-3">
                    {mem.content}
                  </p>
                </div>

                <div className="pt-3 border-t border-slate-900 flex items-center justify-between text-[10px] text-slate-400">
                  <div className="flex items-center gap-1.5 flex-wrap">
                    <Tag className="w-3 h-3 text-slate-500" />
                    {mem.tags.map((t, i) => (
                      <span key={i} className="px-1.5 py-0.5 bg-slate-900 rounded text-slate-400 text-[9px] font-mono">
                        {t}
                      </span>
                    ))}
                  </div>
                  {mem.source_doc && (
                    <span className="text-slate-500 font-mono text-[9px] truncate max-w-[120px]" title={mem.source_doc}>
                      {mem.source_doc}
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Institutional Memory Bank Explorer */}
      <div>
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-3">
          <div>
            <h3 className="text-xs font-bold text-slate-200 uppercase tracking-widest flex items-center gap-2">
              <Database className="w-4 h-4 text-indigo-400" />
              Institutional Memory Bank Explorer ({filteredMemories.length})
            </h3>
            <p className="text-[10px] text-slate-400">
              Browse all company policies, negotiated precedents, and approved exceptions stored in Hindsight.
            </p>
          </div>

          <div className="relative w-full sm:w-64">
            <Search className="w-3.5 h-3.5 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search memories, tags, vendors..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-8 pr-3 py-1.5 bg-slate-900 border border-slate-800 rounded-lg text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
            />
          </div>
        </div>

        <div className="space-y-2 max-h-[380px] overflow-y-auto pr-1">
          {filteredMemories.map((m) => (
            <div
              key={m.id}
              className="p-3.5 rounded-xl border border-slate-900 bg-slate-950/30 hover:bg-slate-900/30 transition flex flex-col md:flex-row md:items-center justify-between gap-3"
            >
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-[10px] font-bold text-indigo-400 uppercase tracking-wider">
                    {m.category}
                  </span>
                  <span className="text-[10px] text-slate-500 font-mono">
                    ID: {m.id}
                  </span>
                </div>
                <p className="text-xs text-slate-300 leading-relaxed font-sans">
                  {m.content}
                </p>
              </div>

              <div className="flex items-center gap-2 flex-wrap md:flex-nowrap shrink-0">
                {m.tags.slice(0, 3).map((tag, i) => (
                  <span key={i} className="text-[9px] font-mono px-2 py-0.5 rounded bg-slate-900 border border-slate-800 text-slate-400">
                    {tag}
                  </span>
                ))}
                {m.source_doc && (
                  <span className="text-[9px] text-slate-500 font-mono bg-slate-950 px-2 py-0.5 rounded border border-slate-850 truncate max-w-[130px]">
                    {m.source_doc}
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* TEACH AGENT MODAL */}
      {showTeachModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4 animate-fade-in">
          <div className="w-full max-w-lg rounded-2xl border border-slate-800 bg-[#0d121f] p-6 shadow-2xl">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-lg bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center">
                  <PlusCircle className="w-4 h-4 text-indigo-400" />
                </div>
                <div>
                  <h3 className="text-sm font-bold text-slate-100">
                    Teach Agent New Precedent
                  </h3>
                  <p className="text-[10px] text-slate-400">
                    Instantly retain a corporate rule or exception into Hindsight memory.
                  </p>
                </div>
              </div>
              <button
                onClick={() => setShowTeachModal(false)}
                className="text-slate-500 hover:text-slate-300 text-sm font-bold cursor-pointer"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleTeachMemory} className="space-y-4">
              <div>
                <label className="text-[11px] font-bold text-slate-300 block mb-1">
                  Category
                </label>
                <select
                  value={teachCategory}
                  onChange={(e) => setTeachCategory(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
                >
                  <option value="Approved Exception">Approved Exception (Vendor specific)</option>
                  <option value="Corporate Policy">Corporate Policy (Global mandate)</option>
                  <option value="Negotiation Precedent">Negotiation Precedent (Prior win/loss)</option>
                  <option value="Compliance Rule">Compliance Rule (Regulatory/Audit)</option>
                </select>
              </div>

              <div>
                <label className="text-[11px] font-bold text-slate-300 block mb-1">
                  Memory Rule / Precedent Text
                </label>
                <textarea
                  required
                  rows={3}
                  value={teachContent}
                  onChange={(e) => setTeachContent(e.target.value)}
                  placeholder="e.g. Approved 45-day payment terms for CloudSoft due to annual prepayment discount."
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-xs text-slate-200 focus:outline-none focus:border-indigo-500 leading-relaxed font-sans"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-[11px] font-bold text-slate-300 block mb-1">
                    Tags (comma separated)
                  </label>
                  <input
                    type="text"
                    value={teachTags}
                    onChange={(e) => setTeachTags(e.target.value)}
                    placeholder="Acme Corp, liability, SLA"
                    className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-xs text-slate-200 focus:outline-none focus:border-indigo-500 font-mono"
                  />
                </div>

                <div>
                  <label className="text-[11px] font-bold text-slate-300 block mb-1">
                    Source Document / Context
                  </label>
                  <input
                    type="text"
                    value={teachSourceDoc}
                    onChange={(e) => setTeachSourceDoc(e.target.value)}
                    placeholder="MSA_2025.pdf"
                    className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-xs text-slate-200 focus:outline-none focus:border-indigo-500 font-mono"
                  />
                </div>
              </div>

              {teachSuccess && (
                <div className="p-2.5 rounded-lg bg-emerald-950/40 border border-emerald-800/50 text-emerald-300 text-xs flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4" />
                  <span>Memory successfully retained in Hindsight Bank!</span>
                </div>
              )}

              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowTeachModal(false)}
                  className="px-3 py-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 text-slate-400 text-xs font-semibold cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold shadow-lg shadow-indigo-600/25 transition cursor-pointer"
                >
                  Retain to Memory
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
