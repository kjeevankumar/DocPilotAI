export interface Coordinate {
  page: number;
  box: [number, number, number, number]; // [x0, y0, x1, y1]
  page_width: number;
  page_height: number;
}

export interface ClauseItem {
  name: string;
  verbatim_text: string;
  confidence: number;
  reasoning: string;
  coordinates?: Coordinate[];
}

export interface RiskFlagItem {
  clause_name: string;
  category: string;
  severity: 'Critical' | 'High' | 'Medium' | 'Low' | 'Safe';
  text: string;
  reasoning: string;
  suggested_action: string;
  confidence: number;
  coordinates?: Coordinate[];
}

export interface BusinessImpactItem {
  priority: 'Critical' | 'High' | 'Medium' | 'Low';
  exposure: 'High' | 'Medium' | 'Low' | 'None';
  explanation: string;
}

export interface ComplianceItem {
  clause_name: string;
  is_present: boolean;
  status: 'Compliant' | 'Non-compliant';
  recommendation: string;
}

export interface NegotiationItem {
  clause_name: string;
  current_clause: string;
  suggested_clause: string;
  reason: string;
  risk_reduction: string;
  coordinates?: Coordinate[];
}

export interface TimelineItem {
  date: string;
  event: string;
}

export interface EntityExtractionResult {
  company_names: string[];
  person_names: string[];
  addresses: string[];
  effective_date: string | null;
  termination_date: string | null;
  renewal_date: string | null;
  contract_duration: string | null;
  payment_amount: string | null;
  currency: string | null;
  tax_details: string | null;
  email: string | null;
  phone: string | null;
  jurisdiction: string | null;
  signatures_found: string[];
  invoice_number: string | null;
  purchase_order_number: string | null;
  due_date: string | null;
  reasoning: string;
}

export interface DocumentAnalysisResponse {
  document_id: string;
  filename: string;
  document_type: string;
  confidence: number;
  overall_risk_score: number;
  decision: string;
  summary: string;
  entities: EntityExtractionResult;
  clauses: ClauseItem[];
  risk_flags: RiskFlagItem[];
  missing_clauses: ComplianceItem[];
  business_impact: BusinessImpactItem[];
  negotiation_suggestions: NegotiationItem[];
  timeline: TimelineItem[];
  recommendations: string[];
  pages_count: number;
  processing_time_sec: number;
}

export interface AgentLog {
  agent: string;
  status: 'pending' | 'processing' | 'success' | 'error';
  elapsed?: number;
  summary?: string;
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}
