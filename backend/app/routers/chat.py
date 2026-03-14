import json
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.db.database import get_db
from app.models.document import Document, ChatHistory
from app.services.embeddings import retrieve_chunks
from app.services.llm import stream_answer

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    doc_id: int
    question: str


@router.post("/")
async def chat(request: ChatRequest, db: Session = Depends(get_db)):

    doc = db.query(Document).filter(Document.id == request.doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    chunks = retrieve_chunks(
        doc_id=request.doc_id,
        query=request.question,
        k=5
    )

    if not chunks:
        raise HTTPException(status_code=404, detail="No relevant chunks found")

    full_answer = []
    citations = [{"page_num": c["page_num"], "similarity": c["similarity"]} for c in chunks]

    def generate():
        for token in stream_answer(request.question, chunks):
            full_answer.append(token)
            yield token

        answer_text = "".join(full_answer)
        history = ChatHistory(
            doc_id=request.doc_id,
            question=request.question,
            answer=answer_text,
            citations=json.dumps(citations)
        )
        db.add(history)
        db.commit()

    return StreamingResponse(generate(), media_type="text/plain")


@router.get("/history/{doc_id}")
def get_history(doc_id: int, db: Session = Depends(get_db)):
    history = db.query(ChatHistory).filter(
        ChatHistory.doc_id == doc_id
    ).order_by(ChatHistory.created_at.desc()).all()

    return [
        {
            "id": h.id,
            "question": h.question,
            "answer": h.answer,
            "citations": json.loads(h.citations) if h.citations else [],
            "created_at": str(h.created_at)
        }
        for h in history
    ]