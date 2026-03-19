# import chromadb
# from sentence_transformers import SentenceTransformer

# _model = None
# _chroma_client = None

# def get_model():
#     global _model
#     if _model is None:
#         _model = SentenceTransformer('all-MiniLM-L6-v2')
#     return _model

# def get_chroma_client():
#     global _chroma_client
#     if _chroma_client is None:
#         _chroma_client = chromadb.PersistentClient(path="chroma_db")
#     return _chroma_client


# def get_or_create_collection(doc_id: int):
#     return get_chroma_client().get_or_create_collection(
#         name=f"doc_{doc_id}",
#         metadata={"hnsw:space": "cosine"}
#     )


# def embed_and_store(doc_id: int, chunks: list[dict]):
#     collection = get_or_create_collection(doc_id)
#     model = get_model()

#     texts = [chunk["text"] for chunk in chunks]
#     embeddings = model.encode(texts, batch_size=32, show_progress_bar=True)

#     collection.upsert(
#         ids=[f"chunk_{chunk['chunk_id']}" for chunk in chunks],
#         embeddings=embeddings.tolist(),
#         documents=texts,
#         metadatas=[{
#             "page_num": chunk["page_num"],
#             "chunk_id": chunk["chunk_id"],
#             "doc_id": doc_id
#         } for chunk in chunks]
#     )

#     print(f"\nStored {len(chunks)} chunks for doc_id={doc_id} in ChromaDB")
#     return len(chunks)


# def retrieve_chunks(doc_id: int, query: str, k: int = 5) -> list[dict]:
#     collection = get_or_create_collection(doc_id)
#     model = get_model()

#     query_embedding = model.encode([query])[0].tolist()

#     results = collection.query(
#         query_embeddings=[query_embedding],
#         n_results=min(k, collection.count()),
#         include=["documents", "metadatas", "distances"]
#     )

#     chunks = []
#     for i in range(len(results["documents"][0])):
#         chunks.append({
#             "text": results["documents"][0][i],
#             "page_num": results["metadatas"][0][i]["page_num"],
#             "chunk_id": results["metadatas"][0][i]["chunk_id"],
#             "similarity": round(1 - results["distances"][0][i], 4)
#         })

#     return chunks

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

_model = None
_chroma_client = None


# ✅ Lazy load model (good practice)
def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


# ✅ Persistent Chroma with reduced overhead
def get_chroma_client():
    global _chroma_client
    if _chroma_client is None:
        _chroma_client = chromadb.PersistentClient(
            path="chroma_db",
            settings=Settings(anonymized_telemetry=False)
        )
    return _chroma_client


def get_or_create_collection(doc_id: int):
    return get_chroma_client().get_or_create_collection(
        name=f"doc_{doc_id}",
        metadata={"hnsw:space": "cosine"}
    )


# 🔥 FIXED: memory-safe embedding
def embed_and_store(doc_id: int, chunks: list[dict]):
    collection = get_or_create_collection(doc_id)
    model = get_model()

    batch_size = 8   # 🔥 reduced batch size (IMPORTANT)

    total = 0

    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]

        texts = [c["text"] for c in batch]

        # ✅ encode only small batch (prevents RAM spike)
        embeddings = model.encode(
            texts,
            batch_size=8,
            show_progress_bar=False
        )

        collection.upsert(
            ids=[f"chunk_{c['chunk_id']}" for c in batch],
            embeddings=embeddings.tolist(),
            documents=texts,
            metadatas=[{
                "page_num": c["page_num"],
                "chunk_id": c["chunk_id"],
                "doc_id": doc_id
            } for c in batch]
        )

        total += len(batch)

        # ✅ optional: free memory early
        del embeddings
        del texts

    print(f"\nStored {total} chunks for doc_id={doc_id} in ChromaDB")
    return total


# 🔥 optimized retrieval
def retrieve_chunks(doc_id: int, query: str, k: int = 3):
    collection = get_or_create_collection(doc_id)
    model = get_model()

    query_embedding = model.encode([query])[0].tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(k, collection.count()),
        include=["documents", "metadatas", "distances"]
    )

    chunks = []

    for i in range(len(results["documents"][0])):
        chunks.append({
            "text": results["documents"][0][i],
            "page_num": results["metadatas"][0][i]["page_num"],
            "chunk_id": results["metadatas"][0][i]["chunk_id"],
            "similarity": round(1 - results["distances"][0][i], 4)
        })

    return chunks