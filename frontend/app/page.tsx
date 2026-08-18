"use client";

import { useEffect, useState } from "react";
import { checkHealth } from "@/lib/api";
import IngestPanel from "@/components/IngestPanel";
import AskPanel from "@/components/AskPanel";
import StatusBadge from "@/components/StatusBadge";

interface IndexedDoc {
  filename: string;
  chunks: number;
}

export default function Home() {
  const [connected, setConnected] = useState<boolean | null>(null);
  const [indexedDocs, setIndexedDocs] = useState<IndexedDoc[]>([]);

  useEffect(() => {
    checkHealth().then(setConnected);
    const interval = setInterval(() => checkHealth().then(setConnected), 15000);
    return () => clearInterval(interval);
  }, []);

  return (
    <main className="graticule-bg min-h-screen">
      <div className="mx-auto max-w-5xl px-6 py-10">
        <header className="mb-10 flex items-baseline justify-between border-b border-grid pb-6">
          <div>
            <h1 className="font-display text-2xl font-medium tracking-tight text-parchment">
              RAG Console
            </h1>
            <p className="mt-1 font-mono text-xs text-parchment-dim">
              retrieval-augmented question answering
            </p>
          </div>
          <StatusBadge connected={connected} />
        </header>

        <div className="grid grid-cols-1 gap-10 md:grid-cols-[minmax(0,1fr)_minmax(0,1.4fr)]">
          <IngestPanel
            indexedDocs={indexedDocs}
            onIngested={(doc) => setIndexedDocs((prev) => [...prev, doc])}
          />
          <AskPanel />
        </div>
      </div>
    </main>
  );
}
