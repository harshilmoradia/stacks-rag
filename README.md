# Stacks RAG

A local retrieval-augmented generation (RAG) system. Upload documents through a Next.js UI or Claude Desktop, then ask questions and get answers grounded in your own content.

```
Next.js UI (port 3000)
       │  POST /ingest · POST /ask
       ▼
FastAPI backend (port 8000)
       │  OpenAI text-embedding-3-small
       ▼
Chroma vector store  ──►  Claude (claude-sonnet-4-6) ──► answer
```

The MCP server wraps the same pipeline so Claude Desktop can call `ingest_file` and `ask_documents` as native tools, no browser required.

---

## Repo layout

```
stacks-rag/
├── backend/          # FastAPI API + RAG pipeline + MCP server
│   ├── app/          # config, embeddings, vectorstore, llm, loaders, chunking
│   ├── eval/         # evaluation harness
│   ├── tests/
│   ├── mcp_server.py
│   ├── requirements.txt
│   └── .env.example
└── frontend/         # Next.js console UI
    ├── app/
    ├── components/   # AskPanel, IngestPanel, MatchMeter, StatusBadge
    └── lib/api.ts
```

---

## Prerequisites

| Tool | Version |
|---|---|
| Python | 3.11+ |
| Node.js | 18+ |
| OpenAI API key | — |
| Anthropic API key | — |
| Claude Desktop | for MCP only |

---

## 1. Backend

```bash
cd backend

# create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# install dependencies
pip install -r requirements.txt

# configure environment
cp .env.example .env
```

Open `backend/.env` and fill in your API keys, the server will not start without them:

```env
OPENAI_API_KEY=sk-...        # used for embeddings (text-embedding-3-small)
ANTHROPIC_API_KEY=sk-ant-... # used for generation (claude-sonnet-4-6)
```

```bash
# start the API
uvicorn app.main:app --reload
```

The API is now available at **http://localhost:8000/docs**.

| Endpoint | Method | Description |
|---|---|---|
| `/health` | GET | Liveness check |
| `/ingest` | POST | Upload a `.txt`, `.md`, or `.pdf` file |
| `/ask` | POST | Ask a question; returns answer + sources + latency |

---

## 2. Frontend

> The backend must be running before starting the frontend.

```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:3000** in your browser. Use the Ingest panel to upload documents and the Ask panel to query them.

---

## 3. MCP server (Claude Desktop)

The MCP server exposes two tools to Claude Desktop:

- **`ingest_file`** - index a local file into the knowledge base by absolute path
- **`ask_documents`** - ask a question and get a RAG-grounded answer

### Setup

1. Make sure the backend virtual environment is set up (step 1 above).

2. Add the following to `~/Library/Application Support/Claude/claude_desktop_config.json`, replacing the path and keys with your own:

```json
{
  "mcpServers": {
    "stacks-rag": {
      "command": "/absolute/path/to/stacks-rag/backend/.venv/bin/python",
      "args": ["-m", "mcp_server"],
      "cwd": "/absolute/path/to/stacks-rag/backend",
      "env": {
        "OPENAI_API_KEY": "sk-...",
        "ANTHROPIC_API_KEY": "sk-ant-..."
      }
    }
  }
}
```

> Tip: run `which python` inside your activated venv to get the exact python path.

3. Restart Claude Desktop.

4. You should see the `stacks-rag` tools listed in Claude's tool picker. Try:
   - *"Ingest this file: /Users/you/docs/notes.md"*
   - *"What does my knowledge base say about California road trips?"*

---

## 4. Docker (backend only)

```bash
cd backend
docker compose up --build
```

The API starts on port 8000 with Chroma data persisted in a named Docker volume.

---

## 5. Tests

```bash
cd backend
pytest
```
