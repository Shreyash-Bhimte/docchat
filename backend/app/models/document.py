from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from app.db.database import Base

class Document(Base):
    __tablename__ = "documents"

    id         = Column(Integer, primary_key=True, index=True)
    filename   = Column(String, nullable=False)
    filepath   = Column(String, nullable=False)
    page_count = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ChatHistory(Base):
    __tablename__ = "chat_history"

    id         = Column(Integer, primary_key=True, index=True)
    doc_id     = Column(Integer, nullable=False)
    question   = Column(Text, nullable=False)
    answer     = Column(Text, nullable=False)
    citations  = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())