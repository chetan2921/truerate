"use client";

import { useEffect, useState } from "react";

import ProductOptions from "@/components/product-options";
import { api, type Meta, type RateCard } from "@/lib/api";
import { compact, inr } from "@/lib/format";

// The specific categories priced with this WLDD category.
function Includes({ products, category }: { products: Meta["products"]; category: string }) {
  const names = products.filter((p) => p.category === category).map((p) => p.name);
  return names.length ? <span className="basis mt-1 block max-w-56 text-xs leading-snug">{names.join(" · ")}</span> : null;
}

export default function RateCardPage() {
  const [card, setCard] = useState<RateCard | null>(null);
  const [error, setError] = useState("");
  const [meta, setMeta] = useState<Meta | null>(null);
  const [product, setProduct] = useState("");
  const [views, setViews] = useState("50000");

  useEffect(() => {
    api.rateCard().then(setCard).catch((e) => setError((e as Error).message));
    api.meta().then((m) => {
      setMeta(m);
      setProduct(m.products[0]?.name ?? "");
    }).catch((e) => setError((e as Error).message));
  }, []);

  // Products are priced with the WLDD category they sit in, the only level WLDD's deals cover.
  const category = meta?.products.find((p) => p.name === product)?.category ?? "";
  const rate = card?.categories.find((c) => c.category === category);
  const wanted = Number(views) || 0;
  const max = Math.max(...(card?.categories.map((c) => c.per_1k.p75) ?? [1]));

  return (
    <main className="mx-auto max-w-6xl px-6 pb-24 pt-[min(6vh,3rem)]">
      <h1 className="text-3xl font-bold">What views cost, by category</h1>
      <p className="basis mt-2 max-w-2xl">From WLDD&apos;s past deals: the price paid divided by the creator&apos;s typical reel views.</p>
      {error && <p className="mt-6 text-avoid">{error}</p>}
      {card && meta && (
        <>
          <section aria-labelledby="calc" className="panel mt-8 max-w-4xl p-6 sm:p-8">
            <h2 id="calc" className="section-title">
              Budget calculator
            </h2>
            <div className="mt-4 flex flex-wrap gap-3">
              <label className="basis flex flex-col gap-1">
                Category
                <select className="field text-text" value={product} onChange={(e) => setProduct(e.target.value)}>
                  <ProductOptions products={meta.products} categories={meta.categories} />
                </select>
              </label>
              <label className="basis flex flex-col gap-1">
                Views wanted
                <input className="field w-40" inputMode="numeric" value={views} onChange={(e) => setViews(e.target.value.replace(/\D/g, ""))} />
              </label>
            </div>
            {rate ? (
              <>
                <p className="figure mt-6 font-bold leading-none" style={{ fontSize: "clamp(2rem, min(4.5vw, 9vh), 3.5rem)" }}>
                  {inr((wanted / 1000) * rate.per_1k.p25)} to {inr((wanted / 1000) * rate.per_1k.p75)}
                </p>
                <p className="mt-3">
                  About {inr((wanted / 1000) * rate.per_1k.median)} at the {category} median of {inr(rate.per_1k.median)} per 1,000 views. Based on {rate.n} WLDD deals; the range is
                  their middle half.{product !== category && ` ${product} is priced with ${category} deals, the WLDD category it belongs to.`}
                </p>
              </>
            ) : (
              <p className="mt-6 text-lg">WLDD has fewer than 3 {category} deals, so there is no rate for {product} yet.</p>
            )}
          </section>

          <section aria-labelledby="rates" className="mt-14 max-w-4xl">
            <h2 id="rates" className="section-title">
              All categories
            </h2>
            <div className="mt-3 overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="text-left text-muted">
                  <tr>
                    <th className="py-2 pr-3 font-normal">Category</th>
                    <th className="py-2 pr-3 font-normal">Per 1,000 views, middle half of deals</th>
                    <th className="py-2 pr-3 text-right font-normal">Typical reel</th>
                    <th className="py-2 pr-3 text-right font-normal">Typical views</th>
                    <th className="py-2 text-right font-normal">Deals</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-line">
                  {card.categories.map((c) => (
                    <tr key={c.category}>
                      <td className="py-2.5 pr-3 align-top">
                        {c.category}
                        <Includes products={meta.products} category={c.category} />
                      </td>
                      <td className="py-2.5 pr-3">
                        <div className="flex items-center gap-3">
                          <span className="relative h-2 w-40 shrink-0 rounded bg-line" aria-hidden>
                            <span className="absolute top-0 h-2 rounded bg-info" style={{ left: `${(100 * c.per_1k.p25) / max}%`, width: `${(100 * (c.per_1k.p75 - c.per_1k.p25)) / max}%` }} />
                            <span className="absolute -top-0.5 h-3 w-0.5 bg-accent" style={{ left: `${(100 * c.per_1k.median) / max}%` }} />
                          </span>
                          <span className="figure whitespace-nowrap">
                            {inr(c.per_1k.p25)} to {inr(c.per_1k.p75)}
                          </span>
                        </div>
                      </td>
                      <td className="figure py-2.5 pr-3 text-right">{inr(c.typical_price)}</td>
                      <td className="figure py-2.5 pr-3 text-right">{compact(c.typical_views)}</td>
                      <td className="figure py-2.5 text-right">{c.n}</td>
                    </tr>
                  ))}
                  {(card.thin ?? []).map((c) => (
                    <tr key={c.category}>
                      <td className="py-2.5 pr-3 align-top">
                        {c.category}
                        <Includes products={meta.products} category={c.category} />
                      </td>
                      <td colSpan={3} className="basis py-2.5 pr-3 align-top">
                        Not enough WLDD deals for a rate yet: {c.n === 0 ? "none" : c.n} so far, 3 needed.
                      </td>
                      <td className="figure py-2.5 text-right align-top">{c.n}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <p className="basis mt-2">
              The lime tick is each category&apos;s median. Each specific category is priced with the WLDD category it sits under, the only level WLDD&apos;s deals cover. One or two deals are not a rate, so those categories show no numbers yet.
            </p>
          </section>
        </>
      )}
    </main>
  );
}
