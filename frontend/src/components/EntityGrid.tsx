'use client';

import React, { useState } from 'react';
import { Copy, Check, Shield, Calendar, DollarSign, Scale, UserCheck } from 'lucide-react';
import { EntityExtractionResult } from '../types';

interface EntityGridProps {
  entities: EntityExtractionResult;
}

export default function EntityGrid({ entities }: EntityGridProps) {
  const [copiedKey, setCopiedKey] = useState<string | null>(null);

  const copyToClipboard = (text: string, key: string) => {
    if (!text) return;
    navigator.clipboard.writeText(text);
    setCopiedKey(key);
    setTimeout(() => setCopiedKey(null), 1500);
  };

  const renderField = (icon: React.ReactNode, label: string, value: string | string[] | null, uniqueKey: string) => {
    const isValArray = Array.isArray(value);
    const displayValue = isValArray 
      ? (value as string[]).join(', ') 
      : (value as string) || 'Not Mentioned';
    
    const isEmpty = !value || (isValArray && (value as string[]).length === 0);

    return (
      <div className="bg-slate-950/30 border border-slate-850 p-4 rounded-xl flex flex-col justify-between group relative overflow-hidden transition-all hover:border-slate-800">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-2 text-[10px] font-bold text-slate-500 uppercase tracking-wider">
            {icon}
            <span>{label}</span>
          </div>
          {!isEmpty && (
            <button
              onClick={() => copyToClipboard(displayValue, uniqueKey)}
              className="opacity-0 group-hover:opacity-100 p-1 bg-slate-900 border border-slate-800 rounded hover:bg-slate-800 text-slate-400 hover:text-slate-200 transition-all cursor-pointer"
              title="Copy value"
            >
              {copiedKey === uniqueKey ? (
                <Check className="w-3 h-3 text-emerald-400" />
              ) : (
                <Copy className="w-3 h-3" />
              )}
            </button>
          )}
        </div>
        
        <div className={`mt-3 font-semibold text-xs leading-relaxed ${isEmpty ? 'text-slate-600 font-normal italic' : 'text-slate-200'}`}>
          {isValArray && !isEmpty ? (
            <div className="flex flex-wrap gap-1.5 mt-1">
              {(value as string[]).map((val, i) => (
                <span key={i} className="px-2 py-0.5 bg-slate-900 border border-slate-800 rounded-md text-[10px]">
                  {val}
                </span>
              ))}
            </div>
          ) : (
            displayValue
          )}
        </div>
      </div>
    );
  };

  return (
    <div className="space-y-6">
      {/* Category: Parties & Jurisdictions */}
      <div>
        <h4 className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-3 flex items-center gap-1.5">
          <Shield className="w-3.5 h-3.5" /> Contracting Identity & Legal Framework
        </h4>
        <div className="grid sm:grid-cols-2 md:grid-cols-3 gap-4">
          {renderField(<Shield className="w-3 h-3" />, 'Company Names', entities.company_names, 'companies')}
          {renderField(<UserCheck className="w-3 h-3" />, 'Authorized Signatures', entities.signatures_found, 'signatures')}
          {renderField(<Scale className="w-3 h-3" />, 'Governing Law / Jurisdiction', entities.jurisdiction, 'jurisdiction')}
        </div>
      </div>

      {/* Category: Timelines & Milestones */}
      <div>
        <h4 className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-3 flex items-center gap-1.5">
          <Calendar className="w-3.5 h-3.5" /> Key Dates & Milestones
        </h4>
        <div className="grid sm:grid-cols-2 md:grid-cols-4 gap-4">
          {renderField(<Calendar className="w-3 h-3" />, 'Effective Date', entities.effective_date, 'effective_date')}
          {renderField(<Calendar className="w-3 h-3" />, 'Termination Date', entities.termination_date, 'termination_date')}
          {renderField(<Calendar className="w-3 h-3" />, 'Renewal Window', entities.renewal_date, 'renewal_date')}
          {renderField(<Calendar className="w-3 h-3" />, 'Duration / Term', entities.contract_duration, 'duration')}
        </div>
      </div>

      {/* Category: Commercial Terms */}
      <div>
        <h4 className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-3 flex items-center gap-1.5">
          <DollarSign className="w-3.5 h-3.5" /> Financial & Transaction Parameters
        </h4>
        <div className="grid sm:grid-cols-2 md:grid-cols-4 gap-4">
          {renderField(<DollarSign className="w-3 h-3" />, 'Transaction Amount', entities.payment_amount, 'payment_amount')}
          {renderField(<DollarSign className="w-3 h-3" />, 'Currency', entities.currency, 'currency')}
          {renderField(<DollarSign className="w-3 h-3" />, 'Taxes / VAT / GST', entities.tax_details, 'tax_details')}
          {renderField(<DollarSign className="w-3 h-3" />, 'Payment Due Date', entities.due_date, 'due_date')}
        </div>
      </div>

      {/* Category: Contextual details */}
      <div className="border-t border-slate-900 pt-4 flex flex-col md:flex-row items-start md:items-center justify-between text-[10px] text-slate-500 font-mono gap-2">
        <span>Extraction Reasoning: {entities.reasoning}</span>
        {entities.invoice_number && <span>Invoice #: {entities.invoice_number}</span>}
        {entities.purchase_order_number && <span>Purchase Order #: {entities.purchase_order_number}</span>}
      </div>
    </div>
  );
}
