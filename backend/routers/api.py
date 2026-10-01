import os
import uuid
import csv
import io
import traceback
import fitz  # PyMuPDF
from fastapi import APIRouter, UploadFile, File, Header, HTTPException, Query
from fastapi.responses import StreamingResponse, FileResponse, JSONResponse
from typing import Optional, Tuple
from google.genai import types

from backend.config import UPLOAD_DIR, MAX_UPLOAD_SIZE, SUPPORTED_FORMATS
from backend.models.schemas import (
    ChatRequest,
    ChatResponse,
    DocumentAnalysisResponse,
    TeachMemoryRequest,
    HindsightStatusResponse,
    MemoryItem
)
from backend.services.pdf_service import render_pdf_pages, get_pdf_info, search_text_coordinates
from backend.services.gemini_service import get_gemini_client, call_chat_agent
from backend.services.hindsight_service import hindsight_service
from backend.agents.orchestrator import run_orchestrator

router = APIRouter()

def extract_document_text(file_path: str, ext: str, api_key: str = "") -> Tuple[str, int]:
    """
    Extracts text from PDF (using PyMuPDF) or images (using Gemini Vision).
    Returns a tuple of (extracted_text, page_count).
    """
    if ext == ".pdf":
        doc = fitz.open(file_path)
        text = ""
        for page in doc:
            text += page.get_text()
        page_count = len(doc)
        doc.close()
        return text, page_count
    else:
        # It's an image. Let's run a Gemini Vision transcription.
        try:
            client = get_gemini_client(api_key)
            if client is None:
                # Return fallback text for image analysis without API key
                return f"[Image Document: {os.path.basename(file_path)}]\nContains agreement layout and visual contract provisions.", 1

            with open(file_path, "rb") as f:
                image_bytes = f.read()
            
            mime_type = "image/png" if ext == ".png" else "image/jpeg"
            
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=[
                    types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                    "Transcribe all text from this image exactly. Do not summarize, explain, or edit the content."
                ]
            )
            return response.text or f"[Image Document: {os.path.basename(file_path)}]", 1
        except Exception as e:
            print(f"Error during Gemini Image transcription: {e}")
            return f"[Image Document: {os.path.basename(file_path)}]\nVisual agreement structure.", 1

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    x_gemini_key: Optional[str] = Header(None)
):
    """
    Receives document files, validates contents, performs page extraction (or image copy),
    and extracts text context.
    """
    filename = file.filename
    ext = os.path.splitext(filename)[1].lower()
    
    # 1. Validation
    if ext not in SUPPORTED_FORMATS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported format {ext}. Allowed: PDF, PNG, JPG, JPEG."
        )
    
    # Read check for size
    contents = await file.read()
    if len(contents) > MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=400,
            detail="File size exceeds maximum limit of 15MB."
        )
    
    # Reset stream pointer
    await file.seek(0)
    
    # Save Upload
    doc_id = uuid.uuid4().hex
    saved_file_name = f"{doc_id}{ext}"
    saved_file_path = str(UPLOAD_DIR / saved_file_name)

    with open(saved_file_path, "wb") as f:
        f.write(contents)

    # ── DEBUG: Upload receipt ─────────────────────────────────────────────
    print(f"\n{'='*60}")
    print(f"[UPLOAD] ✅ File received and saved")
    print(f"[UPLOAD] Original Filename : {filename}")
    print(f"[UPLOAD] Saved Path        : {saved_file_path}")
    print(f"[UPLOAD] File Size         : {len(contents):,} bytes ({len(contents)/1024:.1f} KB)")
    print(f"[UPLOAD] Document ID       : {doc_id}")
    # ─────────────────────────────────────────────────────────────────────

    try:
        # 2. Extract text and render page images
        if ext == ".pdf":
            # Extract text & page count
            document_text, pages_count = extract_document_text(saved_file_path, ext, x_gemini_key or "")
            # Render page images to serve to frontend
            render_pdf_pages(saved_file_path, doc_id)
        else:
            # It's an image
            document_text, pages_count = extract_document_text(saved_file_path, ext, x_gemini_key or "")
            # Just copy the original upload as page 0 PNG
            img_dest = str(UPLOAD_DIR / f"{doc_id}_page_0.png")
            with open(img_dest, "wb") as f:
                f.write(contents)

        # ── DEBUG: Extraction result ──────────────────────────────────────
        print(f"[UPLOAD] Extraction complete")
        print(f"[UPLOAD] Pages             : {pages_count}")
        print(f"[UPLOAD] Text Length       : {len(document_text):,} chars")
        print(f"[UPLOAD] Extraction empty? : {len(document_text.strip()) == 0}")
        print(f"[UPLOAD] First 500 chars   :")
        print(document_text[:500])
        print(f"{'='*60}\n")
        # ─────────────────────────────────────────────────────────────────

        # Save raw document text to a companion txt file for the orchestrator to read
        text_file_path = str(UPLOAD_DIR / f"{doc_id}.txt")
        with open(text_file_path, "w", encoding="utf-8") as f:
            f.write(document_text)

        return {
            "document_id": doc_id,
            "filename": filename,
            "pages_count": pages_count,
            "status": "uploaded"
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions directly — don’t wrap them
        if os.path.exists(saved_file_path):
            os.remove(saved_file_path)
        raise
    except Exception as e:
        # ── FULL TRACEBACK LOG so Railway logs show the real error ───────
        tb = traceback.format_exc()
        print(f"[UPLOAD] ❌ EXCEPTION during file processing:")
        print(tb)
        # ─────────────────────────────────────────────────────────
        # Clean up files on error
        if os.path.exists(saved_file_path):
            os.remove(saved_file_path)
        raise HTTPException(status_code=500, detail=f"File processing error: {str(e)}")

@router.get("/analyze")
async def analyze_document(
    doc_id: str = Query(...),
    filename: str = Query(...),
    api_key: Optional[str] = Query(None)
):
    """
    Server-Sent Events endpoint that streams step-by-step progress reports from
    the autonomous agents as they evaluate the document.
    """
    # Locate files
    pdf_ext_options = [".pdf", ".png", ".jpg", ".jpeg"]
    pdf_path = None
    ext = None
    for opt in pdf_ext_options:
        test_path = UPLOAD_DIR / f"{doc_id}{opt}"
        if test_path.exists():
            pdf_path = str(test_path)
            ext = opt
            break
            
    if not pdf_path:
        raise HTTPException(status_code=404, detail="Uploaded document file not found.")
        
    text_path = UPLOAD_DIR / f"{doc_id}.txt"
    if not text_path.exists():
        raise HTTPException(status_code=404, detail="Document text context not found.")
        
    with open(text_path, "r", encoding="utf-8") as f:
        document_text = f.read()

    # Compute page count
    if ext == ".pdf":
        doc = fitz.open(pdf_path)
        pages_count = len(doc)
        doc.close()
    else:
        pages_count = 1

    # ── DEBUG: Analyze endpoint received text ─────────────────────────────
    print(f"\n{'='*60}")
    print(f"[ANALYZE] Starting analysis for doc_id: {doc_id}")
    print(f"[ANALYZE] Filename   : {filename}")
    print(f"[ANALYZE] PDF Path   : {pdf_path}")
    print(f"[ANALYZE] Pages      : {pages_count}")
    print(f"[ANALYZE] Text Length: {len(document_text):,} chars")
    print(f"[ANALYZE] Text empty?: {len(document_text.strip()) == 0}")
    print(f"{'='*60}\n")
    # ─────────────────────────────────────────────────────────────────────

    # Stream response
    return StreamingResponse(
        run_orchestrator(
            api_key=api_key or "",
            doc_id=doc_id,
            filename=filename,
            pdf_path=pdf_path,
            document_text=document_text,
            pages_count=pages_count
        ),
        media_type="text/event-stream"
    )

@router.post("/chat", response_model=ChatResponse)
async def chat_with_document(
    req: ChatRequest,
    x_gemini_key: Optional[str] = Header(None)
):
    """
    Context-aware Conversational Chat Agent. Reads the stored analysis context file
    and allows user to query document details.
    """
    doc_id = req.document_id
    
    # Load analysis context JSON
    pdf_ext_options = [".pdf", ".png", ".jpg", ".jpeg"]
    base_file = None
    for opt in pdf_ext_options:
        test_path = UPLOAD_DIR / f"{doc_id}{opt}"
        if test_path.exists():
            base_file = str(test_path)
            break
            
    if not base_file:
        raise HTTPException(status_code=404, detail="Document file not found.")
        
    analysis_file = base_file + ".analysis.json"
    if not os.path.exists(analysis_file):
        raise HTTPException(status_code=404, detail="Document has not been analyzed yet. Run analysis first.")
        
    with open(analysis_file, "r", encoding="utf-8") as f:
        analysis_json = f.read()
        
    text_path = UPLOAD_DIR / f"{doc_id}.txt"
    with open(text_path, "r", encoding="utf-8") as f:
        document_text = f.read()
        
    # Call chat service with recalled Hindsight memory
    try:
        # Recall memories relevant to the user's question
        recalled = hindsight_service.recall(req.message, top_k=3)
        hindsight_str = ""
        if recalled:
            hindsight_str = "\n".join([f"- [{m.get('category')}]: {m.get('content')}" for m in recalled])

        client = get_gemini_client(x_gemini_key or "")
        response = call_chat_agent(
            client=client,
            document_text=document_text,
            history=req.history,
            message=req.message,
            context_data_summary=analysis_json,
            hindsight_memories=hindsight_str
        )
        
        # Enforce coordinate highlight lookups for answer evidence
        if response.evidence:
            coords = []
            for ev in response.evidence:
                matches = search_text_coordinates(base_file, ev)
                if matches:
                    coords.extend(matches)
            response.coordinates = coords
            
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conversational Chat error: {str(e)}")

@router.get("/document/{doc_id}/page/{page_num}")
async def get_document_page(doc_id: str, page_num: int):
    """
    Returns the pre-rendered PNG page of the uploaded PDF or image.
    """
    page_img_path = UPLOAD_DIR / f"{doc_id}_page_{page_num}.png"
    if not page_img_path.exists():
        raise HTTPException(status_code=404, detail=f"Page image {page_num} not found.")
    return FileResponse(str(page_img_path), media_type="image/png")

@router.get("/download/{doc_id}/report")
async def download_report(
    doc_id: str,
    format: str = Query("json")
):
    """
    Exports the document intelligence findings in JSON or CSV format.
    """
    pdf_ext_options = [".pdf", ".png", ".jpg", ".jpeg"]
    base_file = None
    for opt in pdf_ext_options:
        test_path = UPLOAD_DIR / f"{doc_id}{opt}"
        if test_path.exists():
            base_file = str(test_path)
            break
            
    if not base_file:
        raise HTTPException(status_code=404, detail="Document file not found.")
        
    analysis_file = base_file + ".analysis.json"
    if not os.path.exists(analysis_file):
        raise HTTPException(status_code=404, detail="No analysis reports exist for this document.")
        
    with open(analysis_file, "r", encoding="utf-8") as f:
        raw_json_str = f.read()
        
    if format == "json":
        # Stream raw JSON
        return StreamingResponse(
            io.BytesIO(raw_json_str.encode("utf-8")),
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename=docpilot_report_{doc_id}.json"}
        )
        
    elif format == "csv":
        # Parse JSON to export risk register as CSV
        try:
            import json
            data = json.loads(raw_json_str)
            risk_flags = data.get("risk_flags", [])
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Header
            writer.writerow(["Risk Category", "Clause Title", "Severity", "Trigger Text", "Reasoning", "Suggested Mitigation"])
            
            for risk in risk_flags:
                writer.writerow([
                    risk.get("category", "N/A"),
                    risk.get("clause_name", "N/A"),
                    risk.get("severity", "N/A"),
                    risk.get("text", "N/A"),
                    risk.get("reasoning", "N/A"),
                    risk.get("suggested_action", "N/A")
                ])
                
            output.seek(0)
            return StreamingResponse(
                io.BytesIO(output.getvalue().encode("utf-8")),
                media_type="text/csv",
                headers={"Content-Disposition": f"attachment; filename=docpilot_risks_{doc_id}.csv"}
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to generate CSV export: {str(e)}")
            
    elif format == "pdf":
        try:
            import json
            from backend.services.report_service import generate_pdf_report
            data = json.loads(raw_json_str)
            pdf_bytes = generate_pdf_report(data)
            return StreamingResponse(
                io.BytesIO(pdf_bytes),
                media_type="application/pdf",
                headers={"Content-Disposition": f"attachment; filename=docpilot_report_{doc_id}.pdf"}
            )
        except Exception as e:
            import traceback
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=f"Failed to generate PDF export: {str(e)}")
            
    else:
        raise HTTPException(status_code=400, detail="Invalid format. Supported formats: json, csv, pdf")

# ── HINDSIGHT PERSISTENT MEMORY ENDPOINTS ─────────────────────────────────────

@router.get("/memory/status", response_model=HindsightStatusResponse)
async def get_memory_status():
    """Returns the connection and storage status of Hindsight Persistent Memory."""
    return hindsight_service.get_status()

@router.get("/memory/bank")
async def list_memory_bank(query: Optional[str] = Query(None)):
    """Lists all memories stored in the Hindsight Memory Bank with optional search filtering."""
    return hindsight_service.list_memories(search=query)

@router.post("/memory/recall")
async def recall_memories(query: str = Query(...)):
    """Recalls precedents and policies for a specific query from Hindsight."""
    results = hindsight_service.recall(query=query, top_k=5)
    return {"query": query, "results": results}

@router.post("/memory/retain")
async def retain_memory_rule(req: TeachMemoryRequest):
    """Teaches a new precedent, approved exception, or corporate policy to Hindsight."""
    retained = hindsight_service.retain(
        content=req.content,
        category=req.category,
        tags=req.tags,
        source_doc=req.source_doc,
        bank_id=req.bank_id
    )
    return {"status": "success", "memory": retained}

@router.post("/memory/reset")
async def reset_memory_bank():
    """Resets the memory bank to the official hackathon seed state."""
    memories = hindsight_service.reset_bank()
    return {"status": "success", "total_memories": len(memories)}
