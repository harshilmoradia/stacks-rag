"use client";

import { useRef, useState } from "react";
import { ApiError, ingestFile } from "@/lib/api";

interface IndexedDoc {
  filename: string;
  chunks: number;
}

interface IngestPanelProps {
  onIngested: (doc: IndexedDoc) => void;
  indexedDocs: IndexedDoc[];
}

export default function IngestPanel({ onIngested, indexedDocs }: IngestPanelProps) {
  const [dragOver, setDragOver] = useState(false);
  const [status, setStatus] = useState<{ kind: "idle" | "loading" | "error"; message?: string }>({
    kind: "idle",
  });
  const inputRef = useRef<HTMLInputElement>(null);

  async function handleFile(file: File) {
    setStatus({ kind: "loading" });
    try {
      const result = await ingestFile(file);
      onIngested({ filename: result.filename, chunks: result.chunks_indexed });
      setStatus({ kind: "idle" });
    } catch (err) {
      const message = err instanceof ApiError ? err.message : "Could not reach the backend.";
      setStatus({ kind: "error", message });
    }
  }

  return (
    <section className="flex flex-col gap-4">
      <h2 className="font-display text-sm tracking-[0.2em] text-parchment-dim uppercase">
        01 / Ingest
      </h2>

      <div
        onDragOver={(e) => {
          e.preventDefault();
          setDragOver(true);
        }}
        onDragLeave={() => setDragOver(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDragOver(false);
          const file = e.dataTransfer.files?.[0];
          if (file) handleFile(file);
        }}
        onClick={() => inputRef.current?.click()}
        className={`cursor-pointer border-2 border-dashed px-6 py-10 text-center transition-colors ${
          dragOver ? "border-signal bg-ink-raised" : "border-grid"
        }`}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".txt,.md,.markdown,.pdf"
          className="hidden"
          onChange={(e) => {
            const file = e.target.files?.[0];
            if (file) handleFile(file);
          }}
        />
        <p className="font-mono text-sm text-parchment-dim">
          {status.kind === "loading" ? "indexing..." : "drop a .txt / .md / .pdf, or click to browse"}
        </p>
      </div>

      {status.kind === "error" && (
        <p className="font-mono text-xs text-miss">Ingest failed: {status.message}</p>
      )}

      <div className="flex flex-col gap-2">
        {indexedDocs.length === 0 ? (
          <p className="font-mono text-xs text-parchment-dim">No documents indexed yet this session.</p>
        ) : (
          indexedDocs.map((doc, i) => (
            <div
              key={`${doc.filename}-${i}`}
              className="flex justify-between border border-grid bg-ink-raised px-3 py-2 font-mono text-xs"
            >
              <span className="text-parchment truncate max-w-[70%]">{doc.filename}</span>
              <span className="text-circuit">{doc.chunks} chunks</span>
            </div>
          ))
        )}
      </div>
    </section>
  );
}
