import time
from google import genai
from backend.agents.context import AgentContext
from backend.models.schemas import RiskIntelligenceResult
from backend.services.gemini_service import call_structured_gemini

def run_risk_intelligence_agent(client: genai.Client, context: AgentContext) -> RiskIntelligenceResult:
    """
    Evaluates extracted clauses AND raw document text for financial, legal, and operational risks.
    Always includes document text as a direct anchor so even if clause extraction fails upstream,
    the risk agent can still find risks in the raw document.
    """
    t0 = time.time()
    doc_type = context.classification.document_type if context.classification else "Unknown"

    clauses_context = ""
    if context.clauses:
        for idx, clause in enumerate(context.clauses):
            clauses_context += f"[{idx + 1}] Clause: {clause.name}\nText: \"{clause.verbatim_text}\"\n\n"
    else:
        clauses_context = "No clauses extracted by the Clause Intelligence Agent — analyze the raw document text below directly."

    # Always include raw document text so the agent can find risks even when clauses are empty
    doc_text_anchor = context.document_text[:5000] if context.document_text else ""

    print(f"[RISK_AGENT] Document type: {doc_type} | Clauses: {len(context.clauses or [])} | Doc text chars: {len(doc_text_anchor)}")

    system_instruction = (
        "You are the DocPilot Risk Intelligence Agent. Your role is to examine the contract clauses "
        "and raw document text to determine if they pose legal, financial, or operational risks.\n\n"
        "Risk Levels:\n"
        "- Critical: Extremely high risk, e.g., unlimited liability, immediate one-sided termination with no notice, high immediate financial penalties.\n"
        "- High: Serious exposure, e.g., auto-renewal with long lock-in, ambiguous IP ownership, weak indemnification protection.\n"
        "- Medium: Moderate exposure, e.g., auto-renewal, standard liability caps, one-sided confidentiality terms.\n"
        "- Low: Minor exposure, standard terms but slightly unbalanced.\n"
        "- Safe: Standard mutual terms with no notable risk.\n\n"
        "For each risk, assign a risk category, severity level, provide clear reasoning, and outline "
        "a suggested action to mitigate this risk. You MUST extract the verbatim text of the risk-triggering section."
    )

    prompt = (
        f"Document Type: {doc_type}\n\n"
        f"--- EXTRACTED CLAUSES (from upstream Clause Intelligence Agent) ---\n{clauses_context}\n\n"
        f"--- RAW DOCUMENT TEXT (direct anchor — analyze for additional risks not covered above) ---\n{doc_text_anchor}\n\n"
        f"Analyze BOTH the extracted clauses AND the raw document text above. Flag all risks in the RiskIntelligenceResult schema."
    )

    print(f"[RISK_AGENT] Prompt length: {len(prompt)} chars")
    result = call_structured_gemini(
        client=client,
        prompt=prompt,
        response_schema=RiskIntelligenceResult,
        system_instruction=system_instruction
    )
    elapsed = round(time.time() - t0, 2)
    print(f"[RISK_AGENT] Done | Risks found: {len(result.risk_flags)} | Elapsed: {elapsed}s")
    return result
