interface MatchMeterProps {
  source: string;
  distance: number;
}

/**
 * Renders cosine distance as a tick-marked signal meter instead of a
 * generic progress bar. Strength = 1 - distance, matching the actual
 * cosine-similarity math the backend uses.
 */
export default function MatchMeter({ source, distance }: MatchMeterProps) {
  const strength = Math.max(0, Math.min(1, 1 - distance));
  const pct = Math.round(strength * 100);

  const tone = strength > 0.6 ? "text-signal" : strength > 0.4 ? "text-circuit" : "text-parchment-dim";
  const barColor = strength > 0.6 ? "bg-signal" : strength > 0.4 ? "bg-circuit" : "bg-parchment-dim";

  return (
    <div className="border border-grid bg-ink-raised px-4 py-3">
      <div className="flex items-baseline justify-between mb-2">
        <span className="font-mono text-xs text-parchment-dim truncate max-w-[60%]">{source}</span>
        <span className={`font-mono text-xs ${tone}`}>{distance.toFixed(4)}</span>
      </div>

      <div className="relative h-3 w-full bg-ink border border-grid">
        {/* tick marks, evoking a graticule/instrument scale */}
        <div className="absolute inset-0 flex justify-between px-[2px] pointer-events-none">
          {Array.from({ length: 11 }).map((_, i) => (
            <div key={i} className="w-px h-full bg-grid" />
          ))}
        </div>
        <div
          className={`h-full ${barColor} transition-all duration-500`}
          style={{ width: `${pct}%` }}
        />
      </div>

      <div className="mt-1 flex justify-between font-mono text-[10px] text-parchment-dim">
        <span>0.0</span>
        <span>match strength {pct}%</span>
        <span>1.0</span>
      </div>
    </div>
  );
}
