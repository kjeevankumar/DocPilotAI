from google import genai
from backend.agents.context import AgentContext
from backend.models.schemas import ExecutiveSummaryResult
from backend.services.gemini_service import call_structured_gemini

def run_executive_summary_agent(client: genai.Client, context: AgentContext) -> ExecutiveSummaryResult:
    """
    Synthesizes classification, entities, risks, and compliance gaps into an executive-ready business summary.
    """
    # Compile cumulative context summary
    context_summary = f"Filename: {context.filename}\n"
    if context.classification:
        context_summary += f"Document Type: {context.classification.document_type} (Confidence: {context.classification.confidence})\n"
    if context.entities:
        context_summary += (
            f"Parties: {', '.join(context.entities.company_names)}\n"
            f"Effective Date: {context.entities.effective_date}\n"
            f"Termination Date: {context.entities.termination_date}\n"
            f"Value/Amount: {context.entities.payment_amount} {context.entities.currency}\n"
        )
    if context.risk_flags:
        context_summary += f"Total Risks Found: {len(context.risk_flags)} ({len([r for r in context.risk_flags if r.severity == 'Critical'])} critical)\n"
    if context.missing_clauses:
        context_summary += f"Missing Clauses: {', '.join([c.clause_name for c in context.missing_clauses if not c.is_present])}\n"
        
    system_instruction = (
        "You are the DocPilot Executive Summary Agent. Your task is to review all the extracted "
        "insights, risks, compliance status, and metadata of the document, and compile a "
        "polished Executive Summary.\n\n"
        "Your output must cover:\n"
        "1. Business Overview: A concise paragraph on what this document does.\n"
        "2. Key Findings: Main takeaways or positive points (e.g. mutual terms).\n"
        "3. Major Risks: High-level summary of the critical exposures.\n"
        "4. Critical Dates: A timeline list of dates and events (e.g. Expiration, renewals).\n"
        "5. Financial Summary: Brief writeup of fees, payments, taxes, and obligations.\n"
        "6. Recommended Actions: High-level checklist of recommended steps.\n"
        "Keep your tone highly professional, clear, and business-focused."
    )
    
    prompt = (
        f"--- ANALYSIS SUMMARY METADATA ---\n{context_summary}\n\n"
        f"--- DOCUMENT TEXT ---\n{context.document_text[:8000]}\n\n"  # Clip if too long
        f"Synthesize the complete summary and timeline items."
    )
    
    result = call_structured_gemini(
        client=client,
        prompt=prompt,
        response_schema=ExecutiveSummaryResult,
        system_instruction=system_instruction
    )
    return result
