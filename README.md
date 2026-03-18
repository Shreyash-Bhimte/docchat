# DocChat 📄

A RAG-based PDF chatbot that lets you upload any PDF and ask questions about it. Get AI-powered answers with page citations, streamed in real time.

**Live Demo:** https://docchat-inky.vercel.app

**API Docs:** https://docchat-api-vore.onrender.com/docs
---

## How it works
```
PDF uploaded
  → PyMuPDF extracts text page by page
    → Chunker splits into 512-word overlapping pieces
      → sentence-transformers converts chunks to vectors
        → ChromaDB stores vectors on disk
          → User asks question
            → Query converted to vector
              → ChromaDB finds top-5 most similar chunks
                → Chunks injected into Groq LLM prompt
                  → Answer streamed back token by token
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend API | FastAPI (Python) |
| Database | PostgreSQL + SQLAlchemy |
| Vector Store | ChromaDB |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) |
| LLM | Groq (llama-3.3-70b-versatile) |
| PDF Processing | PyMuPDF |
| Frontend | React + Vite |
| Containerization | Docker |
| Deployment | Render (backend) + Vercel (frontend) |

---

## Features

- Upload any PDF and chat with it instantly
- Semantic search — finds relevant content even without exact keyword matches
- Streamed AI responses token by token
- Page citations — every answer references the source page
- Conversation memory — understands follow-up questions
- Multi-document support — switch between uploaded PDFs
- Delete documents from the sidebar
- 7 passing pytest tests

---

## Local Setup

### Prerequisites
- Python 3.11+
- Node 18+
- Docker Desktop
- Conda

### 1. Clone the repo
```bash
git clone https://github.com/Shreyash-Bhimte/docchat
cd docchat
```

### 2. Backend setup
```bash
cd backend
conda create -n docchat python=3.11
conda activate docchat
pip install -r requirements.txt
```

### 3. Create .env file
```bash
# backend/.env
GROQ_API_KEY=your_groq_api_key
GEMINI_API_KEY=your_gemini_api_key
DATABASE_URL=postgresql://postgres:password@localhost:5432/docchat
UPLOAD_DIR=uploads
```

### 4. Start PostgreSQL
```bash
docker run --name docchat-db \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=docchat \
  -p 5432:5432 \
  -d postgres
```

### 5. Start backend
```bash
cd backend
conda activate docchat
uvicorn app.main:app --reload --port 8000
```

### 6. Start frontend
```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

---

## API Documentation

Interactive API docs available at:
- Local: http://localhost:8000/docs
- Live: https://docchat-api-vore.onrender.com/docs

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/upload/` | Upload and process PDF |
| POST | `/chat/` | Ask a question, get streamed answer |
| GET | `/chat/history/{doc_id}` | Get conversation history |
| GET | `/documents/` | List all documents |
| DELETE | `/documents/{doc_id}` | Delete a document |

---

## Running Tests
```bash
cd backend
python -m pytest tests/test_api.py -v
```

Expected output: 7 passed

---

## Environment Variables

See `backend/.env.example` for all required variables:

| Variable | Description |
|----------|-------------|
| `GROQ_API_KEY` | Groq API key from console.groq.com |
| `GEMINI_API_KEY` | Google Gemini API key (optional) |
| `DATABASE_URL` | PostgreSQL connection string |
| `UPLOAD_DIR` | Directory for uploaded PDFs |

---

## Project Structure
```
docchat/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── core/config.py
│   │   ├── db/database.py
│   │   ├── models/document.py
│   │   ├── routers/
│   │   │   ├── upload.py
│   │   │   ├── chat.py
│   │   │   └── documents.py
│   │   └── services/
│   │       ├── ingest.py
│   │       ├── embeddings.py
│   │       └── llm.py
│   ├── tests/test_api.py
│   ├── Dockerfile
│   └── requirements.txt
└── frontend/
    └── src/
        ├── App.jsx
        └── index.css
```

---

## Known Limitations

- Render free tier has ~60s cold start after inactivity
- Uploaded files are ephemeral on Render free tier (deleted on restart)
- Use local setup for persistent storage

---

## Author

Shreyash Bhimte