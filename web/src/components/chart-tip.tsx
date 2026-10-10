import { useId } from "react";

// Every hand-drawn chart shows its numbers the same way: hover a bar, or tab to it, and a small card lists what it
// stands for. Styled like the Recharts tooltips on the reel chart and the About page.
export default function ChartTip({ lines, children, className = "" }: { lines: React.ReactNode[]; children: React.ReactNode; className?: string }) {
  const id = useId();
  return (
    <span tabIndex={0} aria-describedby={id} className={`group relative block rounded ${className}`}>
      {children}
      <span
        id={id}
        role="tooltip"
        className="pointer-events-none invisible absolute bottom-full left-0 z-20 mb-2 w-max max-w-xs rounded-lg bg-surface px-3 py-2 text-sm text-text opacity-0 shadow-lg ring-1 ring-line transition-opacity duration-150 group-hover:visible group-hover:opacity-100 group-focus-visible:visible group-focus-visible:opacity-100"
      >
        {lines.map((line, i) => (
          <span key={i} className={`block ${i === 0 ? "font-semibold" : "figure"}`}>
            {line}
          </span>
        ))}
      </span>
    </span>
  );
}
