import os
import shutil
import gc
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.document import Document
from app.services.ingest import process_pdf
from app.services.embeddings import embed_and_store
from app.core.config import settings

router = APIRouter(prefix="/upload", tags=["upload"])

MAX_FILE_SIZE_MB = 5
MAX_CHUNKS = 150


@router.post("/")
async def upload_pdf(file: UploadFile = File(...), db: Session = Depends(get_db)):

    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files allowed")

    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)

    if file_size > MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Max size is {MAX_FILE_SIZE_MB}MB"
        )

    os.makedirs(settings.upload_dir, exist_ok=True)
    filepath = os.path.join(settings.upload_dir, file.filename)

    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    chunks = process_pdf(filepath)

    if len(chunks) > MAX_CHUNKS:
        raise HTTPException(
            status_code=400,
            detail=f"PDF too large. Max allowed chunks = {MAX_CHUNKS}"
        )

    doc = Document(
        filename=file.filename,
        filepath=filepath,
        page_count=max(c["page_num"] for c in chunks) if chunks else 0
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    embed_and_store(doc.id, chunks)

    gc.collect()

    return {
        "doc_id": doc.id,
        "filename": doc.filename,
        "page_count": doc.page_count,
        "total_chunks": len(chunks),
        "message": "PDF uploaded and processed successfully"
    }