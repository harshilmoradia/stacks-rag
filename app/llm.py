from anthropic import Anthropic

from app.config import settings

_client: Anthropic | None = None

SYSTEM_PROMPT = (
    "You answer questions using ONLY the provided context. "
    "If the context does not contain the answer, say so plainly instead of guessing. "
    "Cite which source each part of your answer comes from when possible."
)


def _get_client() -> Anthropic:
    global _client
    if _client is None:
        _client = Anthropic(api_key=settings.anthropic_api_key)
    return _client


def build_context_block(hits: list[dict]) -> str:
    blocks = []
    for i, hit in enumerate(hits, start=1):
        blocks.append(f"[Source {i}: {hit['source']}]\n{hit['text']}")
    return "\n\n".join(blocks)


def generate_answer(question: str, hits: list[dict]) -> str:
    if not hits:
        return "I don't have any indexed documents to answer from yet. Ingest a document first."

    context = build_context_block(hits)
    user_message = f"Context:\n{context}\n\nQuestion: {question}"

    client = _get_client()
    response = client.messages.create(
        model=settings.generation_model,
        max_tokens=1000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )
    return "".join(block.text for block in response.content if block.type == "text")