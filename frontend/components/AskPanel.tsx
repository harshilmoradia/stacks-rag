"use client";

import { useState } from "react";
import { ApiError, AskResponse, askQuestion } from "@/lib/api";
import MatchMeter from "@/components/MatchMeter";

export default function AskPanel() {
  const [question, setQuestion] = useState("");
  const [result, setResult] = useState<AskResponse | null>(null);
  const [status, setStatus] = useState<{ kind: "idle" | "loading" | "error"; message?: string }>({
    kind: "idle",
  });

  async function handleAsk() {
    if (!question.trim()) return;
    setStatus({ kind: "loading" });
    setResult(null);
    try {
      const response = await askQuestion(question);
      setResult(response);
      setStatus({ kind: "idle" });
    } catch (err) {
      const message = err instanceof ApiError ? err.message : "Could not reach the backend.";
      setStatus({ kind: "error", message });
    }
  }

  return (
    <section className="flex flex-col gap-4">
      <h2 className="font-display text-sm tracking-[0.2em] text-parchment-dim uppercase">02 / Ask</h2>

      <div className="flex gap-2">
        <input
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") handleAsk();
          }}
          placeholder="Ask something about your indexed documents..."
          className="flex-1 border border-grid bg-ink-raised px-4 py-3 font-body text-sm text-parchment placeholder:text-parchment-dim focus:outline-none focus:border-signal"
        />
        <button
          onClick={handleAsk}
          disabled={status.kind === "loading"}
          className="border border-signal px-5 py-3 font-display text-sm text-signal transition-colors hover:bg-signal hover:text-ink disabled:opacity-40 disabled:hover:bg-transparent disabled:hover:text-signal"
        >
          {status.kind === "loading" ? "..." : "Ask"}
        </button>
      </div>

      {status.kind === "error" && (
        <p className="font-mono text-xs text-miss">Query failed: {status.message}</p>
      )}

      {result && (
        <div className="flex flex-col gap-6">
          <div className="border border-grid bg-ink-raised p-5">
            <div className="mb-3 flex items-center justify-between">
              <span className="font-display text-xs tracking-[0.2em] text-parchment-dim uppercase">
                Answer
              </span>
              <span className="font-mono text-[10px] text-parchment-dim">
                {result.latency_ms}ms
              </span>
            </div>
            <p className="whitespace-pre-wrap font-body text-sm leading-relaxed text-parchment">
              {result.answer}
            </p>
          </div>

          <div className="flex flex-col gap-2">
            <span className="font-display text-xs tracking-[0.2em] text-parchment-dim uppercase">
              Retrieved passages
            </span>
            {result.sources.length === 0 ? (
              <p className="font-mono text-xs text-parchment-dim">
                No passages retrieved. Ingest a document first.
              </p>
            ) : (
              result.sources.map((s, i) => (
                <MatchMeter key={i} source={s.source} distance={s.distance} />
              ))
            )}
          </div>
        </div>
      )}
    </section>
  );
}
