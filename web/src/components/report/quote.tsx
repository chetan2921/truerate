"use client";

import { useState } from "react";

import { api, type QuoteCheck } from "@/lib/api";
import { inr } from "@/lib/format";

const POSITION = { below: "text-go", within: "text-go", above: "text-avoid" } as const;

export default function QuoteChecker({ id, initial }: { id: string; initial: number | null }) {
  const [quote, setQuote] = useState(initial ? String(initial) : "");
  const [check, setCheck] = useState<QuoteCheck | null>(null);
  const [error, setError] = useState("");

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    if (!quote) return;
    setError("");
    try {
      setCheck(await api.checkQuote(id, Number(quote)));
    } catch (err) {
      setError((err as Error).message);
    }
  }

  return (
    <section aria-labelledby="quote" className="max-w-3xl">
      <h2 id="quote" className="section-title">
        Check a quote
      </h2>
      <form onSubmit={submit} className="mt-3 flex flex-wrap gap-2">
        <label htmlFor="quote-input" className="sr-only">
          The creator&apos;s quote in rupees
        </label>
        <input id="quote-input" className="field w-48" inputMode="numeric" placeholder="Their quote, ₹" value={quote}
          onChange={(e) => setQuote(e.target.value.replace(/\D/g, ""))} />
        <button type="submit" className="btn btn-quiet">
          Check
        </button>
      </form>
      {error && <p className="mt-2 text-avoid">{error}</p>}
      {check && (
        <div className="mt-4">
          <p className="text-lg">
            {inr(check.quote)} is <b className={POSITION[check.position]}>{check.position} the fair range</b>,{" "}
            {check.difference === 0 ? "exactly the recommended price" : `${inr(Math.abs(check.difference))} ${check.difference > 0 ? "above" : "below"} the recommended price`}.{" "}
            {check.counter_offer < check.quote ? `Counter at ${inr(check.counter_offer)}.` : "Take it."}
          </p>
          <ul className="mt-3 space-y-1.5">
            {check.talking_points.map((t) => (
              <li key={t} className="flex gap-3">
                <span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-muted" aria-hidden />
                <span>{t}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </section>
  );
}
