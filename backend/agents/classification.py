from google import genai
from backend.agents.context import AgentContext
from backend.models.schemas import DocumentClassificationResult
from backend.services.gemini_service import call_structured_gemini

def run_classification_agent(client: genai.Client, context: AgentContext) -> DocumentClassificationResult:
    """
    Classifies the document type and calculates classification confidence.
    """
    system_instruction = (
        "You are the DocPilot Document Classification Agent. Your task is to analyze the "
        "provided document text and determine its exact type (e.g., Contract, NDA, Invoice, "
        "Purchase Order, Receipt, Lease Agreement, Service Agreement, or Employment Agreement).\n\n"
        "Assign a confidence score (0.0 to 1.0) and explain your classification reasoning based on "
        "key visual structures, vocabulary, and clause syntax characteristic of that document type."
    )
    
    prompt = (
        f"Document Filename: {context.filename}\n\n"
        f"--- DOCUMENT TEXT ---\n{context.document_text}\n\n"
        f"Classify this document based on the text above."
    )
    
    result = call_structured_gemini(
        client=client,
        prompt=prompt,
        response_schema=DocumentClassificationResult,
        system_instruction=system_instruction
    )
    return result
