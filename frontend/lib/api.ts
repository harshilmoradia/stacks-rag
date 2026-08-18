const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export interface AskResponse {
  answer: string;
  sources: { source: string; distance: number }[];
  latency_ms: number;
}

export interface IngestResponse {
  filename: string;
  chunks_indexed: number;
}

export class ApiError extends Error {}

export async function checkHealth(): Promise<boolean> {
  try {
    const res = await fetch(`${API_BASE_URL}/health`, { cache: "no-store" });
    return res.ok;
  } catch {
    return false;
  }
}

export async function ingestFile(file: File): Promise<IngestResponse> {
  const form = new FormData();
  form.append("file", file);

  const res = await fetch(`${API_BASE_URL}/ingest`, {
    method: "POST",
    body: form,
  });

  if (!res.ok) {
    const detail = await safeErrorDetail(res);
    throw new ApiError(detail || `Ingest failed (${res.status})`);
  }
  return res.json();
}

export async function askQuestion(question: string): Promise<AskResponse> {
  const res = await fetch(`${API_BASE_URL}/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });

  if (!res.ok) {
    const detail = await safeErrorDetail(res);
    throw new ApiError(detail || `Ask failed (${res.status})`);
  }
  return res.json();
}

async function safeErrorDetail(res: Response): Promise<string | null> {
  try {
    const body = await res.json();
    return body?.detail ?? null;
  } catch {
    return null;
  }
}
