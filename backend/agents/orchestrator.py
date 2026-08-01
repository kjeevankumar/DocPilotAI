import time
import json
import traceback
from typing import Generator
from google import genai
from backend.agents.context import AgentContext
from backend.services.gemini_service import get_gemini_client
from backend.services.pdf_service import search_text_coordinates
from backend.models.schemas import DocumentAnalysisResponse

# Import specialized agents
from backend.agents.classification import run_classification_agent
from backend.agents.entity_extraction import run_entity_extraction_agent
from backend.agents.clause_intelligence import run_clause_intelligence_agent
from backend.agents.risk_intelligence import run_risk_intelligence_agent
from backend.agents.business_impact import run_business_impact_agent
from backend.agents.compliance import run_compliance_agent
from backend.agents.negotiation import run_negotiation_agent
from backend.agents.executive_summary import run_executive_summary_agent
from backend.agents.decision_recommendation import run_decision_recommendation_agent

def send_sse_event(event: str, data: dict) -> str:
    """Format SSE response string."""
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"

def run_orchestrator(
    api_key: str,
    doc_id: str,
    filename: str,
    pdf_path: str,
    document_text: str,
    pages_count: int
) -> Generator[str, None, None]:
    """
    Coordinates and executes the multi-agent analysis sequence.
    Yields SSE events during execution to update the UI progress bar.
    """
    total_start_time = time.time()
    
    # Yield initial intake success
    yield send_sse_event("agent_complete", {
        "agent": "Document Intake Agent",
        "status": "success",
        "elapsed": 0.1,
        "summary": f"Uploaded {filename} successfully. Pre-rendered {pages_count} page(s)."
    })
    
    # Initialize dynamic client and context
    try:
        client = get_gemini_client(api_key)
    except Exception as e:
        yield send_sse_event("error", {"detail": f"API Client Setup Error: {str(e)}"})
        return

    context = AgentContext(
        document_id=doc_id,
        filename=filename,
        document_text=document_text
    )

    # 1. Document Classification Agent
    yield send_sse_event("agent_start", {"agent": "Document Classification Agent"})
    try:
        t0 = time.time()
        context.classification = run_classification_agent(client, context)
        elapsed = round(time.time() - t0, 2)
        yield send_sse_event("agent_complete", {
            "agent": "Document Classification Agent",
            "status": "success",
            "elapsed": elapsed,
            "summary": f"Classified as '{context.classification.document_type}' (Confidence: {int(context.classification.confidence * 100)}%)."
        })
    except Exception as e:
        yield send_sse_event("agent_complete", {
            "agent": "Document Classification Agent",
            "status": "error",
            "summary": f"Failed classification: {str(e)}"
        })
        # Default fallback
        from backend.models.schemas import DocumentClassificationResult
        context.classification = DocumentClassificationResult(document_type="Contract", confidence=0.5, reasoning="Fallback classification.")

    # 2. Entity Extraction Agent
    yield send_sse_event("agent_start", {"agent": "Entity Extraction Agent"})
    try:
        t0 = time.time()
        context.entities = run_entity_extraction_agent(client, context)
        elapsed = round(time.time() - t0, 2)
        yield send_sse_event("agent_complete", {
            "agent": "Entity Extraction Agent",
            "status": "success",
            "elapsed": elapsed,
            "summary": f"Extracted {len(context.entities.company_names)} parties, dates, values, and jurisdiction."
        })
    except Exception as e:
        yield send_sse_event("agent_complete", {
            "agent": "Entity Extraction Agent",
            "status": "error",
            "summary": f"Failed extraction: {str(e)}"
        })
        from backend.models.schemas import EntityExtractionResult
        context.entities = EntityExtractionResult(reasoning=f"Fallback due to extraction error: {str(e)}")

    # 3. Clause Intelligence Agent
    yield send_sse_event("agent_start", {"agent": "Clause Intelligence Agent"})
    try:
        t0 = time.time()
        clause_res = run_clause_intelligence_agent(client, context)
        context.clauses = clause_res.clauses
        elapsed = round(time.time() - t0, 2)
        yield send_sse_event("agent_complete", {
            "agent": "Clause Intelligence Agent",
            "status": "success",
            "elapsed": elapsed,
            "summary": f"Identified {len(context.clauses)} legal clauses in the text."
        })
    except Exception as e:
        yield send_sse_event("agent_complete", {
            "agent": "Clause Intelligence Agent",
            "status": "error",
            "summary": f"Failed clause analysis: {str(e)}"
        })
        context.clauses = []

    # 4. Risk Intelligence Agent
    yield send_sse_event("agent_start", {"agent": "Risk Intelligence Agent"})
    try:
        t0 = time.time()
        risk_res = run_risk_intelligence_agent(client, context)
        context.risk_flags = risk_res.risk_flags
        elapsed = round(time.time() - t0, 2)
        yield send_sse_event("agent_complete", {
            "agent": "Risk Intelligence Agent",
            "status": "success",
            "elapsed": elapsed,
            "summary": f"Flagged {len(context.risk_flags)} risks ({len([r for r in context.risk_flags if r.severity in ['Critical', 'High']])} Critical/High severity)."
        })
    except Exception as e:
        yield send_sse_event("agent_complete", {
            "agent": "Risk Intelligence Agent",
            "status": "error",
            "summary": f"Failed risk detection: {str(e)}"
        })
        context.risk_flags = []

    # 5. Business Impact Agent
    yield send_sse_event("agent_start", {"agent": "Business Impact Agent"})
    try:
        t0 = time.time()
        impact_res = run_business_impact_agent(client, context)
        context.business_impact = impact_res.business_impact
        elapsed = round(time.time() - t0, 2)
        yield send_sse_event("agent_complete", {
            "agent": "Business Impact Agent",
            "status": "success",
            "elapsed": elapsed,
            "summary": f"Translated findings into {len(context.business_impact)} operational/financial insights."
        })
    except Exception as e:
        yield send_sse_event("agent_complete", {
            "agent": "Business Impact Agent",
            "status": "error",
            "summary": f"Failed business impact analysis: {str(e)}"
        })
        context.business_impact = []

    # 6. Compliance Agent
    yield send_sse_event("agent_start", {"agent": "Compliance Agent"})
    try:
        t0 = time.time()
        comp_res = run_compliance_agent(client, context)
        context.missing_clauses = comp_res.missing_clauses
        elapsed = round(time.time() - t0, 2)
        missing_count = len([m for m in context.missing_clauses if not m.is_present])
        yield send_sse_event("agent_complete", {
            "agent": "Compliance Agent",
            "status": "success",
            "elapsed": elapsed,
            "summary": f"Compliance check completed. Identified {missing_count} missing clauses."
        })
    except Exception as e:
        yield send_sse_event("agent_complete", {
            "agent": "Compliance Agent",
            "status": "error",
            "summary": f"Failed compliance check: {str(e)}"
        })
        context.missing_clauses = []

    # 7. Negotiation Agent
    yield send_sse_event("agent_start", {"agent": "Negotiation Agent"})
    try:
        t0 = time.time()
        neg_res = run_negotiation_agent(client, context)
        context.negotiation_suggestions = neg_res.negotiation_suggestions
        elapsed = round(time.time() - t0, 2)
        yield send_sse_event("agent_complete", {
            "agent": "Negotiation Agent",
            "status": "success",
            "elapsed": elapsed,
            "summary": f"Generated {len(context.negotiation_suggestions)} contract redline suggestions."
        })
    except Exception as e:
        yield send_sse_event("agent_complete", {
            "agent": "Negotiation Agent",
            "status": "error",
            "summary": f"Failed negotiation strategy: {str(e)}"
        })
        context.negotiation_suggestions = []

    # 8. Executive Summary Agent
    yield send_sse_event("agent_start", {"agent": "Executive Summary Agent"})
    try:
        t0 = time.time()
        context.summary = run_executive_summary_agent(client, context)
        elapsed = round(time.time() - t0, 2)
        yield send_sse_event("agent_complete", {
            "agent": "Executive Summary Agent",
            "status": "success",
            "elapsed": elapsed,
            "summary": "Compiled business overview, key findings, and action items."
        })
    except Exception as e:
        yield send_sse_event("agent_complete", {
            "agent": "Executive Summary Agent",
            "status": "error",
            "summary": f"Failed executive summary: {str(e)}"
        })
        from backend.models.schemas import ExecutiveSummaryResult
        context.summary = ExecutiveSummaryResult(
            business_overview="Fallback due to summary error.",
            key_findings=[],
            major_risks=[],
            critical_dates=[],
            financial_summary="Fallback financial summary.",
            recommended_actions=[]
        )

    # 9. Decision Recommendation Agent
    yield send_sse_event("agent_start", {"agent": "Decision Recommendation Agent"})
    try:
        t0 = time.time()
        context.decision = run_decision_recommendation_agent(client, context)
        elapsed = round(time.time() - t0, 2)
        yield send_sse_event("agent_complete", {
            "agent": "Decision Recommendation Agent",
            "status": "success",
            "elapsed": elapsed,
            "summary": f"Decision issued: '{context.decision.decision}' (Overall Risk Score: {context.decision.overall_risk_score}/100)."
        })
    except Exception as e:
        yield send_sse_event("agent_complete", {
            "agent": "Decision Recommendation Agent",
            "status": "error",
            "summary": f"Failed final decision: {str(e)}"
        })
        from backend.models.schemas import DecisionRecommendationResult
        context.decision = DecisionRecommendationResult(decision="Requires Legal Review", reasoning="Fallback recommendation.", overall_risk_score=75)

    # 10. Bounding-Box Highlight Coordinate Search (Post-processing Step)
    yield send_sse_event("agent_start", {"agent": "Highlight Coordinate Mapping"})
    t_start = time.time()
    try:
        # Resolve coordinates for clauses
        if context.clauses:
            for clause in context.clauses:
                clause.coordinates = search_text_coordinates(pdf_path, clause.verbatim_text)
                
        # Resolve coordinates for risks
        if context.risk_flags:
            for risk in context.risk_flags:
                risk.coordinates = search_text_coordinates(pdf_path, risk.text)
                
        # Resolve coordinates for negotiation clauses
        if context.negotiation_suggestions:
            for suggestion in context.negotiation_suggestions:
                suggestion.coordinates = search_text_coordinates(pdf_path, suggestion.current_clause)
                
        elapsed = round(time.time() - t_start, 2)
        yield send_sse_event("agent_complete", {
            "agent": "Highlight Coordinate Mapping",
            "status": "success",
            "elapsed": elapsed,
            "summary": "Completed search coordinate highlights. Mapping finished."
        })
    except Exception as e:
        yield send_sse_event("agent_complete", {
            "agent": "Highlight Coordinate Mapping",
            "status": "error",
            "summary": f"Failed coordinate mapping: {str(e)}"
        })

    # Final Payload Synthesis
    total_processing_time = round(time.time() - total_start_time, 2)
    
    # Save the consolidated context to a JSON file so that Q&A chat endpoints can reference it
    context_file = pdf_path + ".analysis.json"
    try:
        with open(context_file, "w", encoding="utf-8") as f:
            f.write(context.model_dump_json(indent=2))
    except Exception as e:
        print(f"Error saving analysis state file: {e}")

    try:
        # Build DocumentAnalysisResponse
        response_payload = DocumentAnalysisResponse(
            document_id=doc_id,
            filename=filename,
            document_type=context.classification.document_type if context.classification else "Contract",
            confidence=context.classification.confidence if context.classification else 0.8,
            overall_risk_score=context.decision.overall_risk_score if context.decision else 50,
            decision=context.decision.decision if context.decision else "Requires Legal Review",
            summary=context.summary.business_overview if context.summary else "",
            entities=context.entities if context.entities else None,
            clauses=context.clauses or [],
            risk_flags=context.risk_flags or [],
            missing_clauses=context.missing_clauses or [],
            business_impact=context.business_impact or [],
            negotiation_suggestions=context.negotiation_suggestions or [],
            timeline=context.summary.critical_dates if context.summary else [],
            recommendations=context.summary.recommended_actions if context.summary else [],
            pages_count=pages_count,
            processing_time_sec=total_processing_time
        )
        
        # Yield the final compiled response
        yield send_sse_event("pipeline_complete", response_payload.model_dump())
        
    except Exception as e:
        traceback.print_exc()
        yield send_sse_event("error", {"detail": f"Error synthesizing final payload: {str(e)}"})
