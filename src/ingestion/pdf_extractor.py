import fitz  # PyMuPDF
import re

def extract_text_from_pdf(pdf_path: str) -> dict:
    """
    Extract text and metadata from a PDF file.
    Returns: dict with keys: text, metadata, pages, extraction_warnings
    """
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        return {"text": "", "metadata": {}, "pages": [], "total_pages": 0, "extraction_warnings": [str(e)]}

    full_text = ""
    pages = []
    warnings = []
    
    for page_num, page in enumerate(doc):
        text = page.get_text("text")
        pages.append({
            "page_number": page_num + 1,
            "text": text,
            "char_count": len(text)
        })
        full_text += f"\n[PAGE {page_num + 1}]\n{text}"
        
    metadata = doc.metadata
    
    return {
        "text": full_text,
        "metadata": metadata,
        "pages": pages,
        "total_pages": len(doc),
        "extraction_warnings": warnings
    }

def clean_extracted_text(text: str) -> str:
    """Clean and normalize extracted PDF text."""
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    # Fix hyphenated words at line breaks
    text = re.sub(r'(\w+)-\s+(\w+)', r'\1\2', text)
    # Remove page numbers and headers (customize per document)
    text = re.sub(r'\n\d+\n', '\n', text)
    # Normalize quotes
    text = text.replace('"', '"').replace('"', '"')
    return text.strip()
