import os
import time
import re
from typing import Any, List
from google import genai
from google.genai import types
from backend.config import GEMINI_API_KEY
from backend.models.schemas import ChatResponse, ChatMessage

def get_gemini_client(api_key: str = "") -> genai.Client:
    """
    Retrieves the GenAI Client using either a dynamic API key provided in the
    headers or the local environment variable.
    """
    key = api_key or GEMINI_API_KEY or os.getenv("GEMINI_API_KEY", "")
    if not key:
        raise ValueError("Gemini API Key is missing. Please provide it in the settings panel.")
    # Format sanity check — Gemini keys always start with 'AIzaSy'
    if not key.startswith("AIzaSy"):
        print(f"[GEMINI_CLIENT] ⚠️  WARNING: API key does not start with 'AIzaSy'. "
              f"This key (starts with '{key[:8]}...') is likely invalid for Gemini. "
              f"Get a valid key at https://aistudio.google.com/app/apikey")
    return genai.Client(api_key=key)



def _extract_doc_text_from_prompt(prompt: str) -> str:
    """
    Extracts the raw document text section from a prompt string.
    Prompts use markers like '--- DOCUMENT TEXT ---' or '--- RAW DOCUMENT TEXT ---'.
    This ensures the fallback heuristics receive clean document text, not inflated
    prompt strings with agent headers, system instructions, etc.
    """
    # Try to find the document text block between known markers
    markers = [
        "--- DOCUMENT TEXT ---",
        "--- RAW DOCUMENT TEXT",
        "--- DOCUMENT EXCERPT",
        "DOCUMENT TEXT\n",
    ]
    for marker in markers:
        idx = prompt.find(marker)
        if idx != -1:
            # Start after the marker line
            start = prompt.find("\n", idx) + 1
            # End at the next section marker or end of string
            end_markers = ["\n---", "\n===", "\nAnalyze", "\nExtract", "\nClassify",
                           "\nFind", "\nRun", "\nGenerate", "\nSynthesize", "\nDetermine"]
            end = len(prompt)
            for em in end_markers:
                em_idx = prompt.find(em, start + 100)  # Skip at least 100 chars
                if em_idx != -1 and em_idx < end:
                    end = em_idx
            extracted = prompt[start:end].strip()
            if len(extracted) > 50:
                return extracted
    # Fallback: return the full prompt (better than nothing)
    return prompt


def call_structured_gemini(
    client: genai.Client,
    prompt: str,
    response_schema: Any,
    system_instruction: str = "",
    temperature: float = 0.1
) -> Any:
    """
    Executes a content generation request expecting a structured response.
    Validates and returns the parsed Pydantic schema model.
    Includes robust retries with exponential backoff for 429 Rate Limits.
    Falls back to a smart heuristic generation if the key is exhausted/rate-limited.

    NOTE: API_FAILED and IS_SAMPLE_RUN are intentionally LOCAL variables per call,
    not module-level globals. Using module globals caused every document after
    the first API failure to return identical static fallback data forever — 
    even after a valid API key was provided or the rate limit window expired.
    """
    from backend.services.fallback_service import generate_smart_fallback

    schema_name = getattr(response_schema, "__name__", str(response_schema))
    prompt_length = len(prompt)
    doc_text_present = "DOCUMENT TEXT" in prompt or "document_text" in prompt.lower()

    print(f"\n{'='*60}")
    print(f"[GEMINI] Calling Gemini API")
    print(f"[GEMINI] Schema: {schema_name}")
    print(f"[GEMINI] Prompt Length: {prompt_length} chars")
    print(f"[GEMINI] Document Text in Prompt: {doc_text_present}")
    print(f"[GEMINI] Model: gemini-2.5-flash")

    max_retries = 3
    base_delay = 1
    call_start = time.time()

    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=response_schema,
                    system_instruction=system_instruction,
                    temperature=temperature
                )
            )
            elapsed = round(time.time() - call_start, 2)
            response_length = len(response.text) if response.text else 0
            # Extract token counts if available from usage_metadata
            token_info = ""
            if hasattr(response, "usage_metadata") and response.usage_metadata:
                um = response.usage_metadata
                input_tokens = getattr(um, "prompt_token_count", "?")
                output_tokens = getattr(um, "candidates_token_count", "?")
                token_info = f" | Tokens in/out: {input_tokens}/{output_tokens}"
            print(f"[GEMINI] ✅ SUCCESS — Schema: {schema_name} | Prompt: {prompt_length} chars | Response: {response_length} chars{token_info} | Elapsed: {elapsed}s")
            print(f"{'='*60}\n")
            return response_schema.model_validate_json(response.text)

        except Exception as e:
            error_msg = str(e)
            elapsed = round(time.time() - call_start, 2)
            print(f"[GEMINI] ❌ ERROR (attempt {attempt + 1}/{max_retries}) after {elapsed}s: {error_msg[:200]}")

            # Categorize error
            is_permanent = False
            is_rate_limit = False

            if "403" in error_msg or "PERMISSION_DENIED" in error_msg:
                is_permanent = True
            elif "401" in error_msg or "UNAUTHORIZED" in error_msg or "API key not valid" in error_msg:
                is_permanent = True
            elif "400" in error_msg or "INVALID_ARGUMENT" in error_msg:
                is_permanent = True

            if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg or "rate limit" in error_msg.lower():
                is_rate_limit = True

            # Permanent errors or daily quota exhaustion — go to fallback immediately
            if is_permanent or (is_rate_limit and "quota exceeded" in error_msg.lower()):
                if is_permanent and ("403" in error_msg or "401" in error_msg or "API key not valid" in error_msg or "PERMISSION_DENIED" in error_msg):
                    print(f"[GEMINI] 🔑 CRITICAL: API Key appears invalid or unauthorized.")
                    print(f"[GEMINI] 🔑 Gemini API keys must start with 'AIzaSy...'. Check backend/.env or the settings panel.")
                print(f"[GEMINI] ⚠️  Permanent/quota error — activating per-request heuristic fallback.")
                print(f"{'='*60}\n")
                doc_text = _extract_doc_text_from_prompt(prompt)
                return generate_smart_fallback(response_schema, doc_text)

            # Rate limit (429) with a retry-after hint
            if is_rate_limit:
                if attempt < max_retries - 1:
                    match = re.search(r"retry in (\d+(?:\.\d+)?)s", error_msg)
                    if match:
                        sleep_time = float(match.group(1)) + 0.5
                    else:
                        sleep_time = base_delay * (2 ** attempt)

                    # If sleep time is too long, fall back immediately rather than blocking the request
                    if sleep_time > 15:
                        print(f"[GEMINI] ⚠️  Rate limit sleep too long ({sleep_time}s) — activating fallback.")
                        print(f"{'='*60}\n")
                        doc_text = _extract_doc_text_from_prompt(prompt)
                        return generate_smart_fallback(response_schema, doc_text)

                    print(f"[GEMINI] 🔄 Rate limit — sleeping {sleep_time:.1f}s before retry...")
                    time.sleep(sleep_time)
                    continue

            # Other transient errors — short sleep and retry
            if attempt < max_retries - 1:
                time.sleep(1.5)
                continue

            # All retries exhausted — use per-request heuristic fallback
            print(f"[GEMINI] ⚠️  All {max_retries} retries exhausted — activating per-request heuristic fallback.")
            print(f"{'='*60}\n")
            doc_text = _extract_doc_text_from_prompt(prompt)
            return generate_smart_fallback(response_schema, doc_text)


def call_chat_agent(
    client: genai.Client,
    document_text: str,
    history: List[ChatMessage],
    message: str,
    context_data_summary: str
) -> ChatResponse:
    """
    Specialized agent for answering questions about the analyzed document.
    Incorporates the document text, history, and the computed analysis context.
    """
    system_instruction = (
        "You are the DocPilot Conversational Chat Agent. Your role is to answer questions about the "
        "provided document context and the associated structured analysis findings.\n\n"
        "RULES:\n"
        "1. Answer queries truthfully based ONLY on the document and summary context.\n"
        "2. Do NOT hallucinate. If details are not present, explicitly state they are not in the document.\n"
        "3. Provide confidence score (0.0 to 1.0), internal reasoning, and verbatim evidence snippets.\n"
        "4. Keep answers clear, structured, and easy for business professionals to digest."
    )

    # Reconstruct chat log
    chat_history_prompt = ""
    for msg in history:
        chat_history_prompt += f"{msg.role.upper()}: {msg.content}\n"

    prompt = (
        f"--- DOCUMENT TEXT ---\n{document_text}\n\n"
        f"--- AGENT ANALYSIS SUMMARY ---\n{context_data_summary}\n\n"
        f"--- CONVERSATION HISTORY ---\n{chat_history_prompt}\n"
        f"USER: {message}\n"
        f"Respond using the ChatResponse schema."
    )

    return call_structured_gemini(
        client=client,
        prompt=prompt,
        response_schema=ChatResponse,
        system_instruction=system_instruction,
        temperature=0.2
    )
