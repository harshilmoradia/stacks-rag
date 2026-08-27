import pathlib

from mcp.server import MCPServer

from app import embeddings, llm, vectorstore
from app.chunking import chunk_document
from app.config import settings
from app.loaders import load_document

mcp = MCPServer("stacks-rag")


@mcp.tool()
def ask_documents(question: str) -> str:
    """Answer a question using retrieval-augmented generation over previously ingested documents."""
    query_vector = embeddings.embed_query(question)
    hits = vectorstore.query(query_vector, top_k=settings.top_k)
    answer = llm.generate_answer(question, hits)
    if hits:
        sources = ", ".join(sorted({h["source"] for h in hits}))
        return f"{answer}\n\n(Sources: {sources})"
    return answer


@mcp.tool()
def ingest_file(file_path: str) -> str:
    """Ingest a local document (.txt, .md, or .pdf) into the knowledge base, given its absolute file path."""
    path = pathlib.Path(file_path).expanduser()
    if not path.exists():
        return f"File not found: {file_path}"

    raw = path.read_bytes()
    text = load_document(path.name, raw)
    chunks = chunk_document(
        text, filename=path.name, chunk_size=settings.chunk_size, chunk_overlap=settings.chunk_overlap
    )
    if not chunks:
        return "Document produced no chunks."

    texts = [c.text for c in chunks]
    sources = [c.source for c in chunks]
    vectors = embeddings.embed_texts(texts)
    count = vectorstore.add_chunks(texts=texts, embeddings=vectors, sources=sources)
    return f"Ingested {path.name}: {count} chunks indexed."


if __name__ == "__main__":
    mcp.run()