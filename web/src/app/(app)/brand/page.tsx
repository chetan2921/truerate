"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useLayoutEffect, useState } from "react";

import ProductOptions from "@/components/product-options";
import { api, type BrandSummary, type Meta } from "@/lib/api";
import { daysAgo } from "@/lib/format";

export default function BrandPage() {
  const router = useRouter();
  const [brand, setBrand] = useState("");
  const [product, setProduct] = useState("");
  const [budget, setBudget] = useState("");
  const [meta, setMeta] = useState<Meta | null>(null);
  const [recent, setRecent] = useState<BrandSummary[] | null>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    api.meta().then(setMeta).catch(() => setMeta(null));
  }, []);

  // Runs again each time this page is shown, so a run started a moment ago is listed.
  useEffect(() => {
    api.listBrandRuns().then(setRecent).catch(() => setRecent([]));
  }, []);

  // Next keeps this page alive, hidden, while a run is open; coming back shows a fresh form, not "Starting…".
  useLayoutEffect(
    () => () => {
      setBusy(false);
      setBrand("");
    },
    [],
  );

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    if (!brand.trim()) return;
    setBusy(true);
    setError("");
    try {
      const { id } = await api.createBrandRun({ brand, product: product || null, budget: budget ? Number(budget) : null, count: 10 });
      router.push(`/brand/${id}`);
    } catch (err) {
      setError((err as Error).message);
      setBusy(false);
    }
  }

  return (
    <main className="mx-auto max-w-6xl px-6 pb-24 pt-[min(6vh,3rem)]">
      <h1 className="text-3xl font-bold">Find creators for a brand</h1>
      <p className="basis mt-2 max-w-2xl">
        Give the brand&apos;s Instagram handle, website or name. TruRate reads what it sells and to whom, then ranks WLDD&apos;s creators, everyone analysed
        before, and the creators already seen with the brand.
      </p>
      <form onSubmit={submit} className="mt-6 grid max-w-4xl items-end gap-4 lg:grid-cols-[minmax(0,3fr)_minmax(0,2fr)_minmax(0,1.3fr)_auto]">
        <label className="basis flex flex-col gap-1">
          Brand
          <input className="field text-text" placeholder="@brand, brand.com or a name" value={brand} onChange={(e) => setBrand(e.target.value)} autoFocus autoComplete="off" spellCheck={false} />
        </label>
        <label className="basis flex flex-col gap-1">
          Product, optional
          <select className="field text-sm text-text" value={product} onChange={(e) => setProduct(e.target.value)}>
            <option value="">What the brand sells</option>
            {meta && <ProductOptions products={meta.products} categories={meta.categories} />}
          </select>
        </label>
        <label className="basis flex flex-col gap-1">
          Budget in ₹, optional
          <input className="field text-sm" inputMode="numeric" placeholder="200000" value={budget} onChange={(e) => setBudget(e.target.value.replace(/\D/g, ""))} />
        </label>
        <button type="submit" className="btn btn-primary justify-center" disabled={busy || !brand.trim()}>
          {busy ? "Starting…" : "Find creators"}
        </button>
      </form>
      {error && (
        <p role="alert" className="mt-3 text-avoid">
          {error}
        </p>
      )}

      {recent && recent.length > 0 && (
        <section aria-labelledby="recent-brands" className="mt-16 max-w-4xl">
          <h2 id="recent-brands" className="section-title">
            Recent brands
          </h2>
          <ul className="mt-3 divide-y divide-line">
            {recent.map((b) => (
              <li key={b.id}>
                <Link href={`/brand/${b.id}`} className="grid grid-cols-[1fr_auto_6rem] items-center gap-6 py-3 no-underline hover:bg-surface">
                  <span className="truncate">
                    {b.name ?? b.brand}
                    {b.name && <span className="basis"> · {b.brand}</span>}
                  </span>
                  <span className={`text-sm ${b.status === "failed" ? "text-avoid" : b.status === "running" ? "text-text" : "text-muted"}`}>
                    {b.status === "running" ? "Running" : b.status === "failed" ? "Failed" : "Done"}
                  </span>
                  <span className="basis text-right">{daysAgo(b.created_at)}</span>
                </Link>
              </li>
            ))}
          </ul>
        </section>
      )}
    </main>
  );
}
