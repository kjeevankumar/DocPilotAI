from google import genai
from backend.agents.context import AgentContext
from backend.models.schemas import EntityExtractionResult
from backend.services.gemini_service import call_structured_gemini

def run_entity_extraction_agent(client: genai.Client, context: AgentContext) -> EntityExtractionResult:
    """
    Extracts key structural metadata, values, and entities based on the document type.
    """
    doc_type = context.classification.document_type if context.classification else "Unknown"
    
    system_instruction = (
        "You are the DocPilot Entity Extraction Agent. Your role is to identify and extract key "
        "business entities, values, dates, and regulatory details from the document text.\n\n"
        f"This document is classified as: '{doc_type}'. Customize your extraction strategies accordingly.\n"
        "If a specific field (like invoice_number for an NDA, or renewal_date for a Receipt) is not "
        "present in the text, return null or empty values. Never guess or fabricate information.\n"
        "In your reasoning, outline where you found these items in the text."
    )
    
    prompt = (
        f"Document Classification: {doc_type}\n\n"
        f"--- DOCUMENT TEXT ---\n{context.document_text}\n\n"
        f"Extract all applicable entities from the text."
    )
    
    result = call_structured_gemini(
        client=client,
        prompt=prompt,
        response_schema=EntityExtractionResult,
        system_instruction=system_instruction
    )
    return result
