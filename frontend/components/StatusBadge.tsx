interface StatusBadgeProps {
  connected: boolean | null;
}

export default function StatusBadge({ connected }: StatusBadgeProps) {
  const label =
    connected === null ? "checking..." : connected ? "connected to :8000" : "backend unreachable";
  const dotColor =
    connected === null ? "bg-parchment-dim" : connected ? "bg-signal" : "bg-miss";

  return (
    <div className="flex items-center gap-2 font-mono text-xs text-parchment-dim">
      <span
        className={`inline-block h-2 w-2 rounded-full ${dotColor} ${connected ? "animate-pulse" : ""}`}
      />
      {label}
    </div>
  );
}
