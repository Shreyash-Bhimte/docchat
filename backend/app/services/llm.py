from groq import Groq
from app.core.config import settings

client = Groq(api_key=settings.groq_api_key)

SYSTEM_PROMPT = """You are a helpful assistant that answers questions based strictly on the provided document context.

Rules:
- Only answer based on the context provided below
- If the answer is not in the context, say "I couldn't find that in the document"
- Always mention which page the information came from
- Be concise and clear"""


def build_prompt(question: str, chunks: list[dict]) -> str:
    context = ""
    for i, chunk in enumerate(chunks):
        context += f"\n[Page {chunk['page_num']}]:\n{chunk['text']}\n"

    return f"""Context from document:
{context}

Question: {question}

Answer based only on the context above:"""


def get_answer(question: str, chunks: list[dict]) -> str:
    prompt = build_prompt(question, chunks)

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        temperature=0.1,
        max_tokens=1024
    )

    return response.choices[0].message.content


def stream_answer(question: str, chunks: list[dict]):
    prompt = build_prompt(question, chunks)

    stream = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        temperature=0.1,
        max_tokens=1024,
        stream=True
    )

    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta