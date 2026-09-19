"""
utils.py
Helper functions to read text out of uploaded contract files.
Supports PDF, DOCX and TXT formats.
"""

from pypdf import PdfReader
from docx import Document


def read_pdf(file) -> str:
    """Read all text from a PDF file. `file` is a file-like object (e.g. from Streamlit uploader)."""
    reader = PdfReader(file)
    text_parts = []
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text_parts.append(page_text)
    return "\n".join(text_parts)


def read_docx(file) -> str:
    """Read all text from a DOCX file. `file` is a file-like object."""
    document = Document(file)
    paragraphs = [p.text for p in document.paragraphs]
    return "\n".join(paragraphs)


def read_txt(file) -> str:
    """Read all text from a plain TXT file. `file` is a file-like object."""
    raw_bytes = file.read()
    if isinstance(raw_bytes, bytes):
        return raw_bytes.decode("utf-8", errors="ignore")
    return raw_bytes


def extract_text_from_file(file, filename: str) -> str:
    """
    Main entry point: given an uploaded file and its filename,
    detect the file type from the extension and return its text.
    """
    name_lower = filename.lower()
    if name_lower.endswith(".pdf"):
        return read_pdf(file)
    elif name_lower.endswith(".docx"):
        return read_docx(file)
    elif name_lower.endswith(".txt"):
        return read_txt(file)
    else:
        raise ValueError(f"Unsupported file type: {filename}")