import os
import shutil
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.document import Document
from app.services.ingest import process_pdf
from app.core.config import settings

router = APIRouter(prefix="/upload", tags=["upload"])


@router.post("/")
async def upload_pdf(file: UploadFile = File(...), db: Session = Depends(get_db)):

    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files allowed")

    os.makedirs(settings.upload_dir, exist_ok=True)
    filepath = os.path.join(settings.upload_dir, file.filename)

    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    chunks = process_pdf(filepath)

    for i, chunk in enumerate(chunks[:3]):
        print(f"\n--- Chunk {i+1} (page {chunk['page_num']}) ---")
        print(chunk["text"][:200])

    doc = Document(
        filename=file.filename,
        filepath=filepath,
        page_count=max(c["page_num"] for c in chunks) if chunks else 0
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    return {
        "doc_id": doc.id,
        "filename": doc.filename,
        "page_count": doc.page_count,
        "total_chunks": len(chunks),
        "message": "PDF uploaded and processed successfully"
    }