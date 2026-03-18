from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.database import Base, engine
from app.models import document  # noqa: F401
from app.routers import upload, chat, documents

Base.metadata.create_all(bind=engine)

app = FastAPI(title="DocChat API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://docchat-inky.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router)
app.include_router(chat.router)
app.include_router(documents.router)

@app.get("/")
def root():
    return {"status": "DocChat API is running"}

@app.get("/health")
def health():
    return {"status": "ok"}