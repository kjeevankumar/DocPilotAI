from google import genai
from backend.agents.context import AgentContext
from backend.models.schemas import RiskIntelligenceResult
from backend.services.gemini_service import call_structured_gemini

def run_risk_intelligence_agent(client: genai.Client, context: AgentContext) -> RiskIntelligenceResult:
    """
    Evaluates extracted clauses for financial, legal, and operational risks.
    """
    clauses_context = ""
    if context.clauses:
        for idx, clause in enumerate(context.clauses):
            clauses_context += f"[{idx + 1}] Clause: {clause.name}\nText: \"{clause.verbatim_text}\"\n\n"
    else:
        clauses_context = "No clauses extracted by the Clause Intelligence Agent."

    system_instruction = (
        "You are the DocPilot Risk Intelligence Agent. Your role is to examine the contract clauses "
        "and determine if they pose legal, financial, or operational risks to the organization.\n\n"
        "Risk Levels:\n"
        "- Critical: Extremely high risk, e.g., unlimited liability, immediate one-sided termination with no notice, high immediate financial penalties.\n"
        "- High: Serious exposure, e.g., auto-renewal with long lock-in, ambiguous IP ownership, weak indemnification protection.\n"
        "- Medium: Moderate exposure, e.g., auto-renewal, standard liability caps, one-sided confidentiality terms.\n"
        "- Low: Minor exposure, standard terms but slightly unbalanced.\n"
        "- Safe: Standard mutual terms with no notable risk.\n\n"
        "For each clause, assign a risk category, severity level, provide clear reasoning, and outline "
        "a suggested action to mitigate this risk. You must use the verbatim text of the risk-triggering section."
    )
    
    prompt = (
        f"--- EXTRACTED CLAUSES ---\n{clauses_context}\n"
        f"Analyze these clauses and flag any risks. Respond in the RiskIntelligenceResult schema."
    )
    
    result = call_structured_gemini(
        client=client,
        prompt=prompt,
        response_schema=RiskIntelligenceResult,
        system_instruction=system_instruction
    )
    return result
