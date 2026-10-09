"use client";

import { Copy } from "lucide-react";
import { useState } from "react";

import type { Report } from "@/lib/api";
import { inr } from "@/lib/format";

export default function Negotiation({ r }: { r: Report }) {
  const n = r.negotiation;
  const [copied, setCopied] = useState(false);
  const summary = `Open at ${inr(n.start)}, aim for ${inr(n.target)}, walk away above ${inr(n.walk_away)}.`;

  async function copy() {
    await navigator.clipboard.writeText([`@${r.handle}: ${summary}`, ...n.lines.map((l) => `- ${l}`)].join("\n"));
    setCopied(true);
    setTimeout(() => setCopied(false), 1800);
  }

  return (
    <section aria-labelledby="negotiation" className="panel p-6 sm:p-8">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 id="negotiation" className="section-title">
          Negotiation lines
        </h2>
        <button type="button" className="btn btn-quiet py-1.5 text-sm" onClick={copy}>
          <Copy size={16} aria-hidden />
          {copied ? "Copied" : "Copy lines"}
        </button>
      </div>
      <p className="figure mt-3 text-lg">{summary}</p>
      <ul className="mt-4 space-y-2">
        {n.lines.map((l) => (
          <li key={l} className="flex gap-3">
            <span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-muted" aria-hidden />
            <span>{l}</span>
          </li>
        ))}
      </ul>
    </section>
  );
}
