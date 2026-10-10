import { CallChip, VERDICT_COLOR, VERDICTS } from "@/components/chips";
import Verdicts from "@/components/verdicts";
import type { Output, Report } from "@/lib/api";
import { inr } from "@/lib/format";

export default function Decision({ r, outputs }: { r: Report; outputs: Output[] }) {
  const p = r.price;
  return (
    <section aria-label="Decision" className="panel p-6 sm:p-8">
      <div className="flex flex-wrap items-start justify-between gap-6">
        <div>
          <p className="basis">Pay about, for one reel</p>
          <p className="figure font-bold leading-none" style={{ fontSize: "clamp(2.5rem, min(5vw, 11vh), 4.5rem)" }}>
            {inr(p.fair)}
          </p>
          {/* Honest about spread: a band 3x wide holds about half of real prices on unseen deals; the full range about 3 in 4. */}
          {p.likely_low != null && p.likely_high != null && (
            <p className="mt-3 text-lg">
              Likely <span className="figure font-semibold">{inr(p.likely_low)} to {inr(p.likely_high)}</span>
              <span className="basis"> · about half of real deals land in a band this wide</span>
            </p>
          )}
          <p className="basis mt-1">
            Full range <span className="figure text-text">{inr(p.low)} to {inr(p.high)}</span> · holds about 3 in 4 real prices in testing
          </p>
          {p.market_reference && (
            <p className="basis mt-1 max-w-xl">
              Published asking price for {p.market_reference.tier.toLowerCase()}: {inr(p.market_reference.low)} to {inr(p.market_reference.high)}.
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

      {/* The answers, not the measurements: views, value, reliability, ads, fit and rivals each as one plain line. */}
      <div className="mt-8">
        <Verdicts outputs={outputs} />
      </div>
    </section>
  );
}
