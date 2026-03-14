import fitz  # PyMuPDF
import os
from app.core.config import settings


def extract_text_by_page(filepath: str) -> list[dict]:
    doc = fitz.open(filepath)
    pages = []
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text().strip()
        if text:
            pages.append({
                "page_num": page_num + 1,
                "text": text
            })
    doc.close()
    return pages


def chunk_text(pages: list[dict], chunk_size: int = 512, overlap: int = 50) -> list[dict]:
    chunks = []
    chunk_id = 0

    for page in pages:
        words = page["text"].split()
        start = 0

        while start < len(words):
            end = start + chunk_size
            chunk_words = words[start:end]
            chunk_text = " ".join(chunk_words)

            chunks.append({
                "chunk_id": chunk_id,
                "text": chunk_text,
                "page_num": page["page_num"],
                "word_count": len(chunk_words)
            })

            chunk_id += 1
            start += chunk_size - overlap

    return chunks


def process_pdf(filepath: str) -> list[dict]:
    pages = extract_text_by_page(filepath)
    chunks = chunk_text(pages)
    return chunks