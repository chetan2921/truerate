"use client";

import { useState } from "react";
import { Bar, BarChart, Cell, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import type { Report } from "@/lib/api";
import { compact, pct } from "@/lib/format";

const KIND_COLOR = { own: "var(--accent)", paid: "var(--negotiate)", collab: "var(--info)" } as const;
const KIND_LABEL = { own: "Own reel", paid: "Paid", collab: "Collab with a creator" } as const;
const METRICS = ["views", "likes", "comments", "followers"] as const;
type Metric = (typeof METRICS)[number];

const day = (iso: string) => new Date(iso).toLocaleDateString("en-IN", { day: "numeric", month: "short" });

export default function Placement({ r }: { r: Report }) {
  const [metric, setMetric] = useState<Metric>("views");
  const p = r.placement;
  const reels = [...p.reels].reverse().map((x) => ({ ...x, day: day(x.taken_at) }));
  const history = p.followers_history.map((h) => ({ ...h, day: day(h.at) }));
  const trend = p.trend == null ? null : p.trend >= 1 ? `up ${pct(p.trend - 1)}` : `down ${pct(1 - p.trend)}`;

  return (
    <section aria-labelledby="placement">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 id="placement" className="section-title">
          Placement performance
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
              <Tooltip formatter={(v) => compact(Number(v))} contentStyle={{ background: "var(--surface)", border: "none", borderRadius: 8 }} />
              <Line dataKey="followers" stroke="var(--accent)" strokeWidth={2} dot={{ r: 4, fill: "var(--accent)" }} isAnimationActive={false} />
            </LineChart>
          ) : (
            <BarChart data={reels} margin={{ top: 8, right: 8, bottom: 0, left: 0 }}>
              <XAxis dataKey="day" tick={{ fill: "var(--text-muted)", fontSize: 12 }} axisLine={{ stroke: "var(--line)" }} tickLine={false} interval="preserveStartEnd" minTickGap={24} />
              <YAxis tickFormatter={compact} tick={{ fill: "var(--text-muted)", fontSize: 12 }} axisLine={false} tickLine={false} width={48} />
              <Tooltip
                cursor={{ fill: "rgb(251 251 251 / 0.06)" }}
                contentStyle={{ background: "var(--surface)", border: "none", borderRadius: 8 }}
                formatter={(v, _n, item) => [compact(Number(v)), KIND_LABEL[(item.payload as (typeof reels)[number]).kind]]}
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
          <span>Instagram doesn&apos;t share follower history, so this builds from TrueRate&apos;s first snapshot ({history.length} so far).</span>
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
          <b>Consistency:</b> {p.hits_last_10} of the last 10 reels reached half the usual {compact(p.typical_views)} views. A weak reel gets about {compact(p.bad_reel_views)}.
        </li>
        {trend && (
          <li>
            <b>Trend:</b> the last 10 reels&apos; median views are {trend} on the 10 before.
          </li>
        )}
        <li>
          <b>Paid vs own:</b>{" "}
          {p.paid.n
            ? `${p.paid.n} paid reels keep ${pct(p.paid.ratio ?? 0)} of own-reel views; a typical WLDD creator's keep ${pct(p.paid.typical_ratio)}.`
            : `no paid reels in the last 30. A typical WLDD creator's paid reels keep ${pct(p.paid.typical_ratio)} of own-reel views.`}
        </li>
        <li>
          <b>Collab vs own:</b> {p.collab.n ? `${p.collab.n} posts co-authored with other creators get ${pct(p.collab.ratio ?? 0)} of own-reel views.` : "no posts co-authored with other creators."}
        </li>
      </ul>

      {p.ads.length > 0 && (
        <div className="mt-6">
          <h3 className="font-semibold">Ads found in the last 30 reels</h3>
          <ul className="mt-2 flex flex-wrap gap-2 text-sm">
            {p.ads.map((ad) => (
              <li key={ad.code} className="rounded-lg px-3 py-1 ring-1 ring-line">
                <a href={`https://www.instagram.com/reel/${ad.code}/`} target="_blank" rel="noreferrer">
                  {ad.brand ? `@${ad.brand}` : "Brand not named"}
                </a>
                <span className="basis"> · {day(ad.taken_at)} · {ad.disclosed ? "disclosed" : "not disclosed"}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </section>
  );
}
