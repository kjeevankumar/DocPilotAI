from google import genai
from backend.agents.context import AgentContext
from backend.models.schemas import ComplianceResult
from backend.services.gemini_service import call_structured_gemini

def run_compliance_agent(client: genai.Client, context: AgentContext) -> ComplianceResult:
    """
    Checks for the existence of mandatory clauses and detects compliance gaps.
    """
    doc_type = context.classification.document_type if context.classification else "NDA"
    clauses_list = [c.name.lower() for c in context.clauses] if context.clauses else []
    
    system_instruction = (
        "You are the DocPilot Compliance Agent. Your task is to verify if standard mandatory "
        f"clauses required for a '{doc_type}' are present in the document. Checklist of standard clauses:\n"
        "- Force Majeure\n"
        "- Termination Notice\n"
        "- Confidentiality\n"
        "- Data Privacy / GDPR compliance\n"
        "- Intellectual Property (IP) Ownership\n"
        "- Payment Schedule / Terms\n"
        "- Dispute Resolution\n"
        "- Governing Law / Jurisdiction\n\n"
        "Analyze the document text and the list of extracted clauses. Determine if each of these required clauses "
        "is present. If present, mark is_present=True and status='Compliant'. If absent, mark is_present=False, "
        "status='Non-compliant', and provide a clear recommendation on what clause text should be added."
    )
    
    prompt = (
        f"Document Classification: {doc_type}\n"
        f"Extracted Clause Names: {clauses_list}\n\n"
        f"--- DOCUMENT TEXT ---\n{context.document_text}\n\n"
        f"Run compliance check and respond with the ComplianceResult schema."
    )
    
    result = call_structured_gemini(
        client=client,
        prompt=prompt,
        response_schema=ComplianceResult,
        system_instruction=system_instruction
    )
    return result
