"use client";

import { useState } from "react";
import { Bar, BarChart, Cell, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import type { Report } from "@/lib/api";
import { compact, pct } from "@/lib/format";

const KIND_COLOR = { own: "var(--accent)", paid: "var(--negotiate)", collab: "var(--info)", repost: "rgb(251 251 251 / 0.35)" } as const;
const KIND_LABEL = { own: "Own reel", paid: "Paid", collab: "Collab with a creator", repost: "Repost of someone else's reel" } as const;
const METRICS = ["views", "likes", "comments", "followers"] as const;
type Metric = (typeof METRICS)[number];

const day = (iso: string) => new Date(iso).toLocaleDateString("en-IN", { day: "numeric", month: "short" });

// One chip per brand, most often first, linking to that brand's latest post: "@brand ×9" says more than nine chips.
function byBrand<T extends { brand: string | null; taken_at: string; code: string }>(items: T[]) {
  const groups = new Map<string, T[]>();
  for (const x of items) groups.set(x.brand ?? "", [...(groups.get(x.brand ?? "") ?? []), x]);
  return [...groups.entries()]
    .map(([brand, xs]) => ({ brand, n: xs.length, latest: xs.reduce((a, b) => (a.taken_at > b.taken_at ? a : b)) }))
    .sort((a, b) => b.n - a.n || (a.latest.taken_at < b.latest.taken_at ? 1 : -1));
}

function BrandChips({ items, path }: { items: ReturnType<typeof byBrand>; path: string }) {
  return (
    <ul className="mt-2 flex flex-wrap gap-2 text-sm">
      {items.map((g) => (
        <li key={g.brand || "unnamed"} className="rounded-lg px-3 py-1 ring-1 ring-line">
          <a href={`https://www.instagram.com/${path}/${g.latest.code}/`} target="_blank" rel="noreferrer">
            {g.brand ? `@${g.brand}` : "Brand not named"}
          </a>
          {g.n > 1 && <span className="figure basis"> ×{g.n}</span>}
        </li>
      ))}
    </ul>
  );
}

export default function Placement({ r }: { r: Report }) {
  const [metric, setMetric] = useState<Metric>("views");
  const p = r.placement;
  const reels = [...p.reels].reverse().map((x) => ({ ...x, day: day(x.taken_at) }));
  const history = p.followers_history.map((h) => ({ ...h, day: day(h.at) }));
  const undisclosed = p.ads.filter((a) => !a.disclosed).length;
  const paidVsUsual = p.paid.ratio == null ? null : p.paid.ratio >= p.paid.typical_ratio;

  return (
    <section aria-labelledby="placement">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 id="placement" className="section-title">
          How their reels perform
        </h2>
        <div className="flex gap-1 rounded-lg bg-surface p-1" role="group" aria-label="Chart shows">
          {METRICS.map((m) => (
            <button
              key={m}
              type="button"
              aria-pressed={metric === m}
              onClick={() => setMetric(m)}
              className={`rounded-md px-3 py-1 text-sm capitalize transition-colors duration-150 ${metric === m ? "bg-text text-bg" : "text-muted hover:text-text"}`}
            >
              {m}
            </button>
          ))}
        </div>
      </div>

      <div className="mt-4 h-64" role="img" aria-label={metric === "followers" ? "Followers over time" : `${metric} on each of the last 30 reels`}>
        <ResponsiveContainer width="100%" height="100%">
          {metric === "followers" ? (
            <LineChart data={history} margin={{ top: 8, right: 8, bottom: 0, left: 0 }}>
              <XAxis dataKey="day" tick={{ fill: "var(--text-muted)", fontSize: 12 }} axisLine={{ stroke: "var(--line)" }} tickLine={false} />
              <YAxis tickFormatter={compact} tick={{ fill: "var(--text-muted)", fontSize: 12 }} axisLine={false} tickLine={false} width={48} domain={["auto", "auto"]} />
              <Tooltip formatter={(v) => `${compact(Number(v))} followers`} contentStyle={{ background: "var(--surface)", border: "none", borderRadius: 8 }} labelStyle={{ color: "var(--text)" }} itemStyle={{ color: "var(--text)" }} />
              <Line dataKey="followers" stroke="var(--accent)" strokeWidth={2} dot={{ r: 4, fill: "var(--accent)" }} isAnimationActive={false} />
            </LineChart>
          ) : (
            <BarChart data={reels} margin={{ top: 8, right: 8, bottom: 0, left: 0 }}>
              <XAxis dataKey="day" tick={{ fill: "var(--text-muted)", fontSize: 12 }} axisLine={{ stroke: "var(--line)" }} tickLine={false} interval="preserveStartEnd" minTickGap={24} />
              <YAxis tickFormatter={compact} tick={{ fill: "var(--text-muted)", fontSize: 12 }} axisLine={false} tickLine={false} width={48} />
              <Tooltip
                cursor={{ fill: "rgb(251 251 251 / 0.06)" }}
                contentStyle={{ background: "var(--surface)", border: "none", borderRadius: 8 }} labelStyle={{ color: "var(--text)" }} itemStyle={{ color: "var(--text)" }}
                formatter={(v, _n, item) => [`${compact(Number(v))} ${metric}`, KIND_LABEL[(item.payload as (typeof reels)[number]).kind]]}
              />
              <Bar dataKey={metric} radius={[3, 3, 0, 0]} isAnimationActive={false}>
                {reels.map((x) => (
                  <Cell key={x.code} fill={KIND_COLOR[x.kind]} />
                ))}
              </Bar>
            </BarChart>
          )}
        </ResponsiveContainer>
      </div>
      <p className="basis mt-2 flex flex-wrap gap-x-5 gap-y-1">
        {metric === "followers" ? (
          <span>Instagram doesn&apos;t share follower history, so this builds from TruRate&apos;s first snapshot ({history.length} so far).</span>
        ) : (
          (Object.keys(KIND_COLOR) as (keyof typeof KIND_COLOR)[]).map((k) => (
            <span key={k} className="inline-flex items-center gap-2">
              <span className="h-2.5 w-2.5 rounded-sm" style={{ background: KIND_COLOR[k] }} aria-hidden />
              {KIND_LABEL[k]}
            </span>
          ))
        )}
      </p>

      <ul className="mt-6 max-w-3xl space-y-2">
        <li>
          <b>Consistency:</b> {p.hits_last_10} of the last 10 reels did well, reaching at least half their usual {compact(p.typical_views)} views.
        </li>
        {p.trend != null && (p.trend <= 0.9 || p.trend >= 1.1) && (
          <li>
            <b>Trend:</b> recent reels get {p.trend >= 1 ? `${pct(p.trend - 1)} more` : `${pct(1 - p.trend)} fewer`} views than the ones before.
          </li>
        )}
        <li>
          <b>Ads:</b>{" "}
          {paidVsUsual == null
            ? "no sponsored reels in the last 30, so how an ad does is unknown."
            : paidVsUsual
              ? "their sponsored reels do as well as their own, or better."
              : "their sponsored reels get fewer views than their own."}
        </li>
        {(p.n_reposts ?? 0) > 0 && (
          <li>
            <b>Reposts:</b> {p.n_reposts} of the last 30 reels are someone else&apos;s work, so they are left out of the numbers above.
          </li>
        )}
      </ul>

      {p.ads.length > 0 && (
        <div className="mt-8">
          <h3 className="font-semibold">
            {p.ads.length} ads in the last 30 reels{undisclosed > 0 && <span className="font-normal text-negotiate">, {undisclosed} not disclosed</span>}
          </h3>
          <BrandChips items={byBrand(p.ads)} path="reel" />
        </div>
      )}

      {(p.brand_tags ?? []).length > 0 && (
        <div className="mt-6">
          <h3 className="font-semibold">Brands that tagged them from their own page</h3>
          <BrandChips items={byBrand(p.brand_tags ?? [])} path="p" />
        </div>
      )}
    </section>
  );
}
