from google import genai
from backend.agents.context import AgentContext
from backend.models.schemas import NegotiationResult
from backend.services.gemini_service import call_structured_gemini

def run_negotiation_agent(client: genai.Client, context: AgentContext) -> NegotiationResult:
    """
    Generates balanced, industry-standard revision suggestions for high-risk clauses.
    """
    risks_context = ""
    if context.risk_flags:
        for idx, risk in enumerate(context.risk_flags):
            if risk.severity in ["Critical", "High", "Medium"]:
                risks_context += (
                    f"[{idx + 1}] Clause: {risk.clause_name}\n"
                    f"Risk Category: {risk.category}\n"
                    f"Severity: {risk.severity}\n"
                    f"Current Text: \"{risk.text}\"\n"
                    f"Reason: {risk.reasoning}\n\n"
                )
    else:
        risks_context = "No high/critical risks flagged."

    system_instruction = (
        "You are the DocPilot Negotiation Agent. Your task is to draft contract revision "
        "proposals (redlines) for any clause that has been flagged as a Risk (Critical, High, or Medium).\n\n"
        "Generate a professional, commercially balanced, and protective alternative clause text. "
        "Do NOT draft overly aggressive clauses that the counterparty would instantly reject; instead, "
        "provide a standard compromise (e.g., capping liability to 12 months fees, or making termination mutual).\n"
        "Specify: Current Clause (verbatim), Suggested Clause, Reason, and the Expected Risk Reduction (e.g. Critical -> Low)."
    )
    
    prompt = (
        f"--- CURRENT CLAUSES WITH RISK ---\n{risks_context}\n"
        f"Generate negotiation suggestions for these clauses using the NegotiationResult schema."
    )
    
    result = call_structured_gemini(
        client=client,
        prompt=prompt,
        response_schema=NegotiationResult,
        system_instruction=system_instruction
    )
    return result
