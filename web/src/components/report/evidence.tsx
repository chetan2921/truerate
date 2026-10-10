"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import { api, type Report } from "@/lib/api";
import { compact, inr } from "@/lib/format";

export default function Evidence({ r }: { r: Report }) {
  const router = useRouter();
  const [starting, setStarting] = useState("");

  async function analyse(handle: string) {
    setStarting(handle);
    try {
      const { id } = await api.createAnalysis({ handle });
      router.push(`/analyses/${id}`);
    } catch {
      setStarting("");
    }
  }

  return (
    <section aria-labelledby="evidence" className="grid gap-10 lg:grid-cols-[minmax(0,3fr)_minmax(0,2fr)]">
      <div>
        <h2 id="evidence" className="section-title">
          Fair price evidence
        </h2>
        <h3 className="mt-4 font-semibold">Cheaper {r.category} creators WLDD has booked</h3>
        {r.cheaper.length === 0 ? (
          <p className="basis mt-2">None in this category delivers cheaper views at a similar reach.</p>
        ) : (
          <table className="mt-2 w-full text-sm">
            <thead className="text-left text-muted">
              <tr>
                <th className="py-2 pr-3 font-normal">Creator</th>
                <th className="py-2 pr-3 text-right font-normal">Typical views</th>
                <th className="py-2 pr-3 text-right font-normal">Per 1,000 views</th>
                <th className="py-2 text-right font-normal">WLDD paid</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-line">
              {r.cheaper.map((c) => (
                <tr key={c.handle}>
                  <td className="py-2 pr-3">@{c.handle}</td>
                  <td className="figure py-2 pr-3 text-right">{compact(c.views)}</td>
                  <td className="figure py-2 pr-3 text-right">{inr(c.per_1k_views)}</td>
                  <td className="figure py-2 text-right">{inr(c.price)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
        <p className="basis mt-2">This creator: {inr(r.price.delivery.cost_per_1k)} per 1,000 typical views at the middle of the fair range.</p>
      </div>

      <div className="lg:pt-9">
        <h3 className="font-semibold">Instagram suggests these accounts too</h3>
        {r.suggested.length === 0 ? (
          <p className="basis mt-2">Instagram showed no suggestions for this account.</p>
        ) : (
          <ul className="mt-2 flex flex-wrap gap-2">
            {r.suggested.map((h) => (
              <li key={h}>
                <button type="button" className="btn btn-quiet px-3 py-1.5 text-sm font-normal" disabled={Boolean(starting)} onClick={() => analyse(h)}>
                  {starting === h ? "Starting…" : `Price @${h}`}
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>
    </section>
  );
}
