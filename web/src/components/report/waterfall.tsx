import type { Report } from "@/lib/api";
import { compact, inr, pct } from "@/lib/format";

type Step = Report["price"]["waterfall"][number];

// The first and last steps are totals drawn from zero; the steps between move a running total.
function layout(steps: Step[]) {
  // Scale to the highest running total, which can sit between the first and last steps.
  const totals = steps.slice(1, -1).reduce((acc, s) => [...acc, acc[acc.length - 1] + s.amount], [steps[0].amount]);
  const max = Math.max(...totals, steps[steps.length - 1].amount, 1);
  const rows = [];
  let running = 0;
  for (const [i, s] of steps.entries()) {
    const isTotal = i === 0 || i === steps.length - 1;
    const from = isTotal ? 0 : running;
    const to = isTotal ? s.amount : running + s.amount;
    running = to;
    rows.push({ ...s, isTotal, isLast: i === steps.length - 1, left: Math.min(from, to) / max, width: Math.abs(to - from) / max, negative: !isTotal && s.amount < 0 });
  }
  return rows;
}

export default function Waterfall({ r }: { r: Report }) {
  const p = r.price;
  const rows = layout(p.waterfall);
  const paid = r.placement.paid;
  const notes = [
    paid.n
      ? `Sponsored performance: ${paid.n} paid reels keep ${pct(paid.ratio ?? 0)} of own-reel views, against ${pct(paid.typical_ratio)} for a typical WLDD creator. Few ads are pulled toward the typical figure.`
      : `Sponsored performance: no paid reels in the last 30, so the typical ${pct(paid.typical_ratio)} applies and the price is unchanged.`,
    p.genuine_share < 1
      ? `Fake engagement: ${pct(1 - p.genuine_share)} of engagement is fake beyond what similar creators show, so that share comes off.`
      : "Fake engagement: nothing beyond what similar creators show, so nothing comes off.",
  ];

  return (
    <section aria-labelledby="how" className="grid gap-10 lg:grid-cols-[minmax(0,5fr)_minmax(0,6fr)]">
      <div>
        <h2 id="how" className="section-title">
          How the price was reached
        </h2>
        <ol className="mt-5 space-y-4">
          {rows.map((row) => (
            <li key={row.step}>
              <div className="flex items-baseline justify-between gap-4">
                <span className={row.isTotal ? "font-semibold" : ""}>{row.step}</span>
                <span className={`figure ${row.negative ? "text-avoid" : ""} ${row.isTotal ? "font-semibold" : ""}`}>
                  {row.isTotal ? inr(row.amount) : row.amount === 0 ? "No change" : `${row.amount < 0 ? "−" : "+"}${inr(Math.abs(row.amount))}`}
                </span>
              </div>
              <div className="relative mt-1.5 h-2 rounded bg-line" aria-hidden>
                {row.width > 0 && (
                  <span
                    className={`absolute top-0 h-2 rounded ${row.isTotal ? (row.isLast ? "bg-accent" : "bg-info") : row.negative ? "bg-avoid" : "bg-go"}`}
                    style={{ left: `${row.left * 100}%`, width: `${Math.max(row.width * 100, 0.8)}%` }}
                  />
                )}
              </div>
            </li>
          ))}
        </ol>
        <ul className="basis mt-5 space-y-1.5">
          {notes.map((n) => (
            <li key={n}>{n}</li>
          ))}
        </ul>
      </div>

      <div>
        <h3 className="font-semibold">The 6 past WLDD deals it compared against</h3>
        <p className="basis mt-1">
          Same category first, then closest in views and followers.{" "}
          {p.ridge_share >= 0.99
            ? "The market price itself comes from a regression over all of WLDD's deals; these are the closest for comparison."
            : `The market price blends their ₹ per 1,000 views (${pct(1 - p.ridge_share)}) with a regression over all deals (${pct(p.ridge_share)}).`}
        </p>
        <div className="mt-4 overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="text-left text-muted">
              <tr>
                <th className="py-2 pr-3 font-normal">Creator</th>
                <th className="py-2 pr-3 text-right font-normal">Followers</th>
                <th className="py-2 pr-3 text-right font-normal">Typical views</th>
                <th className="py-2 pr-3 text-right font-normal">WLDD paid</th>
                <th className="py-2 text-right font-normal">Per 1,000 views</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-line">
              {p.comparables.map((c) => (
                <tr key={c.handle}>
                  <td className="py-2 pr-3">
                    @{c.handle}
                    {c.category !== r.category && <span className="basis"> · {c.category}</span>}
                  </td>
                  <td className="figure py-2 pr-3 text-right">{compact(c.followers)}</td>
                  <td className="figure py-2 pr-3 text-right">{compact(c.views)}</td>
                  <td className="figure py-2 pr-3 text-right">{inr(c.price)}</td>
                  <td className="figure py-2 text-right">{inr(c.per_1k_views)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </section>
  );
}
