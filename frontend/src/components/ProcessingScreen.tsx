'use client';

import React, { useEffect, useState, useRef } from 'react';
import { Terminal, CheckCircle2, Circle, Loader2, AlertCircle } from 'lucide-react';
import { AgentLog, DocumentAnalysisResponse } from '../types';

interface ProcessingScreenProps {
  docId: string;
  filename: string;
  apiKey: string;
  onComplete: (data: DocumentAnalysisResponse) => void;
  onCancel: () => void;
}

const AGENTS_LIST = [
  'Document Intake Agent',
  'Document Classification Agent',
  'Entity Extraction Agent',
  'Clause Intelligence Agent',
  'Risk Intelligence Agent',
  'Business Impact Agent',
  'Compliance Agent',
  'Negotiation Agent',
  'Executive Summary Agent',
  'Decision Recommendation Agent',
  'Highlight Coordinate Mapping'
];

export default function ProcessingScreen({ docId, filename, apiKey, onComplete, onCancel }: ProcessingScreenProps) {
  const [logs, setLogs] = useState<AgentLog[]>(
    AGENTS_LIST.map((name) => ({ agent: name, status: 'pending' }))
  );
  const [consoleOutputs, setConsoleOutputs] = useState<string[]>(['[SYSTEM] Initializing Agent Orchestrator...']);
  const [errorMessage, setErrorMessage] = useState('');
  const terminalEndRef = useRef<HTMLDivElement>(null);
  
  const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

  useEffect(() => {
    // Scroll terminal to bottom when logs are added
    terminalEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [consoleOutputs]);

  useEffect(() => {
    let isPipelineFinished = false;
    const url = `${BACKEND_URL}/api/analyze?doc_id=${docId}&filename=${encodeURIComponent(filename)}&api_key=${apiKey}`;
    const eventSource = new EventSource(url);

    eventSource.onopen = () => {
      setConsoleOutputs((prev) => [...prev, `[SYSTEM] SSE connection established for document ID: ${docId}`, `[SYSTEM] Executing autonomous review pipeline...`]);
    };

    eventSource.addEventListener('agent_start', (event: MessageEvent) => {
      const data = JSON.parse(event.data);
      const agentName = data.agent;
      
      setLogs((prev) =>
        prev.map((log) => (log.agent === agentName ? { ...log, status: 'processing' } : log))
      );
      setConsoleOutputs((prev) => [
        ...prev,
        `[SPAWN] Active: ${agentName}...`,
        `[${agentName}] Analyzing contextual tokens...`
      ]);
    });

    eventSource.addEventListener('agent_complete', (event: MessageEvent) => {
      const data = JSON.parse(event.data);
      const agentName = data.agent;
      const status = data.status || 'success';
      const elapsed = data.elapsed;
      const summary = data.summary;

      setLogs((prev) =>
        prev.map((log) =>
          log.agent === agentName
            ? { ...log, status: status, elapsed: elapsed, summary: summary }
            : log
        )
      );

      setConsoleOutputs((prev) => [
        ...prev,
        `[COMPLETE] ${agentName} finished in ${elapsed || 0}s`,
        `[${agentName}] RESULT: ${summary}`,
        `--------------------------------------------------`
      ]);
    });

    eventSource.addEventListener('pipeline_complete', (event: MessageEvent) => {
      isPipelineFinished = true;
      const data = JSON.parse(event.data) as DocumentAnalysisResponse;
      setConsoleOutputs((prev) => [...prev, `[SYSTEM] Pipeline complete! Synthesized payload in ${data.processing_time_sec}s.`, `[SYSTEM] Transitioning to Decision Dashboard.`]);
      
      // Give the user a brief moment to see all checkmarks green before transitioning
      setTimeout(() => {
        eventSource.close();
        onComplete(data);
      }, 1500);
    });

    eventSource.addEventListener('error', (event: MessageEvent) => {
      if (isPipelineFinished) return;
      
      // Standard connection errors do not contain event data
      if (!event.data) {
        return;
      }
      
      let detail = 'An unknown SSE error occurred.';
      try {
        const data = JSON.parse(event.data);
        detail = data.detail || detail;
      } catch {}
      
      setErrorMessage(detail);
      setConsoleOutputs((prev) => [...prev, `[FATAL] Error: ${detail}`]);
      eventSource.close();
    });

    eventSource.onerror = (err) => {
      if (isPipelineFinished) return;
      // Avoid printing errors as console.error to prevent triggering Next.js dev overlay
      console.warn('SSE Connection status changed. ReadyState:', eventSource.readyState, err);
      // Wait to see if we completed before displaying connection failures
      setTimeout(() => {
        if (!isPipelineFinished && eventSource.readyState === EventSource.CLOSED) {
          setErrorMessage('Disconnected from analysis server.');
          setConsoleOutputs((prev) => [...prev, `[FATAL] Server connection terminated abruptly.`]);
        }
      }, 2000);
    };

    return () => {
      eventSource.close();
    };
  }, [docId, filename, apiKey, BACKEND_URL, onComplete]);

  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="text-center mb-8">
        <h2 className="text-2xl font-bold text-slate-200 mb-1">Autonomous Agent Workspace</h2>
        <p className="text-sm text-slate-400">
          Analyzing <span className="text-indigo-400 font-medium">{filename}</span> with 10 specialized intelligence agents
        </p>
      </div>

      <div className="grid md:grid-cols-5 gap-8">
        {/* Agent Checklists */}
        <div className="md:col-span-2 space-y-3 bg-slate-900/40 border border-slate-800 p-6 rounded-2xl">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-4">
            AI Orchestration Queue
          </h3>
          <div className="space-y-3.5">
            {logs.map((log) => {
              const isPending = log.status === 'pending';
              const isProcessing = log.status === 'processing';
              const isSuccess = log.status === 'success';
              const isError = log.status === 'error';

              return (
                <div key={log.agent} className="flex items-center justify-between text-sm">
                  <div className="flex items-center gap-3">
                    {isPending && <Circle className="w-4 h-4 text-slate-600" />}
                    {isProcessing && <Loader2 className="w-4 h-4 text-indigo-400 animate-spin" />}
                    {isSuccess && <CheckCircle2 className="w-4 h-4 text-emerald-400" />}
                    {isError && <AlertCircle className="w-4 h-4 text-red-500" />}
                    <span
                      className={`${
                        isProcessing
                          ? 'text-slate-100 font-medium'
                          : isSuccess
                          ? 'text-slate-300'
                          : isError
                          ? 'text-red-400'
                          : 'text-slate-500'
                      }`}
                    >
                      {log.agent}
                    </span>
                  </div>
                  {log.elapsed !== undefined && (
                    <span className="text-xs text-slate-500 font-mono">{log.elapsed}s</span>
                  )}
                </div>
              );
            })}
          </div>
        </div>

        {/* Live Terminal Log */}
        <div className="md:col-span-3 flex flex-col h-[460px] bg-slate-950 border border-slate-900 rounded-2xl overflow-hidden shadow-2xl">
          {/* Window header */}
          <div className="bg-slate-900 px-4 py-2 border-b border-slate-800 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Terminal className="w-4 h-4 text-slate-400" />
              <span className="text-xs font-mono text-slate-300">orchestrator_stdout.log</span>
            </div>
            <div className="flex gap-1.5">
              <span className="w-2.5 h-2.5 rounded-full bg-slate-800"></span>
              <span className="w-2.5 h-2.5 rounded-full bg-slate-800"></span>
              <span className="w-2.5 h-2.5 rounded-full bg-slate-800"></span>
            </div>
          </div>

          {/* Terminal Console */}
          <div className="p-4 flex-1 font-mono text-xs text-slate-300 overflow-y-auto space-y-1.5 selection:bg-indigo-500/30">
            {consoleOutputs.map((line, idx) => {
              let textClass = 'text-slate-400';
              if (line.startsWith('[SYSTEM]')) textClass = 'text-indigo-400 font-medium';
              else if (line.startsWith('[SPAWN]')) textClass = 'text-slate-300 font-medium';
              else if (line.startsWith('[COMPLETE]')) textClass = 'text-emerald-400 font-semibold';
              else if (line.startsWith('[FATAL]')) textClass = 'text-red-400 font-bold';
              else if (line.startsWith('[') && line.includes('RESULT:')) textClass = 'text-slate-200';

              return (
                <div key={idx} className={textClass}>
                  {line}
                </div>
              );
            })}
            <div ref={terminalEndRef} />
          </div>
        </div>
      </div>

      {/* Footer controls */}
      {errorMessage && (
        <div className="mt-8 p-4 bg-red-500/10 border border-red-500/20 rounded-xl flex items-center justify-between text-sm text-red-400">
          <div className="flex items-center gap-2">
            <AlertCircle className="w-5 h-5 shrink-0" />
            <span>Analysis failed: {errorMessage}</span>
          </div>
          <button
            onClick={onCancel}
            className="px-4 py-1.5 bg-slate-900 border border-slate-800 text-slate-300 rounded-lg hover:bg-slate-800 text-xs font-semibold cursor-pointer"
          >
            Go Back
          </button>
        </div>
      )}
    </div>
  );
}
