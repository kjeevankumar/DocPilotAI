from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

# --- Sub-Agent Schemas ---

class DocumentClassificationResult(BaseModel):
    document_type: str = Field(..., description="The classified type of the document (e.g. Contract, Invoice, NDA, Purchase Order, Receipt, Lease Agreement, Service Agreement, etc.)")
    confidence: float = Field(..., description="Confidence score between 0.0 and 1.0")
    reasoning: str = Field(..., description="Explanation for the classification")

class EntityExtractionResult(BaseModel):
    company_names: List[str] = Field(default_factory=list, description="List of companies mentioned")
    person_names: List[str] = Field(default_factory=list, description="List of key individual names mentioned")
    addresses: List[str] = Field(default_factory=list, description="Physical addresses found")
    effective_date: Optional[str] = Field(None, description="Date contract becomes active (YYYY-MM-DD format if possible)")
    termination_date: Optional[str] = Field(None, description="Expiration date of contract (YYYY-MM-DD format if possible)")
    renewal_date: Optional[str] = Field(None, description="Date by which contract renewals must be actioned")
    contract_duration: Optional[str] = Field(None, description="Term/duration of agreement")
    payment_amount: Optional[str] = Field(None, description="Financial transaction or agreement amounts")
    currency: Optional[str] = Field(None, description="Transaction currency (e.g., USD, EUR, INR)")
    tax_details: Optional[str] = Field(None, description="Tax or GST registration IDs and percentages")
    email: Optional[str] = Field(None, description="Contact email addresses")
    phone: Optional[str] = Field(None, description="Contact phone numbers")
    jurisdiction: Optional[str] = Field(None, description="Governing law / state / country jurisdiction")
    signatures_found: List[str] = Field(default_factory=list, description="Names of individuals who signed")
    invoice_number: Optional[str] = Field(None, description="Invoice ID number (if applicable)")
    purchase_order_number: Optional[str] = Field(None, description="Purchase order ID (if applicable)")
    due_date: Optional[str] = Field(None, description="Payment due date (if applicable)")
    reasoning: str = Field(..., description="Reasoning/metadata about extraction process")

class Coordinate(BaseModel):
    page: int = Field(..., description="0-indexed page number")
    box: List[float] = Field(..., description="Bounding box [x0, y0, x1, y1] in PDF points")
    page_width: float = Field(..., description="PDF page width in points")
    page_height: float = Field(..., description="PDF page height in points")

class ClauseItem(BaseModel):
    name: str = Field(..., description="Clause category name (e.g., Payment Terms, Liability, Termination, Confidentiality, IP, Dispute Resolution, Indemnification, Auto Renewal)")
    verbatim_text: str = Field(..., description="The exact text snippet of the clause extracted from the document")
    confidence: float = Field(..., description="Confidence score of detection (0.0 to 1.0)")
    reasoning: str = Field(..., description="Reasoning behind selecting this clause text")
    coordinates: Optional[List[Coordinate]] = Field(None, description="Highlight bounding boxes mapped by PDF processing service")

class ClauseIntelligenceResult(BaseModel):
    clauses: List[ClauseItem] = Field(..., description="List of recognized document clauses")

class RiskFlagItem(BaseModel):
    clause_name: str = Field(..., description="Name of the clause where risk was detected")
    category: str = Field(..., description="Specific risk category (e.g., Unlimited Liability, One-sided Termination, Missing Notice, High Penalty)")
    severity: str = Field(..., description="Risk rating: Critical, High, Medium, Low, Safe")
    text: str = Field(..., description="Verbatim text triggering the risk")
    reasoning: str = Field(..., description="Detailed explanation of the risk finding")
    suggested_action: str = Field(..., description="Actionable recommendation to address the risk")
    confidence: float = Field(..., description="Risk identification confidence (0.0 to 1.0)")
    coordinates: Optional[List[Coordinate]] = Field(None, description="Highlight bounding boxes mapped by PDF processing service")

class RiskIntelligenceResult(BaseModel):
    risk_flags: List[RiskFlagItem] = Field(..., description="List of detected risk items")

class BusinessImpactItem(BaseModel):
    priority: str = Field(..., description="Critical, High, Medium, Low")
    exposure: str = Field(..., description="High, Medium, Low, None")
    explanation: str = Field(..., description="Plain-English explanation of how this affects operations/finance")

class BusinessImpactResult(BaseModel):
    business_impact: List[BusinessImpactItem] = Field(..., description="Business implications of the risk findings")

class ComplianceItem(BaseModel):
    clause_name: str = Field(..., description="Name of required clause (e.g., Force Majeure, Termination Notice, IP Ownership, Confidentiality, Data Privacy, Dispute Resolution)")
    is_present: bool = Field(..., description="True if the clause was detected, False if absent")
    status: str = Field(..., description="Compliant or Non-compliant")
    recommendation: str = Field(..., description="Action to take, especially if missing")

class ComplianceResult(BaseModel):
    missing_clauses: List[ComplianceItem] = Field(..., description="Checklist of essential required clauses and status")

class NegotiationItem(BaseModel):
    clause_name: str = Field(..., description="Name of the clause being negotiated")
    current_clause: str = Field(..., description="Verbatim text of the current high-risk clause")
    suggested_clause: str = Field(..., description="Suggested redline replacement wording")
    reason: str = Field(..., description="Rationale for the suggested wording change")
    risk_reduction: str = Field(..., description="Expected change in risk level (e.g., Critical -> Low)")
    coordinates: Optional[List[Coordinate]] = Field(None, description="Highlight bounding boxes mapped by PDF processing service")

class NegotiationResult(BaseModel):
    negotiation_suggestions: List[NegotiationItem] = Field(..., description="List of proposed clause redlines")

class TimelineItem(BaseModel):
    date: str = Field(..., description="Extracted date (YYYY-MM-DD or readable date)")
    event: str = Field(..., description="Description of the deadline or event (e.g. Termination Notice Deadline, Contract End, Payment Due)")

class ExecutiveSummaryResult(BaseModel):
    business_overview: str = Field(..., description="High-level paragraph describing the document's business purpose")
    key_findings: List[str] = Field(..., description="Key insights or positive highlights")
    major_risks: List[str] = Field(..., description="Summary of the main risk areas")
    critical_dates: List[TimelineItem] = Field(..., description="Key calendar milestones found in the document")
    financial_summary: str = Field(..., description="Summary of financial value, payment schedules, and currency dynamics")
    recommended_actions: List[str] = Field(..., description="Action items sorted by priority")

class DecisionRecommendationResult(BaseModel):
    decision: str = Field(..., description="Final Action: Proceed, Proceed after Negotiation, Requires Legal Review, Reject")
    reasoning: str = Field(..., description="Reasoning for the recommended decision")
    overall_risk_score: int = Field(..., description="Calculated overall business risk score (0-100, where 0 is safest, 100 is highest risk)")

# --- Chat Agent Schemas ---

class ChatMessage(BaseModel):
    role: str = Field(..., description="user or assistant")
    content: str = Field(..., description="Text content of the message")

class ChatRequest(BaseModel):
    document_id: str = Field(..., description="ID of the uploaded document")
    history: List[ChatMessage] = Field(default_factory=list, description="Previous messages in chat")
    message: str = Field(..., description="The user's question about the document")

class ChatResponse(BaseModel):
    answer: str = Field(..., description="Response to the user's question")
    confidence: float = Field(..., description="Confidence score")
    reasoning: str = Field(..., description="Internal thinking process")
    evidence: List[str] = Field(default_factory=list, description="Specific snippets supporting the answer")
    coordinates: Optional[List[Coordinate]] = Field(None, description="Highlight bounding boxes for references")

# --- Consolidated Output payload for UI ---

class DocumentAnalysisResponse(BaseModel):
    document_id: str
    filename: str
    document_type: str
    confidence: float
    overall_risk_score: int
    decision: str
    summary: str
    entities: EntityExtractionResult
    clauses: List[ClauseItem]
    risk_flags: List[RiskFlagItem]
    missing_clauses: List[ComplianceItem]
    business_impact: List[BusinessImpactItem]
    negotiation_suggestions: List[NegotiationItem]
    timeline: List[TimelineItem]
    recommendations: List[str]
    pages_count: int
    processing_time_sec: float
