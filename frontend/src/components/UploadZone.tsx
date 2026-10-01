'use client';

import React, { useState, useRef } from 'react';
import { Upload, FileText, AlertCircle, Cpu, Zap, BarChart3, FileSearch } from 'lucide-react';
import { getBackendUrl } from '../lib/api';

interface UploadZoneProps {
  apiKey: string;
  setApiKey?: (key: string) => void;
  onUploadSuccess: (docId: string, filename: string, pagesCount: number) => void;
}

export default function UploadZone({ apiKey, onUploadSuccess }: UploadZoneProps) {
  const [dragActive, setDragActive] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const fileInputRef = useRef<HTMLInputElement>(null);

  const BACKEND_URL = getBackendUrl();

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = async (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      await uploadFile(e.dataTransfer.files[0]);
    }
  };

  const handleChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      await uploadFile(e.target.files[0]);
    }
  };

  const onButtonClick = () => {
    fileInputRef.current?.click();
  };

  const uploadFile = async (file: File) => {
    const ext = file.name.substring(file.name.lastIndexOf('.')).toLowerCase();
    const validExtensions = ['.pdf', '.png', '.jpg', '.jpeg'];
    
    if (!validExtensions.includes(ext)) {
      setErrorMsg('Unsupported file format. Please upload PDF, PNG, or JPEG.');
      return;
    }

    if (file.size > 15 * 1024 * 1024) {
      setErrorMsg('File size exceeds the 15MB limit.');
      return;
    }

    setUploading(true);
    setErrorMsg('');

    const formData = new FormData();
    formData.append('file', file);

    try {
      const headers: Record<string, string> = {};
      if (apiKey) {
        headers['X-Gemini-Key'] = apiKey;
      }

      const res = await fetch(`${BACKEND_URL}/api/upload`, {
        method: 'POST',
        headers,
        body: formData,
      });

      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || 'Failed to upload document.');
      }

      const data = await res.json();
      onUploadSuccess(data.document_id, data.filename, data.pages_count);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'An error occurred during file upload.';
      setErrorMsg(message);
      setUploading(false);
    }
  };

  return (
    <div className="relative w-full max-w-6xl mx-auto px-4 py-8 flex flex-col items-center">
      {/* Background Decorative Blurs */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-indigo-500/10 rounded-full blur-[120px] pointer-events-none select-none -z-10" />
      <div className="absolute top-1/3 left-1/4 w-[300px] h-[300px] bg-purple-500/5 rounded-full blur-[100px] pointer-events-none select-none -z-10" />

      {/* Product Hero */}
      <div className="text-center mb-12 select-none">
        <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-gradient-to-r from-indigo-500/10 to-purple-500/10 border border-indigo-500/25 text-indigo-300 text-xs font-bold uppercase tracking-wider mb-6 shadow-lg shadow-indigo-500/5 animate-pulse">
          <Zap className="w-3.5 h-3.5 text-indigo-400 fill-indigo-400" /> Autonomous Document Review Agent
        </div>
        
        <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight mb-5 leading-tight">
          DocPilot <span className="bg-gradient-to-r from-indigo-400 via-purple-400 to-indigo-400 bg-clip-text text-transparent font-black">AI</span>
        </h1>
        
        <p className="text-sm sm:text-base text-slate-400 max-w-2xl mx-auto leading-relaxed font-medium">
          Transform complex contracts, NDAs, and agreements into structured insight dashboards. Audits legal liabilities, identifies compliance gaps, and proposes balanced negotiations.
        </p>
      </div>

      {/* Centered Large Upload Zone */}
      <div className="w-full max-w-3xl">
        <div
          onDragEnter={handleDrag}
          onDragOver={handleDrag}
          onDragLeave={handleDrag}
          onDrop={handleDrop}
          className={`glass-panel p-12 rounded-3xl border-2 border-dashed flex flex-col items-center justify-center min-h-[340px] text-center cursor-pointer transition-all duration-300 relative overflow-hidden ${
            dragActive
              ? 'border-indigo-500 bg-indigo-500/5 shadow-2xl shadow-indigo-500/10 scale-[0.99]'
              : 'border-slate-800 hover:border-slate-700/80 bg-slate-950/40 hover:shadow-2xl hover:shadow-indigo-500/5'
          }`}
          onClick={onButtonClick}
        >
          {/* Subtle grid patterns inside card */}
          <div className="absolute inset-0 bg-[linear-gradient(to_right,#0f172a_1px,transparent_1px),linear-gradient(to_bottom,#0f172a_1px,transparent_1px)] bg-[size:24px_24px] opacity-25 -z-10" />

          <input
            ref={fileInputRef}
            type="file"
            className="hidden"
            multiple={false}
            onChange={handleChange}
            accept=".pdf,.png,.jpg,.jpeg"
            disabled={uploading}
          />

          {uploading ? (
            <div className="flex flex-col items-center space-y-5 animate-fade-in">
              <div className="relative">
                <div className="w-16 h-16 border-4 border-indigo-500/25 border-t-indigo-400 rounded-full animate-spin"></div>
                <Cpu className="w-6 h-6 text-indigo-400 absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2" />
              </div>
              <div className="text-slate-200 font-bold tracking-wide">Uploading and preparing document...</div>
              <div className="text-xs text-slate-500 font-medium">Extracting structure, page details & text layouts</div>
            </div>
          ) : (
            <div className="flex flex-col items-center animate-fade-in">
              <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-indigo-500/10 to-purple-500/10 flex items-center justify-center mb-6 border border-indigo-500/20 shadow-lg shadow-indigo-500/5">
                <Upload className="w-9 h-9 text-indigo-400" />
              </div>
              <h3 className="text-xl font-black text-slate-200 mb-2">
                Drag and drop your file here
              </h3>
              <p className="text-sm text-slate-400 mb-6 font-medium">
                or click to browse from your computer
              </p>
              
              <div className="inline-flex gap-4 items-center text-[10px] font-bold text-slate-500 bg-slate-950 px-4 py-2 rounded-full border border-slate-800 shadow-inner">
                <span className="flex items-center gap-1.5">
                  <FileText className="w-3.5 h-3.5 text-red-500" /> PDF
                </span>
                <span className="w-1 h-1 bg-slate-800 rounded-full"></span>
                <span className="flex items-center gap-1.5">
                  <FileText className="w-3.5 h-3.5 text-blue-400" /> Images (PNG/JPG)
                </span>
                <span className="w-1 h-1 bg-slate-800 rounded-full"></span>
                <span>Max 15MB</span>
              </div>
            </div>
          )}
        </div>

        {errorMsg && (
          <div className="mt-6 p-4 bg-red-500/10 border border-red-500/20 rounded-2xl flex items-start gap-3 text-sm text-red-400 shadow-lg shadow-red-500/5">
            <AlertCircle className="w-5 h-5 shrink-0 mt-0.5" />
            <span>{errorMsg}</span>
          </div>
        )}
      </div>

      {/* Feature Showcase Grid */}
      <div className="w-full mt-24 border-t border-slate-900 pt-16">
        <h2 className="text-center font-extrabold uppercase tracking-widest text-[10px] text-slate-500 mb-10 select-none">
          Autonomous multi-agent workspace features
        </h2>
        
        <div className="grid sm:grid-cols-3 gap-6">
          <div className="glass-panel p-6 rounded-2xl hover:border-slate-800/80 group">
            <div className="w-10 h-10 rounded-xl bg-indigo-500/10 flex items-center justify-center mb-4 border border-indigo-500/10 group-hover:border-indigo-500/20">
              <Cpu className="w-5 h-5 text-indigo-400" />
            </div>
            <h3 className="font-bold text-slate-200 mb-2 text-sm">Orchestrated Analysis</h3>
            <p className="text-xs text-slate-400 leading-relaxed font-medium">
              Coordinates 9 specialized AI agents sequentially, piping context findings to minimize model execution speeds.
            </p>
          </div>
          
          <div className="glass-panel p-6 rounded-2xl hover:border-slate-800/80 group">
            <div className="w-10 h-10 rounded-xl bg-purple-500/10 flex items-center justify-center mb-4 border border-purple-500/10 group-hover:border-purple-500/20">
              <FileSearch className="w-5 h-5 text-purple-400" />
            </div>
            <h3 className="font-bold text-slate-200 mb-2 text-sm">Visual Bounding Boxes</h3>
            <p className="text-xs text-slate-400 leading-relaxed font-medium">
              Maps clauses and identified risks to coordinates in the PDF layout, highlighting exposures in real time.
            </p>
          </div>
          
          <div className="glass-panel p-6 rounded-2xl hover:border-slate-800/80 group">
            <div className="w-10 h-10 rounded-xl bg-emerald-500/10 flex items-center justify-center mb-4 border border-emerald-500/10 group-hover:border-emerald-500/20">
              <BarChart3 className="w-5 h-5 text-emerald-400" />
            </div>
            <h3 className="font-bold text-slate-200 mb-2 text-sm">Executive Dashboard</h3>
            <p className="text-xs text-slate-400 leading-relaxed font-medium">
              Translates complex legal terms into plain English summaries, timeline dates, and proposed contract redlines.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
