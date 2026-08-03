import time
from google import genai
from backend.agents.context import AgentContext
from backend.models.schemas import DecisionRecommendationResult
from backend.services.gemini_service import call_structured_gemini

def run_decision_recommendation_agent(client: genai.Client, context: AgentContext) -> DecisionRecommendationResult:
    """
    Grades the document, calculating an overall risk score and providing a final action decision.
    Always includes document metadata and a raw text anchor so the decision is never made blindly.
    """
    t0 = time.time()

    # Build structured summary of prior agents' outputs
    summary_context = ""
    if context.classification:
        summary_context += f"Document Type: {context.classification.document_type} (Confidence: {int(context.classification.confidence*100)}%)\n"
    if context.entities:
        parties = ', '.join(context.entities.company_names) if context.entities.company_names else 'Unknown'
        summary_context += f"Parties: {parties}\n"
        if context.entities.payment_amount:
            summary_context += f"Financial Value: {context.entities.payment_amount} {context.entities.currency or ''}\n"
        if context.entities.jurisdiction:
            summary_context += f"Jurisdiction: {context.entities.jurisdiction}\n"
    if context.summary:
        summary_context += f"Business Overview: {context.summary.business_overview}\n"
    if context.risk_flags:
        summary_context += f"Total Risks: {len(context.risk_flags)}\nRisks:\n"
        for r in context.risk_flags:
            summary_context += f"- [{r.severity}] {r.clause_name}: {r.category} — {r.reasoning}\n"
    if context.missing_clauses:
        missing = [m.clause_name for m in context.missing_clauses if not m.is_present]
        if missing:
            summary_context += f"Missing Clauses: {', '.join(missing)}\n"

    # If summary_context is thin (upstream failures), fall back to raw doc text anchor
    doc_text_anchor = ""
    if len(summary_context) < 200 and context.document_text:
        doc_text_anchor = f"\n--- RAW DOCUMENT EXCERPT (upstream agents returned limited data) ---\n{context.document_text[:3000]}\n"

    print(f"[DECISION_AGENT] Summary context length: {len(summary_context)} chars | Doc anchor: {len(doc_text_anchor)} chars")

    system_instruction = (
        "You are the DocPilot Decision Recommendation Agent. Your job is to make a final business decision "
        "recommendation on whether the organization should execute this document.\n\n"
        "Possible Decision Outputs:\n"
        "- Proceed: The document is extremely safe and has standard, balanced clauses.\n"
        "- Proceed after Negotiation: The document is acceptable overall, but has critical/high-risk clauses that must be redlined first.\n"
        "- Requires Legal Review: The document contains complex, custom, or highly non-standard clauses that must be evaluated by a lawyer.\n"
        "- Reject: The document contains severe liabilities, compliance violations, or predatory terms that cannot be resolved through basic negotiation.\n\n"
        "Calculate an overall_risk_score from 0 to 100:\n"
        "- 0-25: Safe/Low Risk\n"
        "- 26-55: Medium Risk\n"
        "- 56-80: High Risk\n"
        "- 81-100: Critical Risk\n"
        "Provide thorough, professional business reasoning for your decision."
    )

    prompt = (
        f"--- ANALYSIS SUMMARY FROM UPSTREAM AGENTS ---\n{summary_context}\n"
        f"{doc_text_anchor}\n"
        f"Based on all evidence above, determine the final recommendation decision and overall risk score."
    )

    print(f"[DECISION_AGENT] Prompt length: {len(prompt)} chars")
    result = call_structured_gemini(
        client=client,
        prompt=prompt,
        response_schema=DecisionRecommendationResult,
        system_instruction=system_instruction
    )
    elapsed = round(time.time() - t0, 2)
    print(f"[DECISION_AGENT] Done | Decision: {result.decision} | Risk Score: {result.overall_risk_score} | Elapsed: {elapsed}s")
    return result
