'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Loader2, Sparkles, MapPin } from 'lucide-react';
import { ChatMessage, Coordinate } from '../types';

interface AiChatProps {
  documentId: string;
  apiKey: string;
  onLocate: (coordinates: Coordinate[], id: string) => void;
}

const QUICK_PROMPTS = [
  'Is confidentiality included?',
  'Can either party terminate early?',
  'What penalties exist?',
  'What governing law applies?',
  'Summarize in simple English.'
];

export default function AiChat({ documentId, apiKey, onLocate }: AiChatProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([
    { role: 'assistant', content: 'Hello! I am DocPilot chat agent. I have analyzed the document. Ask me any specific questions about clauses, payment schedules, liabilities, or termination clauses.' }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  
  // Track detailed responses containing coordinates
  const [responseDetails, setResponseDetails] = useState<Record<number, { evidence?: string[]; coordinates?: Coordinate[] }>>({});

  const chatEndRef = useRef<HTMLDivElement>(null);
  const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const handleSend = async (textToSend: string) => {
    if (!textToSend.trim() || loading) return;

    const userMsg: ChatMessage = { role: 'user', content: textToSend };
    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const res = await fetch(`${BACKEND_URL}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(apiKey ? { 'X-Gemini-Key': apiKey } : {})
        },
        body: JSON.stringify({
          document_id: documentId,
          history: messages.slice(1), // Exclude initial greeting
          message: textToSend
        })
      });

      if (!res.ok) {
        throw new Error('Failed to fetch response from chat agent.');
      }

      const data = await res.json();
      
      const assistantMsgIndex = messages.length + 1;
      setMessages((prev) => [...prev, { role: 'assistant', content: data.answer }]);
      
      if (data.evidence || data.coordinates) {
        setResponseDetails((prev) => ({
          ...prev,
          [assistantMsgIndex]: {
            evidence: data.evidence,
            coordinates: data.coordinates
          }
        }));
      }
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: 'Sorry, I encountered an error answering your question. Please verify your connection or API configuration.' }
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[500px] bg-slate-900/30 border border-slate-800 rounded-xl overflow-hidden">
      {/* Title */}
      <div className="bg-slate-950/40 border-b border-slate-850 px-4 py-2.5 flex items-center justify-between text-xs select-none">
        <div className="flex items-center gap-1.5 font-bold text-slate-300">
          <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
          <span>DocPilot Conversational Chat</span>
        </div>
        <span className="text-[10px] text-slate-500 font-mono">Gemini 2.5 Flash</span>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg, idx) => {
          const isAssistant = msg.role === 'assistant';
          const details = responseDetails[idx];
          const hasCoords = details?.coordinates && details.coordinates.length > 0;

          return (
            <div key={idx} className={`flex gap-3 ${isAssistant ? 'justify-start' : 'justify-end'}`}>
              {isAssistant && (
                <div className="w-6 h-6 rounded-full bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center shrink-0 mt-0.5">
                  <Bot className="w-3.5 h-3.5 text-indigo-400" />
                </div>
              )}
              
              <div className="flex flex-col max-w-[80%] gap-1.5">
                <div
                  className={`px-3 py-2.5 rounded-2xl text-xs leading-relaxed font-sans ${
                    isAssistant
                      ? 'bg-slate-950/40 border border-slate-850 text-slate-200 rounded-tl-sm'
                      : 'bg-indigo-600 text-white rounded-tr-sm'
                  }`}
                >
                  {msg.content}
                </div>

                {/* Evidence and Coordinate Mapping Buttons */}
                {isAssistant && details && (
                  <div className="space-y-1.5 pl-1">
                    {details.evidence && details.evidence.length > 0 && (
                      <div className="text-[9px] text-slate-500 leading-normal max-w-full">
                        <span className="font-semibold uppercase tracking-wider text-slate-600 block mb-0.5">Source Evidence:</span>
                        <p className="italic truncate" title={details.evidence[0]}>
                          &quot;{details.evidence[0]}&quot;
                        </p>
                      </div>
                    )}
                    {hasCoords && (
                      <button
                        onClick={() => onLocate(details.coordinates!, `chat-bubble-${idx}`)}
                        className="inline-flex items-center gap-1 px-2 py-0.5 bg-indigo-500/10 hover:bg-indigo-500/20 border border-indigo-500/20 text-indigo-400 text-[9px] font-bold rounded cursor-pointer transition-all mt-0.5"
                      >
                        <MapPin className="w-2.5 h-2.5" /> View Evidence in Document (Page {details.coordinates![0].page + 1})
                      </button>
                    )}
                  </div>
                )}
              </div>

              {!isAssistant && (
                <div className="w-6 h-6 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center shrink-0 mt-0.5">
                  <User className="w-3.5 h-3.5 text-slate-300" />
                </div>
              )}
            </div>
          );
        })}

        {loading && (
          <div className="flex gap-3 justify-start">
            <div className="w-6 h-6 rounded-full bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center shrink-0">
              <Loader2 className="w-3.5 h-3.5 text-indigo-400 animate-spin" />
            </div>
            <div className="px-3 py-2 bg-slate-950/40 border border-slate-850 rounded-2xl rounded-tl-sm flex items-center gap-1.5 text-xs text-slate-400 italic">
              DocPilot thinking...
            </div>
          </div>
        )}
        <div ref={chatEndRef} />
      </div>

      {/* Quick Prompt Chips */}
      <div className="px-4 py-2 border-t border-slate-900 flex gap-1.5 overflow-x-auto whitespace-nowrap scrollbar-none select-none bg-slate-950/20">
        {QUICK_PROMPTS.map((prompt) => (
          <button
            key={prompt}
            onClick={() => handleSend(prompt)}
            disabled={loading}
            className="px-2 py-1 bg-slate-900 border border-slate-850 hover:bg-slate-800 text-slate-400 hover:text-slate-200 text-[10px] font-semibold rounded-full cursor-pointer disabled:opacity-40 transition-colors shrink-0"
          >
            {prompt}
          </button>
        ))}
      </div>

      {/* Input */}
      <div className="p-3 bg-slate-950/40 border-t border-slate-850 flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSend(input)}
          placeholder="Ask a question about this document..."
          disabled={loading}
          className="flex-1 px-3 py-2 text-xs bg-slate-950 border border-slate-850 rounded-lg focus:outline-none focus:border-indigo-500 text-slate-200"
        />
        <button
          onClick={() => handleSend(input)}
          disabled={!input.trim() || loading}
          className="p-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg disabled:opacity-40 transition-colors cursor-pointer shrink-0"
        >
          <Send className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}
