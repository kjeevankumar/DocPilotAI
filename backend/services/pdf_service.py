import fitz  # PyMuPDF
import re
from pathlib import Path
from typing import List, Dict, Any, Tuple
from backend.config import UPLOAD_DIR
from backend.models.schemas import Coordinate

def get_pdf_info(pdf_path: str) -> List[Dict[str, float]]:
    """
    Get dimensions of each page in the PDF.
    """
    pages_info = []
    try:
        doc = fitz.open(pdf_path)
        for idx, page in enumerate(doc):
            pages_info.append({
                "page": idx,
                "width": page.rect.width,
                "height": page.rect.height
            })
        doc.close()
    except Exception as e:
        print(f"Error reading PDF dimensions: {e}")
    return pages_info

def render_pdf_pages(pdf_path: str, doc_id: str) -> int:
    """
    Renders PDF pages as PNG images.
    Returns the total number of pages rendered.
    """
    pages_count = 0
    try:
        doc = fitz.open(pdf_path)
        pages_count = len(doc)
        for page_num in range(pages_count):
            page = doc[page_num]
            # 150 DPI is a great balance between text readability and load speed (default is 72 dpi)
            pix = page.get_pixmap(dpi=150)
            img_path = UPLOAD_DIR / f"{doc_id}_page_{page_num}.png"
            pix.save(str(img_path))
        doc.close()
    except Exception as e:
        print(f"Error rendering PDF pages as PNG: {e}")
        raise e
    return pages_count

def search_text_coordinates(pdf_path: str, text_snippet: str) -> List[Coordinate]:
    """
    Searches for a text snippet in a PDF and returns coordinates for highlighting.
    Includes fallbacks for line breaks, normalization, and substring matching.
    """
    if not text_snippet or len(text_snippet.strip()) < 4:
        return []

    coordinates = []
    cleaned_snippet = re.sub(r'\s+', ' ', text_snippet.strip())
    
    try:
        doc = fitz.open(pdf_path)
        for page_num in range(len(doc)):
            page = doc[page_num]
            w = page.rect.width
            h = page.rect.height
            
            # Fallback 1: Try exact matching on page
            rects = page.search_for(text_snippet)
            if rects:
                for r in rects:
                    coordinates.append(Coordinate(page=page_num, box=[r.x0, r.y0, r.x1, r.y1], page_width=w, page_height=h))
                continue
                
            # Fallback 2: Try matching cleaned snippet (whitespace normalized)
            rects = page.search_for(cleaned_snippet)
            if rects:
                for r in rects:
                    coordinates.append(Coordinate(page=page_num, box=[r.x0, r.y0, r.x1, r.y1], page_width=w, page_height=h))
                continue

            # Fallback 3: If long snippet, search for first 30 characters
            if len(cleaned_snippet) > 40:
                prefix = cleaned_snippet[:30]
                rects = page.search_for(prefix)
                if rects:
                    for r in rects:
                        coordinates.append(Coordinate(page=page_num, box=[r.x0, r.y0, r.x1, r.y1], page_width=w, page_height=h))
                    continue
                
                # Try last 30 characters
                suffix = cleaned_snippet[-30:]
                rects = page.search_for(suffix)
                if rects:
                    for r in rects:
                        coordinates.append(Coordinate(page=page_num, box=[r.x0, r.y0, r.x1, r.y1], page_width=w, page_height=h))
                    continue
        
        doc.close()
    except Exception as e:
        print(f"Error searching text coordinates: {e}")
        
    return coordinates
