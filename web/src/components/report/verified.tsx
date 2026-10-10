"use client";

import { useState } from "react";

import type { Report } from "@/lib/api";
import { compact, pct } from "@/lib/format";

// What the creator shared through Phyllo, or the link to ask them for it.
export default function VerifiedPanel({ r }: { r: Report }) {
  const v = r.verified;
  const [copied, setCopied] = useState<"" | "yes" | "no">("");
  if (!v) {
    const link = typeof window === "undefined" ? `/connect/${r.handle}` : `${window.location.origin}/connect/${r.handle}`;
    return (
      <div className="mt-8 rounded-xl p-5 ring-1 ring-line">
        <p className="font-semibold">Not verified by the creator yet</p>
        <p className="basis mt-1">Send them this link to share their real reach and audience through Phyllo.</p>
        <p className="mt-2 select-all break-all text-sm">{link}</p>
        <button
          type="button"
          className="btn btn-quiet mt-3 py-1.5 text-sm"
          onClick={() =>
            // The clipboard is blocked outside HTTPS and in some browsers; the link above can still be copied by hand.
            Promise.resolve()
              .then(() => navigator.clipboard.writeText(link))
              .then(() => setCopied("yes"))
              .catch(() => setCopied("no"))
          }
        >
          {copied === "yes" ? "Link copied" : copied === "no" ? "Copy blocked: select the link above" : "Copy verification link"}
        </button>
      </div>
    );
  }
  const typical = r.placement.typical_views;
  return (
    <div className="mt-8 rounded-xl p-5 ring-1 ring-go/40">
      <p className="font-semibold text-go">Verified by @{v.username || r.handle} through Phyllo</p>
      {v.username && v.username.toLowerCase() !== r.handle && (
        <p className="mt-1 text-negotiate">The connected account is not @{r.handle}. Check with the creator before trusting these numbers.</p>
      )}
      <ul className="mt-3 space-y-1.5">
        {v.followers != null && <li>{compact(v.followers)} followers, from Instagram itself.</li>}
        {v.median_reach != null && (
          <li>
            Median reach {compact(v.median_reach)} per post across {v.posts} posts
            {v.reach_per_follower != null ? ` (${v.reach_per_follower.toFixed(2)} per follower)` : ""}; public typical views {compact(typical)}.
          </li>
        )}
        {v.countries.length > 0 && <li>Audience: {v.countries.map((c) => `${pct(c.share)} ${c.code}`).join(", ")}{v.india_share ? `; India ${pct(v.india_share)}` : ""}.</li>}
        {v.cities.length > 0 && <li>Top cities: {v.cities.map((c) => `${c.name} ${pct(c.share)}`).join(", ")}.</li>}
        {v.gender_age.length > 0 && <li>Age and gender: {v.gender_age.slice(0, 4).map((g) => `${g.gender.toLowerCase()} ${g.age_range} ${pct(g.share)}`).join(", ")}.</li>}
      </ul>
    </div>
  );
}
