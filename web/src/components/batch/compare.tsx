import Link from "next/link";

import ChartTip from "@/components/chart-tip";
import { CallChip } from "@/components/chips";
import ValueBars from "@/components/value-bars";
import { StatusIcon } from "@/components/verdicts";
import type { Batch, Output } from "@/lib/api";
import { compact, inr } from "@/lib/format";

type Row = Batch["rows"][number];

// The short word for each answer in the scorecard; the full sentence shows on hover.
const WORDS: Record<string, Partial<Record<Output["status"], string>>> = {
  quote: { good: "Fair", warn: "High side", bad: "Too high" },
  budget: { good: "Fits", warn: "Low end only", bad: "Over budget" },
  audience: { good: "Real", warn: "Some fake", bad: "Mostly fake" },
  value: { good: "Good value", warn: "A bit pricey", bad: "Expensive" },
  consistency: { good: "Reliable", warn: "Hit or miss", bad: "Unreliable" },
  ads: { good: "Ads work", warn: "Ads weaker", bad: "Ads flop", info: "No ads yet" },
  fit: { good: "Fits", warn: "Partial", bad: "Weak fit" },
  competitor: { warn: "Rival ad" },
};

const COLUMNS: [string, string][] = [
  ["quote", "Their quote"],
  ["budget", "Budget"],
  ["audience", "Audience"],
  ["value", "Value"],
  ["consistency", "Reliable"],
  ["ads", "Ads"],
  ["fit", "Product fit"],
];

const done = (rows: Row[]) => rows.filter((r) => r.status === "done" && r.fair != null);
const find = (r: Row, key: string) => r.outputs.find((o) => o.key === key);

function Answer({ o }: { o: Output | undefined }) {
  if (!o) return <span className="text-muted">None</span>;
  return (
    <span className="inline-flex items-center gap-1.5 whitespace-nowrap" title={`${o.title}. ${o.detail}`}>
      <StatusIcon status={o.status} size={16} />
      {WORDS[o.key]?.[o.status] ?? o.title}
    </span>
  );
}

// Who to book first: the cheapest views among the creators worth booking, and why, in plain words.
export function Recommendation({ rows }: { rows: Row[] }) {
  const ready = done(rows);
  if (!ready.length) return null;
  // Rows come cheapest views first with Avoid last, so the first Go is the best value among the safe bookings.
  const best = ready.find((r) => r.call === "Go") ?? ready.find((r) => r.call === "Negotiate");
  const cheapest = ready[0];
  const skip = ready.filter((r) => r.call === "Avoid");
  const why = (r: Row, ...statuses: Output["status"][]) =>
    r.outputs.filter((o) => statuses.includes(o.status) && !["reach", "size", "engagement", "trend"].includes(o.key)).map((o) => o.title);
  return (
    <section aria-label="Recommendation" className="panel grid items-start gap-8 p-6 sm:p-8 lg:grid-cols-[minmax(0,1fr)_minmax(0,26rem)]">
      <div>
      {best ? (
        <>
          <p className="text-2xl font-bold">
            {best.call === "Go" ? "Book " : "Best of these, after a negotiation: "}
            <Link href={`/analyses/${best.analysis_id}`}>@{best.handle}</Link>
            {best.call === "Go" ? " first" : ""}, at about <span className="figure">{inr(best.fair!)}</span>
          </p>
          <p className="mt-2">{why(best, "good").slice(0, 4).join(" · ")}</p>
          {why(best, "warn", "bad").length > 0 && <p className="mt-1 text-negotiate">Watch: {why(best, "bad", "warn").slice(0, 2).join(" · ")}</p>}
          {cheapest !== best && cheapest.call !== "Avoid" && (
            <p className="mt-4">
              Cheapest views: <Link href={`/analyses/${cheapest.analysis_id}`}>@{cheapest.handle}</Link> at about{" "}
              <span className="figure">{inr(cheapest.fair!)}</span>
              {why(cheapest, "bad", "warn").length > 0 && `, but ${why(cheapest, "bad", "warn")[0].toLowerCase()}: negotiate first`}.
            </p>
          )}
        </>
      ) : (
        <p className="text-2xl font-bold">None of these is worth booking as they are.</p>
      )}
      {skip.length > 0 && (
        <p className="mt-3 text-avoid">
          Skip {skip.map((r) => `@${r.handle}`).join(", ")}: {skip.map((r) => why(r, "bad")[0] ?? "see the report").join("; ")}.
        </p>
      )}
      </div>
      <ValueBars
        rows={done(rows)
          .filter((r) => r.expected_views)
          .map((r) => ({ handle: `@${r.handle}`, fair: r.fair!, views: r.expected_views!, highlight: r === best, usualPerK: r.category_cost_per_1k }))}
        caption="Green is the pick; the white tick is what ₹10,000 buys at WLDD's usual rate for that category."
      />
    </section>
  );
}

export function Scorecard({ rows }: { rows: Row[] }) {
  // A question nobody asked (no quote, no budget, no product) gets no column.
  const cols = COLUMNS.filter(([key]) => rows.some((r) => find(r, key)));
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead className="text-left text-muted">
          <tr>
            <th className="py-2 pr-4 font-normal">Creator</th>
            <th className="py-2 pr-4 font-normal">Call</th>
            <th className="py-2 pr-4 text-right font-normal">Pay about</th>
            <th className="py-2 pr-4 text-right font-normal">Expected views</th>
            {cols.map(([key, label]) => (
              <th key={key} className="py-2 pr-4 font-normal">
                {label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-line">
          {rows.map((r) => (
            <tr key={r.analysis_id}>
              <td className="py-3 pr-4">
                <Link href={`/analyses/${r.analysis_id}`}>@{r.handle}</Link>
              </td>
              {r.status === "done" && r.fair != null ? (
                <>
                  <td className="py-3 pr-4">{r.call && <CallChip call={r.call} />}</td>
                  <td className="py-3 pr-4 text-right">
                    <span className="figure font-semibold">{inr(r.fair)}</span>
                    {r.likely_low != null && r.likely_high != null && (
                      <span className="figure basis block whitespace-nowrap text-xs">
                        likely {inr(r.likely_low)} to {inr(r.likely_high)}
                      </span>
                    )}
                  </td>
                  <td className="figure py-3 pr-4 text-right">{r.expected_views != null && compact(r.expected_views)}</td>
                  {cols.map(([key]) => (
                    <td key={key} className="py-3 pr-4">
                      <Answer o={find(r, key)} />
                    </td>
                  ))}
                </>
              ) : (
                <td colSpan={4 + cols.length} className="basis py-3">
                  {r.status === "running" ? "Running…" : r.reason ?? r.status}
                </td>
              )}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

// Prices on a log scale, so a ₹5,000 creator and a ₹5,00,000 creator can share one chart.
function logScale(values: number[]) {
  const lo = Math.log(Math.min(...values) / 1.3);
  const hi = Math.log(Math.max(...values) * 1.15);
  return (v: number) => (100 * (Math.log(v) - lo)) / (hi - lo);
}

export function PriceChart({ rows, budget }: { rows: Row[]; budget: number | null | undefined }) {
  const ready = done(rows);
  if (!ready.length) return null;
  const x = logScale([...ready.flatMap((r) => [r.low!, r.high!]), ...(budget ? [budget] : [])]);
  return (
    <figure>
      <figcaption className="section-title">What each creator should cost{budget ? " against your budget" : ""}</figcaption>
      <p className="basis mt-1">The tick is the price to aim for, the bright bar where about half of real deals land, the faint bar the full range.</p>
      <div className="relative mt-5 space-y-4">
        {budget && (
          <div className="pointer-events-none absolute inset-y-0 z-10 ml-40 w-[calc(100%-10rem)]" aria-hidden>
            <div className="absolute inset-y-0 border-l-2 border-dashed border-negotiate" style={{ left: `${x(budget)}%` }}>
              <span className="absolute -top-5 left-1 whitespace-nowrap text-xs text-negotiate">budget {inr(budget)}</span>
            </div>
          </div>
        )}
        {ready.map((r) => (
          <div key={r.analysis_id} className="flex items-center gap-4">
            <span className="w-36 shrink-0 truncate text-sm">@{r.handle}</span>
            <ChartTip
              className="flex-1"
              lines={[
                `@${r.handle}`,
                `Aim for ${inr(r.fair!)}`,
                `Likely ${inr(r.likely_low ?? r.low!)} to ${inr(r.likely_high ?? r.high!)} (about half of real deals)`,
                `Full range ${inr(r.low!)} to ${inr(r.high!)}`,
                ...(budget ? [`Your budget ${inr(budget)}`] : []),
              ]}
            >
            <div className="relative h-6">
              <span className="absolute top-2.5 h-1 rounded bg-info/35" style={{ left: `${x(r.low!)}%`, width: `${x(r.high!) - x(r.low!)}%` }} />
              <span className="absolute top-1.5 h-3 rounded bg-info" style={{ left: `${x(r.likely_low ?? r.low!)}%`, width: `${x(r.likely_high ?? r.high!) - x(r.likely_low ?? r.low!)}%` }} />
              <span className="absolute top-0 h-6 w-0.5 bg-accent" style={{ left: `${x(r.fair!)}%` }} />
              <span className="figure absolute top-0.5 whitespace-nowrap pl-2 text-xs" style={{ left: `${x(r.high!)}%` }}>
                {inr(r.fair!)}
              </span>
            </div>
            </ChartTip>
          </div>
        ))}
      </div>
    </figure>
  );
}

export function ReachChart({ rows }: { rows: Row[] }) {
  const ready = done(rows).filter((r) => r.expected_views != null);
  if (!ready.length) return null;
  const most = Math.max(...ready.map((r) => r.views_high ?? r.expected_views!));
  const pct = (v: number) => (100 * v) / most;
  return (
    <figure>
      <figcaption className="section-title">Who will see the reel</figcaption>
      <p className="basis mt-1">Expected views on the sponsored reel; the thin line runs from a weak reel to a strong one.</p>
      <div className="mt-5 space-y-4">
        {ready.map((r) => (
          <div key={r.analysis_id} className="flex items-center gap-4">
            <span className="w-36 shrink-0 truncate text-sm">@{r.handle}</span>
            <ChartTip
              className="flex-1"
              lines={[
                `@${r.handle}`,
                `About ${compact(r.expected_views!)} views on the sponsored reel`,
                ...(r.views_low != null && r.views_high != null ? [`A weak reel ${compact(r.views_low)}, a strong one ${compact(r.views_high)}`] : []),
              ]}
            >
            <div className="relative h-6">
              {r.views_low != null && r.views_high != null && (
                <span className="absolute top-2.5 h-1 rounded bg-info/35" style={{ left: `${pct(r.views_low)}%`, width: `${pct(r.views_high) - pct(r.views_low)}%` }} />
              )}
              <span className="absolute top-1 h-4 rounded bg-info" style={{ width: `${pct(r.expected_views!)}%` }} />
            </div>
            </ChartTip>
            <span className="figure w-28 shrink-0 text-right text-sm">{compact(r.expected_views!)}</span>
          </div>
        ))}
      </div>
    </figure>
  );
}
