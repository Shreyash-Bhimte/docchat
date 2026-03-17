from groq import Groq
from app.core.config import settings

client = Groq(api_key=settings.groq_api_key)

SYSTEM_PROMPT = """You are a helpful assistant that answers questions based strictly on the provided document context.

Rules:
- Only answer based on the context provided below
- If the answer is not in the context, say "I couldn't find that in the document"
- Always mention which page the information came from
- Be concise and clear"""


def build_prompt(question: str, chunks: list[dict], history: list[dict] = []) -> list[dict]:
    context = ""
    for chunk in chunks:
        context += f"\n[Page {chunk['page_num']}]:\n{chunk['text']}\n"

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    messages.append({
        "role": "user",
        "content": f"Document context:\n{context}"
    })
    messages.append({
        "role": "assistant",
        "content": "I have read the document context. I will answer based only on this content."
    })

    for exchange in history[-3:]:
        messages.append({"role": "user", "content": exchange["question"]})
        messages.append({"role": "assistant", "content": exchange["answer"]})

    messages.append({"role": "user", "content": question})

    return messages


def stream_answer(question: str, chunks: list[dict], history: list[dict] = []):
    messages = build_prompt(question, chunks, history)

    stream = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        temperature=0.1,
        max_tokens=1024,
        stream=True
    )

    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta