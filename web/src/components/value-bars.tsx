import ChartTip from "@/components/chart-tip";
import { compact, inr } from "@/lib/format";

export type ValueRow = { handle: string; fair: number; views: number; highlight?: boolean; usualPerK?: number | null };

// What ₹10,000 buys with each creator: expected views per ₹10,000 at the price to aim for, best value first. One bar per
// row with its handle and figure written beside it, so nothing has to be decoded from axes or a key.
export default function ValueBars({ rows, caption }: { rows: ValueRow[]; caption: string }) {
  if (!rows.length) return null;
  const buys = (r: ValueRow) => (r.views * 10_000) / r.fair;
  const usual = (r: ValueRow) => (r.usualPerK ? 10_000_000 / r.usualPerK : 0);
  const sorted = [...rows].sort((a, b) => buys(b) - buys(a));
  const most = Math.max(...sorted.map((r) => Math.max(buys(r), usual(r))));
  return (
    <figure>
      <figcaption className="font-semibold">What ₹10,000 buys</figcaption>
      <p className="basis mt-1">Expected views for every ₹10,000 at the price to aim for. Longer is better value. {caption} Hover a bar for its numbers.</p>
      <ol className="mt-4 space-y-2.5">
        {sorted.map((r) => (
          <li key={r.handle} className="grid grid-cols-[8.5rem_minmax(0,1fr)_4.5rem] items-center gap-3 text-sm">
            <span className={`truncate ${r.highlight ? "font-semibold text-text" : "text-muted"}`}>{r.handle}</span>
            <ChartTip
              lines={[
                r.handle,
                `Pay about ${inr(r.fair)} for about ${compact(r.views)} views`,
                `₹10,000 buys about ${compact(buys(r))} views`,
                ...(r.usualPerK ? [`White tick: WLDD's usual ${inr(r.usualPerK)} per 1,000 views, so ₹10,000 buys ${compact(usual(r))}`] : []),
              ]}
            >
              <span className="relative block h-3">
                <span className={`absolute inset-y-0 left-0 rounded ${r.highlight ? "bg-accent" : "bg-info/50"}`} style={{ width: `${Math.max((100 * buys(r)) / most, 1)}%` }} />
                {usual(r) > 0 && <span className="absolute -inset-y-1 w-0.5 bg-text" style={{ left: `${(100 * usual(r)) / most}%` }} />}
              </span>
            </ChartTip>
            <span className={`figure text-right ${r.highlight ? "text-text" : "text-muted"}`}>{compact(buys(r))}</span>
          </li>
        ))}
      </ol>
    </figure>
  );
}
