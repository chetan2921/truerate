"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";

import ValueBars from "@/components/value-bars";
import { StatusIcon } from "@/components/verdicts";
import { api, type BrandRun } from "@/lib/api";
import { compact, inr } from "@/lib/format";

type Result = NonNullable<BrandRun["result"]>;
type Pick = Result["picks"][number];
type Answer = Pick["answers"][number];

// The short word for each answer in the scorecard; the full sentence shows on hover.
const WORDS: Record<string, Partial<Record<Answer["status"], string>>> = {
  fit: { good: "Fits", warn: "Sometimes", bad: "Rarely" },
  audience: { good: "Real", warn: "Some fake", bad: "Mostly fake" },
  value: { good: "Good value", warn: "A bit pricey", bad: "Expensive" },
  budget: { good: "Fits", warn: "Low end only", bad: "Over" },
  consistency: { good: "Reliable", warn: "Hit or miss", bad: "Unreliable" },
  brand: { good: "Yes" },
};
const COLUMNS: [string, string][] = [
  ["fit", "Product fit"],
  ["audience", "Audience"],
  ["value", "Value"],
  ["budget", "Budget"],
  ["consistency", "Reliable"],
];

function Cell({ a }: { a: Answer | undefined }) {
  if (!a) return <span className="text-muted">No</span>;
  return (
    <span className="inline-flex items-center gap-1.5 whitespace-nowrap" title={a.title}>
      <StatusIcon status={a.status} size={16} />
      {WORDS[a.key]?.[a.status] ?? a.title}
    </span>
  );
}

function Handle({ p }: { p: Pick }) {
  return p.analysis_id ? <Link href={`/analyses/${p.analysis_id}`}>@{p.handle}</Link> : <span>@{p.handle}</span>;
}

export default function BrandResult({ run }: { run: BrandRun }) {
  const router = useRouter();
  const [starting, setStarting] = useState(false);
  const r = run.result!;
  const b = r.brand;
  const budget = run.request.budget;
  const inPlan = new Set(r.plan?.handles ?? []);
  const planned = r.picks.filter((p) => inPlan.has(p.handle));
  const top = r.picks[0];
  const cols = COLUMNS.filter(([key]) => key !== "budget" || budget);

  async function priceThem() {
    setStarting(true);
    try {
      const { id } = await api.createBatch({ handles: r.to_price.slice(0, 20), category: b.product, budget: budget ?? null });
      router.push(`/batch/${id}`);
    } catch {
      setStarting(false);
    }
  }

  return (
    <main className="mx-auto max-w-6xl px-6 pb-24 pt-4">
      <h1 className="text-3xl font-bold">Creators for {b.name}</h1>
      <p className="basis mt-1">
        {b.product} ({b.category}) · sells to {b.audience} · {b.tone} · {b.price_tier} price ·{" "}
        {b.source === "instagram" ? `read from Instagram @${b.handle}` : b.source === "website" ? `read from ${b.url}` : "from its name only"} · {r.pool_size} creators
        considered
      </p>

      <section aria-label="Recommendation" className="panel mt-6 grid items-start gap-8 p-6 sm:p-8 lg:grid-cols-[minmax(0,1fr)_minmax(0,26rem)]">
        <div>
          {budget && planned.length > 0 ? (
            <>
              <p className="text-2xl font-bold">
                With {inr(budget)}, book {planned.map((p) => `@${p.handle}`).join(", ")}
              </p>
              <p className="mt-2">
                About <b className="figure">{compact(r.plan!.views)} views</b> for <b className="figure">{inr(r.plan!.cost)}</b>, the most views of any set of these
                creators that fits the budget.
              </p>
            </>
          ) : budget ? (
            <p className="text-2xl font-bold">None of the top creators fits {inr(budget)}; the closest are below.</p>
          ) : top ? (
            <p className="text-2xl font-bold">
              Best match: <Handle p={top} /> at about <span className="figure">{inr(top.fair)}</span>
            </p>
          ) : (
            <p className="text-2xl font-bold">No creator in the pool can be priced for this brand yet.</p>
          )}
          <h2 className="mt-6 font-semibold">Best matches</h2>
          <ol className="mt-2 space-y-2">
            {r.picks.slice(0, 3).map((p, i) => (
              <li key={p.handle} className="flex gap-3">
                <span className="figure basis w-4 shrink-0 text-right">{i + 1}.</span>
                <span>
                  <b className="font-semibold">
                    <Handle p={p} />
                  </b>{" "}
                  <span className="basis">{p.reasons.join(" · ")}</span>
                </span>
              </li>
            ))}
          </ol>
        </div>
        <ValueBars
          rows={r.picks
            .filter((p) => p.expected_views)
            .map((p) => ({ handle: `@${p.handle}`, fair: p.fair, views: p.expected_views!, highlight: inPlan.has(p.handle), usualPerK: p.category_cost_per_1k }))}
          caption={inPlan.size ? "Green bars are the budget plan; the white tick is WLDD's usual rate." : "The white tick is what ₹10,000 buys at WLDD's usual rate."}
        />
      </section>

      <section aria-labelledby="ranked" className="pt-12">
        <h2 id="ranked" className="section-title">
          The top {r.picks.length} for {b.product}
        </h2>
        <p className="basis mt-1">Ranked by fit, a real audience, value for money{budget ? ", the budget" : ""} and reliability. Hover an answer for the reason.</p>
        <div className="mt-4 overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="text-left text-muted">
              <tr>
                <th className="py-2 pr-3 font-normal">#</th>
                <th className="py-2 pr-4 font-normal">Creator</th>
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
              {r.picks.map((p, i) => (
                <tr key={p.handle} className={inPlan.has(p.handle) ? "bg-surface" : ""}>
                  <td className="figure py-3 pr-3 text-muted">{i + 1}</td>
                  <td className="py-3 pr-4">
                    <Handle p={p} />
                    <span className="basis block text-xs">{p.sources.join(" · ")}</span>
                  </td>
                  <td className="py-3 pr-4 text-right">
                    <span className="figure font-semibold">{inr(p.fair)}</span>
                    {p.likely_low != null && p.likely_high != null && (
                      <span className="figure basis block whitespace-nowrap text-xs">
                        likely {inr(p.likely_low)} to {inr(p.likely_high)}
                      </span>
                    )}
                  </td>
                  <td className="figure py-3 pr-4 text-right">{p.expected_views != null && compact(p.expected_views)}</td>
                  {cols.map(([key]) => (
                    <td key={key} className="py-3 pr-4">
                      <Cell a={p.answers.find((a) => a.key === key)} />
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {inPlan.size > 0 && <p className="basis mt-2">Highlighted rows are the budget plan.</p>}
      </section>

      {r.to_price.length > 0 && (
        <section aria-labelledby="to-price" className="pt-14">
          <h2 id="to-price" className="section-title">
            Seen with {b.name}, not priced yet
          </h2>
          <p className="basis mt-1 max-w-2xl">
            Accounts that co-authored, appeared in or tagged the brand&apos;s posts. Some may be brands or fan pages. Pricing them runs a full analysis for each, about
            20 Instagram requests apiece.
          </p>
          <ul className="mt-4 flex flex-wrap gap-2 text-sm">
            {r.to_price.map((h) => (
              <li key={h} className="rounded-lg px-3 py-1 ring-1 ring-line">
                <a href={`https://www.instagram.com/${h}/`} target="_blank" rel="noreferrer">
                  @{h}
                </a>
              </li>
            ))}
          </ul>
          <button type="button" className="btn btn-quiet mt-4" onClick={priceThem} disabled={starting}>
            {starting ? "Starting…" : `Price ${Math.min(r.to_price.length, 20)} of them as a batch`}
          </button>
        </section>
      )}
    </main>
  );
}
