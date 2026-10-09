"use client";

import { useEffect, useState } from "react";
import { ReferenceLine, ResponsiveContainer, Scatter, ScatterChart, Tooltip, XAxis, YAxis } from "recharts";

import { api, type ModelReport } from "@/lib/api";
import { compact, inr, pct } from "@/lib/format";

import { FAKE_KINDS, FLOW, LIMITS, OTHER_PAGES, SIGNALS } from "./content";

type Holdout = { n: number; coverage: number; points: { actual: number; predicted: number; band: string }[] } & Record<string, { median_error: number; by_band: Record<string, number | null> }>;
const METHODS: [string, string][] = [["model", "TrueRate"], ["band_median", "Band median price"], ["modash", "Modash-style formula"]];
// Log axes read best on 1-3-10 steps.
const STEPS = [1e3, 3e3, 1e4, 3e4, 1e5, 3e5, 1e6, 3e6, 1e7, 3e7];

export default function AboutPage() {
  const [report, setReport] = useState<ModelReport | null>(null);
  useEffect(() => {
    api.modelReport().then(setReport).catch(() => setReport({ validation: null, redteam: null }));
  }, []);
  const v = report?.validation as { holdout: Holdout; by_category: Record<string, Record<string, number>>; n_deals: number } | null | undefined;
  const rt = report?.redteam as { n: number; unmodified_flagged: number; caught: Record<string, number>; genuine_share: Record<string, number> } | null | undefined;
  const pts = v?.holdout.points ?? [];
  const lo = Math.min(...pts.map((p) => Math.min(p.actual, p.predicted)), 1000);
  const hi = Math.max(...pts.map((p) => Math.max(p.actual, p.predicted)), 10000);
  const ticks = STEPS.filter((t) => t >= lo * 0.8 && t <= hi * 1.2);

  return (
    <main className="mx-auto max-w-6xl px-6 pb-24 pt-[min(6vh,3rem)]">
      <h1 className="max-w-3xl text-3xl font-bold">How TrueRate prices a reel, and how well it does</h1>

      <section aria-labelledby="accuracy" className="pt-8">
        <h2 id="accuracy" className="section-title">
          Tested against prices WLDD actually paid
        </h2>
        {!v ? (
          <p className="basis mt-2">No validation report yet. It appears after `truerate validate` runs on the collected creators.</p>
        ) : (
          <div className="mt-4 grid gap-10 lg:grid-cols-[minmax(0,1fr)_minmax(0,1fr)]">
            <div>
              <div className="h-80" role="img" aria-label="Predicted against actual price for each held-out creator">
                <ResponsiveContainer width="100%" height="100%">
                  <ScatterChart margin={{ top: 8, right: 8, bottom: 20, left: 8 }}>
                    <XAxis type="number" dataKey="actual" name="Paid" scale="log" domain={[lo * 0.8, hi * 1.2]} ticks={ticks} tickFormatter={compact} tick={{ fill: "var(--text-muted)", fontSize: 12 }}
                      axisLine={{ stroke: "var(--line)" }} tickLine={false} label={{ value: "What WLDD paid", position: "insideBottom", offset: -12, fill: "var(--text-muted)", fontSize: 12 }} />
                    <YAxis type="number" dataKey="predicted" name="Predicted" scale="log" domain={[lo * 0.8, hi * 1.2]} ticks={ticks} tickFormatter={compact} tick={{ fill: "var(--text-muted)", fontSize: 12 }}
                      axisLine={false} tickLine={false} width={44} />
                    <ReferenceLine segment={[{ x: lo, y: lo }, { x: hi, y: hi }]} stroke="var(--line)" strokeDasharray="4 4" />
                    <Tooltip formatter={(x) => inr(Number(x))} contentStyle={{ background: "var(--surface)", border: "none", borderRadius: 8 }} />
                    <Scatter data={pts} fill="var(--accent)" isAnimationActive={false} />
                  </ScatterChart>
                </ResponsiveContainer>
              </div>
              <p className="basis mt-1">
                {v.holdout.n} creators held out of training. On the dashed line, the prediction equals what WLDD paid. {pct(v.holdout.coverage)} of their prices fall inside TrueRate&apos;s range.
              </p>
            </div>
            <div>
              <table className="w-full text-sm">
                <caption className="basis mb-2 text-left">Median error on the held-out creators, by follower band</caption>
                <thead className="text-left text-muted">
                  <tr>
                    <th className="py-2 pr-3 font-normal">Method</th>
                    <th className="py-2 pr-3 text-right font-normal">All</th>
                    <th className="py-2 pr-3 text-right font-normal">Under 20K</th>
                    <th className="py-2 pr-3 text-right font-normal">20K to 100K</th>
                    <th className="py-2 text-right font-normal">100K+</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-line">
                  {METHODS.map(([key, label]) => (
                    <tr key={key} className={key === "model" ? "font-semibold" : ""}>
                      <td className="py-2 pr-3">{label}</td>
                      <td className="figure py-2 pr-3 text-right">{pct(v.holdout[key].median_error)}</td>
                      {["small", "medium", "big"].map((b) => (
                        <td key={b} className="figure py-2 pr-3 text-right last:pr-0">
                          {v.holdout[key].by_band[b] == null ? "n/a" : pct(v.holdout[key].by_band[b] as number)}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
              <table className="mt-8 w-full text-sm">
                <caption className="basis mb-2 text-left">Median error by category, leave-one-out over all {v.n_deals} deals</caption>
                <thead className="text-left text-muted">
                  <tr>
                    <th className="py-2 pr-3 font-normal">Category</th>
                    <th className="py-2 pr-3 text-right font-normal">Deals</th>
                    <th className="py-2 pr-3 text-right font-normal">TrueRate</th>
                    <th className="py-2 pr-3 text-right font-normal">Band median</th>
                    <th className="py-2 text-right font-normal">Modash-style</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-line">
                  {Object.entries(v.by_category).map(([c, e]) => (
                    <tr key={c}>
                      <td className="py-2 pr-3">{c}</td>
                      <td className="figure py-2 pr-3 text-right">{e.n}</td>
                      <td className="figure py-2 pr-3 text-right font-semibold">{pct(e.model)}</td>
                      <td className="figure py-2 pr-3 text-right">{pct(e.band_median)}</td>
                      <td className="figure py-2 text-right">{pct(e.modash)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </section>

      <section aria-labelledby="fakes" className="max-w-4xl pt-16">
        <h2 id="fakes" className="section-title">
          The fake-creator test
        </h2>
        {!rt ? (
          <p className="basis mt-2">No red-team report yet. It appears after `truerate redteam` runs.</p>
        ) : (
          <>
            <p className="mt-2">
              Each fake is built from a real WLDD creator&apos;s data, {rt.n} of them per kind. Caught means a verdict other than Real audience.{" "}
              {pct(rt.unmodified_flagged)} of the unmodified creators get flagged.
            </p>
            <table className="mt-4 w-full text-sm">
              <thead className="text-left text-muted">
                <tr>
                  <th className="py-2 pr-3 font-normal">Fake</th>
                  <th className="py-2 pr-3 font-normal">How it is built</th>
                  <th className="py-2 pr-3 text-right font-normal">Caught</th>
                  <th className="py-2 text-right font-normal">Price cut</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-line">
                {Object.entries(rt.caught).map(([kind, rate]) => (
                  <tr key={kind}>
                    <td className="py-2 pr-3">{FAKE_KINDS[kind]?.[0] ?? kind}</td>
                    <td className="basis py-2 pr-3">{FAKE_KINDS[kind]?.[1]}</td>
                    <td className={`figure py-2 pr-3 text-right font-semibold ${rate >= 0.8 ? "text-go" : rate >= 0.5 ? "text-negotiate" : "text-avoid"}`}>{pct(rate)}</td>
                    <td className="figure py-2 text-right">{pct(1 - rt.genuine_share[kind])}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </>
        )}
      </section>

      <section aria-labelledby="flow" className="pt-14">
        <h2 id="flow" className="section-title">
          From a handle to a price
        </h2>
        <ol className="mt-4 flex flex-wrap items-stretch gap-y-4 text-sm">
          {FLOW.map((s, i) => (
            <li key={s.title} className="flex max-w-56 items-start">
              <div className="pr-4">
                <p className="font-semibold">{s.title}</p>
                <p className="basis mt-1">{s.detail}</p>
              </div>
              {i < FLOW.length - 1 && <span className="mr-4 text-accent" aria-hidden>→</span>}
            </li>
          ))}
        </ol>
      </section>

      <section aria-labelledby="signals" className="pt-10">
        <h2 id="signals" className="section-title">
          Signals and why each is there
        </h2>
        <table className="mt-3 w-full text-sm">
          <thead className="text-left text-muted">
            <tr>
              <th className="py-2 pr-3 font-normal">Area</th>
              <th className="py-2 pr-3 font-normal">Signal</th>
              <th className="py-2 font-normal">Why</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-line">
            {SIGNALS.map(([area, signal, why]) => (
              <tr key={signal}>
                <td className="basis py-2 pr-3 align-top">{area}</td>
                <td className="py-2 pr-3 align-top">{signal}</td>
                <td className="py-2 align-top text-muted">{why}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      <section aria-labelledby="other" className="grid gap-10 pt-16 lg:grid-cols-[minmax(0,3fr)_minmax(0,2fr)]">
        <div>
          <h2 id="other" className="section-title">
            Pages without a face
          </h2>
          <dl className="mt-3 space-y-4">
            {OTHER_PAGES.map(([title, text]) => (
              <div key={title}>
                <dt className="font-semibold">{title}</dt>
                <dd className="mt-1 text-muted">{text}</dd>
              </div>
            ))}
          </dl>
        </div>
        <div>
          <h2 className="section-title">Known limits</h2>
          <ul className="mt-3 space-y-3 text-muted">
            {LIMITS.map((l) => (
              <li key={l}>{l}</li>
            ))}
          </ul>
        </div>
      </section>
    </main>
  );
}
