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
from backend.agents.hindsight_memory_agent import run_hindsight_memory_agent

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

    # ── DEBUG: Pipeline startup banner ──────────────────────────────────────
    print(f"\n{'#'*70}")
    print(f"[ORCHESTRATOR] Pipeline starting for: {filename}")
    print(f"[ORCHESTRATOR] Document ID: {doc_id}")
    print(f"[ORCHESTRATOR] PDF Path: {pdf_path}")
    print(f"[ORCHESTRATOR] Pages: {pages_count}")
    print(f"[ORCHESTRATOR] Extracted Text Length: {len(document_text)} chars")
    print(f"[ORCHESTRATOR] First 500 chars of text:")
    print(f"{document_text[:500]}")
    print(f"{'#'*70}\n")
    # ────────────────────────────────────────────────────────────────────────

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
    print(f"[ORCHESTRATOR] >>> Calling Classification Agent...")
    yield send_sse_event("agent_start", {"agent": "Document Classification Agent"})
    try:
        t0 = time.time()
        context.classification = run_classification_agent(client, context)
        elapsed = round(time.time() - t0, 2)
        print(f"[ORCHESTRATOR] Classification Agent DONE | Result: {context.classification.document_type} ({int(context.classification.confidence*100)}%) | Elapsed: {elapsed}s")
        yield send_sse_event("agent_complete", {
            "agent": "Document Classification Agent",
            "status": "success",
            "elapsed": elapsed,
            "summary": f"Classified as '{context.classification.document_type}' (Confidence: {int(context.classification.confidence * 100)}%)."
        })
    except Exception as e:
        print(f"[ORCHESTRATOR] Classification Agent ERROR: {e}")
        yield send_sse_event("agent_complete", {
            "agent": "Document Classification Agent",
            "status": "error",
            "summary": f"Failed classification: {str(e)}"
        })
        # Default fallback
        from backend.models.schemas import DocumentClassificationResult
        context.classification = DocumentClassificationResult(document_type="Contract", confidence=0.5, reasoning="Fallback classification.")

    # 2. Entity Extraction Agent
    print(f"[ORCHESTRATOR] >>> Calling Entity Extraction Agent... (doc_text={len(document_text)} chars)")
    yield send_sse_event("agent_start", {"agent": "Entity Extraction Agent"})
    try:
        t0 = time.time()
        context.entities = run_entity_extraction_agent(client, context)
        elapsed = round(time.time() - t0, 2)
        print(f"[ORCHESTRATOR] Entity Extraction DONE | Companies: {context.entities.company_names} | Elapsed: {elapsed}s")
        yield send_sse_event("agent_complete", {
            "agent": "Entity Extraction Agent",
            "status": "success",
            "elapsed": elapsed,
            "summary": f"Extracted {len(context.entities.company_names)} parties, dates, values, and jurisdiction."
        })
    except Exception as e:
        print(f"[ORCHESTRATOR] Entity Extraction ERROR: {e}")
        yield send_sse_event("agent_complete", {
            "agent": "Entity Extraction Agent",
            "status": "error",
            "summary": f"Failed extraction: {str(e)}"
        })
        from backend.models.schemas import EntityExtractionResult
        context.entities = EntityExtractionResult(reasoning=f"Fallback due to extraction error: {str(e)}")

    # 3. Clause Intelligence Agent
    print(f"[ORCHESTRATOR] >>> Calling Clause Intelligence Agent...")
    yield send_sse_event("agent_start", {"agent": "Clause Intelligence Agent"})
    try:
        t0 = time.time()
        clause_res = run_clause_intelligence_agent(client, context)
        context.clauses = clause_res.clauses
        elapsed = round(time.time() - t0, 2)
        print(f"[ORCHESTRATOR] Clause Intelligence DONE | Clauses: {[c.name for c in context.clauses]} | Elapsed: {elapsed}s")
        yield send_sse_event("agent_complete", {
            "agent": "Clause Intelligence Agent",
            "status": "success",
            "elapsed": elapsed,
            "summary": f"Identified {len(context.clauses)} legal clauses in the text."
        })
    except Exception as e:
        print(f"[ORCHESTRATOR] Clause Intelligence ERROR: {e}")
        yield send_sse_event("agent_complete", {
            "agent": "Clause Intelligence Agent",
            "status": "error",
            "summary": f"Failed clause analysis: {str(e)}"
        })
        context.clauses = []

    # 4. Risk Intelligence Agent
    print(f"[ORCHESTRATOR] >>> Calling Risk Intelligence Agent... ({len(context.clauses or [])} clauses to analyze)")
    yield send_sse_event("agent_start", {"agent": "Risk Intelligence Agent"})
    try:
        t0 = time.time()
        risk_res = run_risk_intelligence_agent(client, context)
        context.risk_flags = risk_res.risk_flags
        elapsed = round(time.time() - t0, 2)
        critical_high = len([r for r in context.risk_flags if r.severity in ['Critical', 'High']])
        print(f"[ORCHESTRATOR] Risk Intelligence DONE | Risks: {len(context.risk_flags)} ({critical_high} Critical/High) | Elapsed: {elapsed}s")
        yield send_sse_event("agent_complete", {
            "agent": "Risk Intelligence Agent",
            "status": "success",
            "elapsed": elapsed,
            "summary": f"Flagged {len(context.risk_flags)} risks ({critical_high} Critical/High severity)."
        })
    except Exception as e:
        print(f"[ORCHESTRATOR] Risk Intelligence ERROR: {e}")
        yield send_sse_event("agent_complete", {
            "agent": "Risk Intelligence Agent",
            "status": "error",
            "summary": f"Failed risk detection: {str(e)}"
        })
        context.risk_flags = []

    # 5. Business Impact Agent
    print(f"[ORCHESTRATOR] >>> Calling Business Impact Agent... ({len(context.risk_flags or [])} risks to translate)")
    yield send_sse_event("agent_start", {"agent": "Business Impact Agent"})
    try:
        t0 = time.time()
        impact_res = run_business_impact_agent(client, context)
        context.business_impact = impact_res.business_impact
        elapsed = round(time.time() - t0, 2)
        print(f"[ORCHESTRATOR] Business Impact DONE | Impacts: {len(context.business_impact)} | Elapsed: {elapsed}s")
        yield send_sse_event("agent_complete", {
            "agent": "Business Impact Agent",
            "status": "success",
            "elapsed": elapsed,
            "summary": f"Translated findings into {len(context.business_impact)} operational/financial insights."
        })
    except Exception as e:
        print(f"[ORCHESTRATOR] Business Impact ERROR: {e}")
        yield send_sse_event("agent_complete", {
            "agent": "Business Impact Agent",
            "status": "error",
            "summary": f"Failed business impact analysis: {str(e)}"
        })
        context.business_impact = []

    # 6. Compliance Agent
    print(f"[ORCHESTRATOR] >>> Calling Compliance Agent...")
    yield send_sse_event("agent_start", {"agent": "Compliance Agent"})
    try:
        t0 = time.time()
        comp_res = run_compliance_agent(client, context)
        context.missing_clauses = comp_res.missing_clauses
        elapsed = round(time.time() - t0, 2)
        missing_count = len([m for m in context.missing_clauses if not m.is_present])
        print(f"[ORCHESTRATOR] Compliance DONE | Clauses checked: {len(context.missing_clauses)} | Missing: {missing_count} | Elapsed: {elapsed}s")
        yield send_sse_event("agent_complete", {
            "agent": "Compliance Agent",
            "status": "success",
            "elapsed": elapsed,
            "summary": f"Compliance check completed. Identified {missing_count} missing clauses."
        })
    except Exception as e:
        print(f"[ORCHESTRATOR] Compliance ERROR: {e}")
        yield send_sse_event("agent_complete", {
            "agent": "Compliance Agent",
            "status": "error",
            "summary": f"Failed compliance check: {str(e)}"
        })
        context.missing_clauses = []

    # 7. Negotiation Agent
    print(f"[ORCHESTRATOR] >>> Calling Negotiation Agent...")
    yield send_sse_event("agent_start", {"agent": "Negotiation Agent"})
    try:
        t0 = time.time()
        neg_res = run_negotiation_agent(client, context)
        context.negotiation_suggestions = neg_res.negotiation_suggestions
        elapsed = round(time.time() - t0, 2)
        print(f"[ORCHESTRATOR] Negotiation DONE | Suggestions: {len(context.negotiation_suggestions)} | Elapsed: {elapsed}s")
        yield send_sse_event("agent_complete", {
            "agent": "Negotiation Agent",
            "status": "success",
            "elapsed": elapsed,
            "summary": f"Generated {len(context.negotiation_suggestions)} contract redline suggestions."
        })
    except Exception as e:
        print(f"[ORCHESTRATOR] Negotiation ERROR: {e}")
        yield send_sse_event("agent_complete", {
            "agent": "Negotiation Agent",
            "status": "error",
            "summary": f"Failed negotiation strategy: {str(e)}"
        })
        context.negotiation_suggestions = []

    # 8. Executive Summary Agent
    print(f"[ORCHESTRATOR] >>> Calling Executive Summary Agent...")
    yield send_sse_event("agent_start", {"agent": "Executive Summary Agent"})
    try:
        t0 = time.time()
        context.summary = run_executive_summary_agent(client, context)
        elapsed = round(time.time() - t0, 2)
        overview_preview = (context.summary.business_overview or "")[:100]
        print(f"[ORCHESTRATOR] Executive Summary DONE | Overview preview: '{overview_preview}...' | Elapsed: {elapsed}s")
        yield send_sse_event("agent_complete", {
            "agent": "Executive Summary Agent",
            "status": "success",
            "elapsed": elapsed,
            "summary": "Compiled business overview, key findings, and action items."
        })
    except Exception as e:
        print(f"[ORCHESTRATOR] Executive Summary ERROR: {e}")
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
    print(f"[ORCHESTRATOR] >>> Calling Decision Recommendation Agent...")
    yield send_sse_event("agent_start", {"agent": "Decision Recommendation Agent"})
    try:
        t0 = time.time()
        context.decision = run_decision_recommendation_agent(client, context)
        elapsed = round(time.time() - t0, 2)
        print(f"[ORCHESTRATOR] Decision Recommendation DONE | Decision: '{context.decision.decision}' | Risk Score: {context.decision.overall_risk_score}/100 | Elapsed: {elapsed}s")
        yield send_sse_event("agent_complete", {
            "agent": "Decision Recommendation Agent",
            "status": "success",
            "elapsed": elapsed,
            "summary": f"Decision issued: '{context.decision.decision}' (Overall Risk Score: {context.decision.overall_risk_score}/100)."
        })
    except Exception as e:
        print(f"[ORCHESTRATOR] Decision Recommendation ERROR: {e}")
        yield send_sse_event("agent_complete", {
            "agent": "Decision Recommendation Agent",
            "status": "error",
            "summary": f"Failed final decision: {str(e)}"
        })
        from backend.models.schemas import DecisionRecommendationResult
        context.decision = DecisionRecommendationResult(decision="Requires Legal Review", reasoning="Fallback recommendation.", overall_risk_score=75)

    # 10. Hindsight Memory Agent (Precedent Recall & Cross-Contract Learning)
    print(f"[ORCHESTRATOR] >>> Calling Hindsight Memory Agent...")
    yield send_sse_event("agent_start", {"agent": "Hindsight Memory Agent"})
    try:
        t0 = time.time()
        recalled_mem, mem_insights = run_hindsight_memory_agent(context)
        context.recalled_memories = recalled_mem
        context.memory_insights = mem_insights
        elapsed = round(time.time() - t0, 2)
        print(f"[ORCHESTRATOR] Hindsight Memory DONE | Recalled: {len(recalled_mem)} memories | Insights: {len(mem_insights)} | Elapsed: {elapsed}s")
        yield send_sse_event("agent_complete", {
            "agent": "Hindsight Memory Agent",
            "status": "success",
            "elapsed": elapsed,
            "summary": f"Recalled {len(recalled_mem)} institutional precedents. Applied {len(mem_insights)} cross-contract insights."
        })
    except Exception as e:
        print(f"[ORCHESTRATOR] Hindsight Memory ERROR: {e}")
        yield send_sse_event("agent_complete", {
            "agent": "Hindsight Memory Agent",
            "status": "error",
            "summary": f"Failed memory recall: {str(e)}"
        })
        context.recalled_memories = []
        context.memory_insights = []

    # 11. Bounding-Box Highlight Coordinate Search (Post-processing Step)
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

    # ── DEBUG: Pipeline completion summary ──────────────────────────────────
    total_processing_time = round(time.time() - total_start_time, 2)
    print(f"\n{'#'*70}")
    print(f"[ORCHESTRATOR] ✅ Pipeline complete for: {filename}")
    print(f"[ORCHESTRATOR] Total processing time: {total_processing_time}s")
    print(f"[ORCHESTRATOR] Summary: type={context.classification.document_type if context.classification else 'N/A'} | "
          f"risk_score={context.decision.overall_risk_score if context.decision else 'N/A'} | "
          f"decision={context.decision.decision if context.decision else 'N/A'} | "
          f"clauses={len(context.clauses or [])} | risks={len(context.risk_flags or [])} | "
          f"recalled_memories={len(context.recalled_memories or [])} | "
          f"entities={context.entities.company_names if context.entities else []}")
    print(f"{'#'*70}\n")
    # ────────────────────────────────────────────────────────────────────────

    # Final Payload Synthesis
    
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
            processing_time_sec=total_processing_time,
            recalled_memories=context.recalled_memories or [],
            memory_insights=context.memory_insights or []
        )
        
        # Yield the final compiled response
        yield send_sse_event("pipeline_complete", response_payload.model_dump())
        
    except Exception as e:
        traceback.print_exc()
        yield send_sse_event("error", {"detail": f"Error synthesizing final payload: {str(e)}"})
