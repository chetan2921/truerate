"use client";

import { use, useEffect, useState } from "react";

import { api, type Analysis } from "@/lib/api";
import { compact, inr } from "@/lib/format";

// The client one-pager: the decision block, the waterfall and the red flags on A4, black on white (DESIGN.md, Print).
export default function PrintView({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const [a, setA] = useState<Analysis | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api.getAnalysis(id).then(setA).catch((e) => setError((e as Error).message));
  }, [id]);
  useEffect(() => {
    if (a?.result) setTimeout(() => window.print(), 300);
  }, [a]);

  if (error) return <main className="mx-auto max-w-3xl px-6 pt-10">{error}</main>;
  if (!a?.result) return <main className="mx-auto max-w-3xl px-6 pt-10">Loading…</main>;
  const r = a.result;
  const p = r.price;
  const d = p.delivery;

  return (
    <main className="mx-auto my-6 max-w-[210mm] bg-white p-[14mm] text-black print:m-0 print:max-w-none">
      <div className="flex items-baseline justify-between">
        <h1 className="text-2xl font-bold">@{r.handle}</h1>
        <span className="text-sm text-neutral-700">TruRate by WLDD · {new Date(r.fetched_at).toLocaleDateString("en-IN")}</span>
      </div>
      <p className="mt-1 text-sm text-neutral-700">
        {r.profile.full_name} · {compact(r.profile.followers)} followers · {r.category}
      </p>

      <div className="mt-6 flex items-end justify-between border-y border-neutral-300 py-5">
        <div>
          <p className="text-sm text-neutral-700">Fair price range for one reel</p>
          <p className="figure text-4xl font-bold">
            {inr(p.low)} to {inr(p.high)}
          </p>
        </div>
        <div className="text-right">
          <p className="text-3xl font-bold">{r.decision.call}</p>
          <p className="text-sm">{r.audience.verdict}</p>
        </div>
      </div>

      <p className="mt-4">
        Expected on the sponsored reel: about {compact(d.views[1])} views ({compact(d.views[0])} to {compact(d.views[2])}), {compact(d.likes)} likes and {compact(d.comments)} comments, at{" "}
        {inr(d.cost_per_1k)} per 1,000 typical views{d.category_cost_per_1k ? ` (${r.category} average ${inr(d.category_cost_per_1k)})` : ""}.
      </p>
      <ul className="mt-3 list-disc space-y-1 pl-5">
        {r.decision.reasons.map((x) => (
          <li key={x}>{x}</li>
        ))}
      </ul>

      <h2 className="mt-6 font-semibold">How the price was reached</h2>
      <table className="mt-2 w-full text-sm">
        <tbody className="divide-y divide-neutral-200">
          {p.waterfall.map((s, i) => (
            <tr key={s.step}>
              {/* Reports saved before the range became the headline call the last step "Recommended price". */}
              <td className="py-1.5">{i === p.waterfall.length - 1 ? "Middle of the fair range" : s.step}</td>
              <td className="figure py-1.5 text-right">{s.amount < 0 ? "−" : ""}{inr(Math.abs(s.amount))}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <h2 className="mt-6 font-semibold">Red flags</h2>
      {r.audience.flags.length === 0 ? (
        <p className="mt-1 text-sm">None: likes, followers and comments all look like similar creators&apos;.</p>
      ) : (
        <ul className="mt-1 list-disc space-y-1 pl-5 text-sm">
          {r.audience.flags.map((f) => (
            <li key={f.signal}>{f.text}</li>
          ))}
        </ul>
      )}

      <p className="mt-8 text-xs text-neutral-600">
        Prices come from WLDD&apos;s past deals and this creator&apos;s public reels; the authenticity checks compare them with WLDD creators of the same size.
      </p>
      <button type="button" onClick={() => window.print()} className="btn mt-6 bg-black text-white print:hidden">
        Print or save as PDF
      </button>
    </main>
  );
}
