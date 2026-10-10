import { CallChip, VERDICT_COLOR, VERDICTS } from "@/components/chips";
import type { Report } from "@/lib/api";
import { compact, inr } from "@/lib/format";

const REASON_DOT: Record<string, string> = { Go: "bg-go", Negotiate: "bg-negotiate", Avoid: "bg-avoid" };

export default function Decision({ r }: { r: Report }) {
  const p = r.price;
  const d = p.delivery;
  return (
    <section aria-label="Decision" className="panel p-6 sm:p-8">
      <div className="flex flex-wrap items-start justify-between gap-6">
        <div>
          <p className="basis">Recommended price for one reel</p>
          <p className="figure font-bold leading-none" style={{ fontSize: "clamp(2.75rem, min(6vw, 12vh), 5rem)" }}>
            {inr(p.fair)}
          </p>
          <p className="figure mt-3 text-lg">
            Fair range {inr(p.low)} to {inr(p.high)}
          </p>
          {p.note && <p className="mt-2 max-w-xl text-sm text-negotiate">{p.note}</p>}
          {p.market_reference && (
            <p className="basis mt-2 max-w-xl">
              Published asking price for {p.market_reference.tier.toLowerCase()}: {inr(p.market_reference.low)} to {inr(p.market_reference.high)} ({p.market_reference.source}).
            </p>
          )}
        </div>
        <CallChip call={r.decision.call} large />
      </div>

      <div className="mt-6 flex flex-wrap gap-2" role="list" aria-label="Audience verdict">
        {VERDICTS.map((v) => {
          const lit = v === r.audience.verdict;
          return (
            <span
              key={v}
              role="listitem"
              aria-current={lit ? "true" : undefined}
              className={`rounded-lg px-3 py-1 text-sm ${lit ? "font-semibold text-bg" : "text-muted ring-1 ring-line"}`}
              style={lit ? { background: VERDICT_COLOR[v] } : undefined}
            >
              {v}
            </span>
          );
        })}
      </div>

      <p className="mt-6 max-w-3xl text-base">
        On the sponsored reel, expect about <b className="figure">{compact(d.views[1])} views</b> (a weak one {compact(d.views[0])}, a strong one {compact(d.views[2])}),{" "}
        {compact(d.likes)} likes and {compact(d.comments)} comments. That is {inr(d.cost_per_1k)} per 1,000 typical views
        {d.category_cost_per_1k ? `, against ${inr(d.category_cost_per_1k)} for the ${r.category} creators WLDD has booked` : ""}.
      </p>

      <ul className="mt-5 space-y-2">
        {r.decision.reasons.map((reason) => (
          <li key={reason} className="flex gap-3">
            <span className={`mt-2 h-1.5 w-1.5 shrink-0 rounded-full ${REASON_DOT[r.decision.call]}`} aria-hidden />
            <span>{reason}</span>
          </li>
        ))}
      </ul>
    </section>
  );
}
