from google import genai
from backend.agents.context import AgentContext
from backend.models.schemas import BusinessImpactResult
from backend.services.gemini_service import call_structured_gemini

def run_business_impact_agent(client: genai.Client, context: AgentContext) -> BusinessImpactResult:
    """
    Translates legal and financial risks into clear business implications, estimating financial exposure.
    """
    risks_context = ""
    if context.risk_flags:
        for idx, risk in enumerate(context.risk_flags):
            risks_context += (
                f"[{idx + 1}] Clause: {risk.clause_name}\n"
                f"Risk Category: {risk.category}\n"
                f"Severity: {risk.severity}\n"
                f"Text: \"{risk.text}\"\n"
                f"Reasoning: {risk.reasoning}\n\n"
            )
    else:
        risks_context = "No risks flagged."

    system_instruction = (
        "You are the DocPilot Business Impact Agent. Your role is to translate legal/risk findings "
        "into clear, jargon-free business language that non-legal personnel (like executives, product "
        "owners, or procurement managers) can immediately understand.\n\n"
        "Explain what the finding means in practical terms, estimate the financial exposure (High, "
        "Medium, Low, None), and set a business priority level (Critical, High, Medium, Low)."
    )
    
    prompt = (
        f"--- DETECTED RISKS ---\n{risks_context}\n"
        f"Translate these risks into plain business impacts using the BusinessImpactResult schema."
    )
    
    result = call_structured_gemini(
        client=client,
        prompt=prompt,
        response_schema=BusinessImpactResult,
        system_instruction=system_instruction
    )
    return result
