import logging
import time

from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel

from app import embeddings, llm, vectorstore
from app.chunking import chunk_text
from app.config import settings
from app.loaders import load_document

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("rag")

app = FastAPI(title="Stacks RAG API", version="0.1.0")


class AskRequest(BaseModel):
    question: str


class AskResponse(BaseModel):
    answer: str
    sources: list[dict]
    latency_ms: int


class IngestResponse(BaseModel):
    filename: str
    chunks_indexed: int


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ingest", response_model=IngestResponse)
async def ingest(file: UploadFile = File(...)):
    raw = await file.read()
    try:
        text = load_document(file.filename, raw)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not text.strip():
        raise HTTPException(status_code=400, detail="No extractable text found in file.")

    chunks = chunk_text(
        text, source=file.filename, chunk_size=settings.chunk_size, chunk_overlap=settings.chunk_overlap
    )
    if not chunks:
        raise HTTPException(status_code=400, detail="Document produced zero chunks.")

    texts = [c.text for c in chunks]
    sources = [c.source for c in chunks]
    vectors = embeddings.embed_texts(texts)
    count = vectorstore.add_chunks(texts=texts, embeddings=vectors, sources=sources)

    logger.info("ingest file=%s chunks=%d", file.filename, count)
    return IngestResponse(filename=file.filename, chunks_indexed=count)


@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest):
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="question must not be empty")

    start = time.time()
    query_vector = embeddings.embed_query(req.question)
    hits = vectorstore.query(query_vector, top_k=settings.top_k)
    answer = llm.generate_answer(req.question, hits)
    latency_ms = int((time.time() - start) * 1000)

    logger.info("ask question=%r hits=%d latency_ms=%d", req.question, len(hits), latency_ms)

    return AskResponse(
        answer=answer,
        sources=[{"source": h["source"], "distance": h["distance"]} for h in hits],
        latency_ms=latency_ms,
    )