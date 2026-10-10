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
          <p className="basis">Fair price range for one reel</p>
          <p className="figure font-bold leading-none" style={{ fontSize: "clamp(2.5rem, min(5vw, 11vh), 4.5rem)" }}>
            {inr(p.low)} to {inr(p.high)}
          </p>
          <p className="basis mt-2">Holds about 3 in 4 real prices in testing.</p>
          {/* Only for mega creators: below 10L followers the published rate cards are noise next to WLDD's own deals. */}
          {p.market_reference && r.profile.followers >= 1_000_000 && (
            <p className="basis mt-1 max-w-xl">
              Published asking price for {p.market_reference.tier.toLowerCase()}: {inr(p.market_reference.low)} to {inr(p.market_reference.high)}.
            </p>
          )}
          {r.web_rate && r.web_rate.sources.length > 0 && (
            <p className="basis mt-1 max-w-xl">
              Web check read:{" "}
              {r.web_rate.sources.slice(0, 3).map((s, i) => (
                <span key={s.url}>
                  {i > 0 && ", "}
                  <a href={s.url} target="_blank" rel="noreferrer">
                    {s.title}
                  </a>
                </span>
              ))}
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
