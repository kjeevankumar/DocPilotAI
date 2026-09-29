from pydantic import BaseModel
from typing import Optional, List
from backend.models.schemas import (
    DocumentClassificationResult,
    EntityExtractionResult,
    ClauseItem,
    RiskFlagItem,
    BusinessImpactItem,
    ComplianceItem,
    NegotiationItem,
    ExecutiveSummaryResult,
    DecisionRecommendationResult,
    MemoryItem
)

class AgentContext(BaseModel):
    document_id: str
    filename: str
    document_text: str
    classification: Optional[DocumentClassificationResult] = None
    entities: Optional[EntityExtractionResult] = None
    clauses: Optional[List[ClauseItem]] = None
    risk_flags: Optional[List[RiskFlagItem]] = None
    business_impact: Optional[List[BusinessImpactItem]] = None
    missing_clauses: Optional[List[ComplianceItem]] = None
    negotiation_suggestions: Optional[List[NegotiationItem]] = None
    summary: Optional[ExecutiveSummaryResult] = None
    decision: Optional[DecisionRecommendationResult] = None
    recalled_memories: Optional[List[MemoryItem]] = None
    memory_insights: Optional[List[str]] = None
