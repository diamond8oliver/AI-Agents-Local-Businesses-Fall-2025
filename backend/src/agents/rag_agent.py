from typing import List, Dict
from openai import OpenAI

from src.agents.knowledge_base import get_chroma_client, get_collection, query_similar


SYSTEM_PROMPT = (
    "You are a helpful assistant for a local business. "
    "Use only the provided CONTEXT to answer. If the answer is not found in the context, say you don't know."
)


def answer_question(question: str, k: int = 5, model: str = "gpt-4o-mini") -> Dict:
    client = OpenAI()
    collection = get_collection(get_chroma_client(".chroma"), "business_kb")
    hits = query_similar(collection, question, k=k)
    context_blocks: List[str] = []
    for h in hits:
        src = h.get("metadata", {}).get("source_url", "")
        snippet = h.get("document", "")[:1200]
        context_blocks.append(f"Source: {src}\n{snippet}")
    context = "\n\n".join(context_blocks) or "No context."

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"CONTEXT:\n{context}\n\nQUESTION: {question}"},
    ]

    chat = client.chat.completions.create(model=model, messages=messages, temperature=0.2)
    answer = chat.choices[0].message.content
    return {"answer": answer, "sources": [h.get("metadata", {}).get("source_url", "") for h in hits]}


