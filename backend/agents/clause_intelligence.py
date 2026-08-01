from google import genai
from backend.agents.context import AgentContext
from backend.models.schemas import ClauseIntelligenceResult
from backend.services.gemini_service import call_structured_gemini

def run_clause_intelligence_agent(client: genai.Client, context: AgentContext) -> ClauseIntelligenceResult:
    """
    Identifies contract clauses and extracts their exact verbatim text snippets from the document.
    """
    system_instruction = (
        "You are the DocPilot Clause Intelligence Agent. Your primary objective is to scan the "
        "document text and extract critical clauses. Examples of clauses to find include:\n"
        "- Payment Terms\n"
        "- Limitation of Liability / Liability Cap\n"
        "- Termination / Early Termination Notice\n"
        "- Confidentiality obligations\n"
        "- Intellectual Property (IP) Ownership\n"
        "- Indemnification clauses\n"
        "- Auto-Renewal / Contract Extension terms\n"
        "- Force Majeure\n"
        "- Dispute Resolution & Jurisdiction\n"
        "- Non-compete / Non-solicit covenants\n\n"
        "CRITICAL REQUIREMENT:\n"
        "You MUST extract the 'verbatim_text' of each clause exactly as it appears in the document. "
        "Do NOT paraphrase, do NOT summarize, and do NOT correct typos. The exact text is required "
        "so the coordinate engine can locate the clause's exact coordinates in the original PDF file.\n"
        "Provide a confidence score (0.0 to 1.0) for each identified clause."
    )
    
    prompt = (
        f"--- DOCUMENT TEXT ---\n{context.document_text}\n\n"
        f"Find all major clauses and extract their exact verbatim text."
    )
    
    result = call_structured_gemini(
        client=client,
        prompt=prompt,
        response_schema=ClauseIntelligenceResult,
        system_instruction=system_instruction
    )
    return result
