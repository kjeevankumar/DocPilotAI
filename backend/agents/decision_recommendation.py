from google import genai
from backend.agents.context import AgentContext
from backend.models.schemas import DecisionRecommendationResult
from backend.services.gemini_service import call_structured_gemini

def run_decision_recommendation_agent(client: genai.Client, context: AgentContext) -> DecisionRecommendationResult:
    """
    Grades the document, calculating an overall risk score and providing a final action decision.
    """
    summary_context = ""
    if context.summary:
        summary_context += f"Business Overview: {context.summary.business_overview}\n"
    if context.risk_flags:
        summary_context += "Risks:\n"
        for r in context.risk_flags:
            summary_context += f"- [{r.severity}] {r.clause_name}: {r.category} ({r.reasoning})\n"
    if context.missing_clauses:
        missing = [m.clause_name for m in context.missing_clauses if not m.is_present]
        summary_context += f"Missing Clauses: {', '.join(missing)}\n"
        
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
        f"--- CURRENT SUMMARY & RISK FINDINGS ---\n{summary_context}\n\n"
        f"Determine the final recommendation decision and risk score."
    )
    
    result = call_structured_gemini(
        client=client,
        prompt=prompt,
        response_schema=DecisionRecommendationResult,
        system_instruction=system_instruction
    )
    return result
