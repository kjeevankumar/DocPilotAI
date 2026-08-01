'use client';

import React, { useState } from 'react';
import { Shield, Cpu, Key, Eye, EyeOff } from 'lucide-react';
import UploadZone from '../components/UploadZone';
import ProcessingScreen from '../components/ProcessingScreen';
import DashboardWorkspace from '../components/DashboardWorkspace';
import { DocumentAnalysisResponse } from '../types';

export default function Home() {
  const [appState, setAppState] = useState<'landing' | 'processing' | 'dashboard'>('landing');
  const [apiKey, setApiKey] = useState(() => {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('gemini_api_key') || '';
    }
    return '';
  });
  const [showSettings, setShowSettings] = useState(false);
  const [showKey, setShowKey] = useState(false);
  
  // File details
  const [docId, setDocId] = useState('');
  const [filename, setFilename] = useState('');
  
  // Analysis details
  const [analysisData, setAnalysisData] = useState<DocumentAnalysisResponse | null>(null);

  // Persist API Key changes
  const handleSetApiKey = (key: string) => {
    setApiKey(key);
    if (typeof window !== 'undefined') {
      localStorage.setItem('gemini_api_key', key);
    }
  };

  const handleUploadSuccess = (id: string, name: string) => {
    setDocId(id);
    setFilename(name);
    setAppState('processing');
  };

  const handleAnalysisComplete = (data: DocumentAnalysisResponse) => {
    setAnalysisData(data);
    setAppState('dashboard');
  };

  const handleCancelAnalysis = () => {
    setAppState('landing');
  };

  const handleReset = () => {
    setAnalysisData(null);
    setDocId('');
    setFilename('');
    setAppState('landing');
  };

  return (
    <div className="min-h-screen flex flex-col bg-[#090d16] text-slate-100 selection:bg-indigo-500/20 selection:text-indigo-200">
      {/* Brand Header */}
      <header className="border-b border-slate-900 bg-slate-950/30 px-6 py-4 flex items-center justify-between select-none">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-indigo-600/10 border border-indigo-500/25 flex items-center justify-center">
            <Cpu className="w-4 h-4 text-indigo-400" />
          </div>
          <span className="font-extrabold text-sm tracking-tight text-slate-200">
            DocPilot <span className="text-indigo-400">AI</span>
          </span>
        </div>

        <div className="flex items-center gap-4">
          <div className="flex items-center gap-1.5 text-xs text-slate-500 font-mono">
            <Shield className="w-3.5 h-3.5 text-indigo-400/80" />
            <span>Autonomous Sandbox</span>
          </div>
          
          <div className="relative">
            <button
              onClick={() => setShowSettings(!showSettings)}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-800 hover:border-slate-700 text-slate-300 text-xs font-semibold cursor-pointer transition-colors"
            >
              <Key className="w-3.5 h-3.5 text-indigo-400" />
              <span>{apiKey ? 'API Key Configured' : 'Configure API Key'}</span>
            </button>
            
            {showSettings && (
              <div className="absolute right-0 mt-2 w-80 glass-panel p-4 rounded-xl border border-slate-800 bg-[#0b0f19] shadow-2xl z-50 animate-fade-in">
                <h3 className="text-xs font-bold text-slate-200 mb-2 flex items-center gap-1.5">
                  <Key className="w-3.5 h-3.5 text-indigo-400" /> Gemini API Settings
                </h3>
                <p className="text-[10px] text-slate-400 mb-3 leading-relaxed">
                  Enter your Gemini API key below. It is stored locally in your browser and sent only to your autonomous workspace.
                </p>
                <div className="flex gap-2 relative">
                  <input
                    type={showKey ? 'text' : 'password'}
                    value={apiKey}
                    onChange={(e) => handleSetApiKey(e.target.value)}
                    placeholder="AIzaSy..."
                    className="flex-1 px-3 py-1.5 text-xs bg-slate-950 border border-slate-850 rounded-lg focus:outline-none focus:border-indigo-500 text-slate-200 pr-8 font-mono"
                  />
                  <button
                    onClick={() => setShowKey(!showKey)}
                    className="absolute right-2 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300 cursor-pointer"
                  >
                    {showKey ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
                  </button>
                </div>
                <div className="mt-3 flex justify-between items-center">
                  <span className="text-[9px] text-slate-500">
                    {apiKey ? '✓ Key stored locally' : '⚠️ Using backend .env key'}
                  </span>
                  <button
                    onClick={() => setShowSettings(false)}
                    className="px-2.5 py-1 bg-indigo-600 hover:bg-indigo-500 text-white text-[10px] font-bold rounded-md transition-colors cursor-pointer"
                  >
                    Save
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </header>

      {/* Main Container */}
      <main className="flex-1 flex flex-col justify-center py-8">
        {appState === 'landing' && (
          <UploadZone
            apiKey={apiKey}
            setApiKey={handleSetApiKey}
            onUploadSuccess={handleUploadSuccess}
          />
        )}

        {appState === 'processing' && (
          <ProcessingScreen
            docId={docId}
            filename={filename}
            apiKey={apiKey}
            onComplete={handleAnalysisComplete}
            onCancel={handleCancelAnalysis}
          />
        )}

        {appState === 'dashboard' && analysisData && (
          <DashboardWorkspace
            data={analysisData}
            onReset={handleReset}
            apiKey={apiKey}
          />
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-950 bg-slate-950/20 py-4 text-center text-[10px] text-slate-600 select-none">
        DocPilot AI Agent Platform &bull; Hackathon Edition v1.0 &bull; Powered by Google Gemini 2.5 Flash
      </footer>
    </div>
  );
}
