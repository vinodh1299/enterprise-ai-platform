import os
import csv
from typing import List, Dict, Any
from pypdf import PdfReader
import docx


def extract_text_from_file(file_path: str, filename: str) -> List[Dict[str, Any]]:
    """
    Extracts text content and page metadata from PDF, DOCX, TXT, or CSV files.
    Returns a list of page dicts: [{'page_number': 1, 'text': '...'}]
    """
    ext = os.path.splitext(filename)[1].lower()

    if ext == ".pdf":
        return _parse_pdf(file_path)
    elif ext == ".docx":
        return _parse_docx(file_path)
    elif ext == ".txt":
        return _parse_txt(file_path)
    elif ext == ".csv":
        return _parse_csv(file_path)
    else:
        raise ValueError(f"Unsupported file format: '{ext}'. Supported: PDF, DOCX, TXT, CSV.")


def _parse_pdf(file_path: str) -> List[Dict[str, Any]]:
    reader = PdfReader(file_path)
    pages = []
    for idx, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        text = text.strip()
        if text:
            pages.append({
                "page_number": idx + 1,
                "text": text
            })
    return pages


def _parse_docx(file_path: str) -> List[Dict[str, Any]]:
    doc = docx.Document(file_path)
    full_text = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
    return [{
        "page_number": 1,
        "text": full_text
    }]


def _parse_txt(file_path: str) -> List[Dict[str, Any]]:
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read().strip()
    return [{
        "page_number": 1,
        "text": text
    }]


def _parse_csv(file_path: str) -> List[Dict[str, Any]]:
    rows = []
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        reader = csv.reader(f)
        for row in reader:
            if row:
                rows.append(", ".join(row))
    return [{
        "page_number": 1,
        "text": "\n".join(rows)
    }]
