import logging
import pathlib
import time
from collections import defaultdict
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app import embeddings, llm, vectorstore
from app.chunking import chunk_document
from app.config import settings
from app.loaders import load_document

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("rag")

@asynccontextmanager
async def lifespan(app: FastAPI):
    load_sample_corpus_if_empty()
    yield


app = FastAPI(title="Stacks RAG API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

SAMPLE_DOCS_DIR = pathlib.Path(__file__).parent.parent / "data" / "sample_docs"

# Simple in-memory per-IP daily limiter. Resets on restart, which is fine
# for a free-tier demo that already restarts on every cold start.
RATE_LIMIT_PER_DAY = 20
_request_log: dict[str, list[float]] = defaultdict(list)


def _check_rate_limit(ip: str) -> None:
    now = time.time()
    window_start = now - 86400
    _request_log[ip] = [t for t in _request_log[ip] if t > window_start]
    if len(_request_log[ip]) >= RATE_LIMIT_PER_DAY:
        raise HTTPException(status_code=429, detail="Daily demo limit reached. Try again tomorrow.")
    _request_log[ip].append(now)


def _ingest_bytes(filename: str, raw: bytes) -> int:
    text = load_document(filename, raw)
    if not text.strip():
        return 0
    chunks = chunk_document(
        text, filename=filename, chunk_size=settings.chunk_size, chunk_overlap=settings.chunk_overlap
    )
    if not chunks:
        return 0
    texts = [c.text for c in chunks]
    sources = [c.source for c in chunks]
    vectors = embeddings.embed_texts(texts)
    return vectorstore.add_chunks(texts=texts, embeddings=vectors, sources=sources)


def load_sample_corpus_if_empty():
    collection = vectorstore.get_collection()
    if collection.count() > 0:
        logger.info("startup: vectorstore already has %d chunks, skipping ingestion", collection.count())
        return

    if not SAMPLE_DOCS_DIR.exists():
        logger.warning("startup: sample docs dir not found at %s", SAMPLE_DOCS_DIR)
        return

    total = 0
    for path in sorted(SAMPLE_DOCS_DIR.glob("*.md")):
        raw = path.read_bytes()
        count = _ingest_bytes(path.name, raw)
        total += count
        logger.info("startup: ingested %s (%d chunks)", path.name, count)

    logger.info("startup: ingestion complete, %d total chunks indexed", total)

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

    chunks = chunk_document(
        text, filename=file.filename, chunk_size=settings.chunk_size, chunk_overlap=settings.chunk_overlap
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
def ask(req: AskRequest, request: Request):
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="question must not be empty")

    client_ip = request.client.host if request.client else "unknown"
    _check_rate_limit(client_ip)

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