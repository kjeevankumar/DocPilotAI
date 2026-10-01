'use client';

import React, { useState } from 'react';
import { ChevronLeft, ChevronRight, ZoomIn, ZoomOut, RotateCcw } from 'lucide-react';
import { Coordinate } from '../types';
import { getBackendUrl } from '../lib/api';

interface HighlightItem {
  id: string;
  name: string;
  severity: 'Critical' | 'High' | 'Medium' | 'Low' | 'Safe';
  coordinates: Coordinate[];
}

interface PdfViewerProps {
  docId: string;
  pagesCount: number;
  highlights: HighlightItem[];
  activeHighlightId: string | null;
  onHighlightClick: (id: string, name: string) => void;
  currentPage: number;
  setCurrentPage: (page: number) => void;
}

export default function PdfViewer({
  docId,
  pagesCount,
  highlights,
  activeHighlightId,
  onHighlightClick,
  currentPage,
  setCurrentPage
}: PdfViewerProps) {
  const [zoom, setZoom] = useState(100); // Zoom in percentage (e.g., 100, 120, 150)
  const BACKEND_URL = getBackendUrl();

  const handlePrevPage = () => {
    if (currentPage > 0) {
      setCurrentPage(currentPage - 1);
    }
  };

  const handleNextPage = () => {
    if (currentPage < pagesCount - 1) {
      setCurrentPage(currentPage + 1);
    }
  };

  const handleZoomIn = () => {
    setZoom((prev) => Math.min(prev + 15, 200));
  };

  const handleZoomOut = () => {
    setZoom((prev) => Math.max(prev - 15, 50));
  };

  const handleResetZoom = () => {
    setZoom(100);
  };

  // Color mapping based on risk level
  const getHighlightStyle = (severity: string, isActive: boolean) => {
    let colorClass = 'border-blue-500 bg-blue-500/10 text-blue-500';
    
    if (severity === 'Critical') {
      colorClass = 'border-red-500 bg-red-500/25 text-red-500';
    } else if (severity === 'High') {
      colorClass = 'border-orange-500 bg-orange-500/25 text-orange-400';
    } else if (severity === 'Medium') {
      colorClass = 'border-amber-500 bg-amber-500/25 text-amber-500';
    } else if (severity === 'Low') {
      colorClass = 'border-emerald-500 bg-emerald-500/20 text-emerald-400';
    } else if (severity === 'Safe') {
      colorClass = 'border-teal-500 bg-teal-500/15 text-teal-400';
    }

    if (isActive) {
      return `${colorClass} ring-2 ring-indigo-500 ring-offset-2 ring-offset-slate-950 scale-[1.01] shadow-lg z-10`;
    }
    return colorClass;
  };

  // Filter highlights to only show on the active page
  const pageHighlights = highlights.flatMap((h) => 
    (h.coordinates || [])
      .filter((coord) => coord.page === currentPage)
      .map((coord) => ({
        ...coord,
        id: h.id,
        name: h.name,
        severity: h.severity,
        isActive: h.id === activeHighlightId
      }))
  );

  return (
    <div className="flex flex-col h-full bg-slate-900/40 border border-slate-800 rounded-2xl overflow-hidden">
      {/* Top Toolbar */}
      <div className="bg-slate-950/60 border-b border-slate-800 px-4 py-2.5 flex items-center justify-between text-sm select-none">
        {/* Page Nav */}
        <div className="flex items-center gap-1.5">
          <button
            onClick={handlePrevPage}
            disabled={currentPage === 0}
            className="p-1 rounded bg-slate-900 hover:bg-slate-800 disabled:opacity-40 text-slate-300 border border-slate-800 cursor-pointer"
          >
            <ChevronLeft className="w-4 h-4" />
          </button>
          <span className="text-xs font-mono text-slate-400 px-1">
            Page {currentPage + 1} of {pagesCount}
          </span>
          <button
            onClick={handleNextPage}
            disabled={currentPage === pagesCount - 1}
            className="p-1 rounded bg-slate-900 hover:bg-slate-800 disabled:opacity-40 text-slate-300 border border-slate-800 cursor-pointer"
          >
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>

        {/* Zoom controls */}
        <div className="flex items-center gap-1">
          <button
            onClick={handleZoomOut}
            disabled={zoom <= 50}
            className="p-1 rounded bg-slate-900 hover:bg-slate-800 disabled:opacity-40 text-slate-300 border border-slate-800 cursor-pointer"
          >
            <ZoomOut className="w-4 h-4" />
          </button>
          <span className="text-xs font-mono text-slate-400 w-12 text-center">{zoom}%</span>
          <button
            onClick={handleZoomIn}
            disabled={zoom >= 200}
            className="p-1 rounded bg-slate-900 hover:bg-slate-800 disabled:opacity-40 text-slate-300 border border-slate-800 cursor-pointer"
          >
            <ZoomIn className="w-4 h-4" />
          </button>
          <button
            onClick={handleResetZoom}
            className="p-1 rounded bg-slate-900 hover:bg-slate-800 text-slate-400 border border-slate-800 cursor-pointer ml-1"
            title="Reset Zoom"
          >
            <RotateCcw className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Main Canvas Scroll Area */}
      <div className="flex-1 overflow-auto p-6 bg-slate-950/20 flex justify-center items-start">
        {/* Dynamic Zoom Wrapper */}
        <div
          className="relative transition-all duration-200 shadow-2xl rounded-lg border border-slate-800 bg-slate-950 overflow-hidden"
          style={{ width: `${zoom}%`, maxWidth: '100%', minWidth: '320px' }}
        >
          {/* Document Render Page */}
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src={`${BACKEND_URL}/api/document/${docId}/page/${currentPage}`}
            alt={`Page ${currentPage + 1}`}
            className="w-full h-auto select-none pointer-events-none"
          />

          {/* Absolute Highlights Canvas Layer */}
          {pageHighlights.map((highlight, idx) => {
            const { box, page_width, page_height } = highlight;
            
            // Percentage conversion to align absolute elements regardless of window scale
            const left = `${(box[0] / page_width) * 100}%`;
            const top = `${(box[1] / page_height) * 100}%`;
            const width = `${((box[2] - box[0]) / page_width) * 100}%`;
            const height = `${((box[3] - box[1]) / page_height) * 100}%`;

            return (
              <div
                key={`${highlight.id}-${idx}`}
                className={`absolute highlight-overlay border rounded-sm transition-all duration-150 ${getHighlightStyle(
                  highlight.severity,
                  highlight.isActive
                )}`}
                style={{ left, top, width, height }}
                onClick={() => onHighlightClick(highlight.id, highlight.name)}
                title={`Click to view: ${highlight.name} (${highlight.severity} Risk)`}
              />
            );
          })}
        </div>
      </div>
    </div>
  );
}
