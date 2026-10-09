import { VERDICT_COLOR } from "@/components/chips";
import type { Report } from "@/lib/api";
import { pct } from "@/lib/format";

type Signals = Report["audience"]["signals"];
const two = (v: number) => v.toFixed(2);
const whole = (v: number) => String(Math.round(v));

// Every check, its family, how it reads and what it is based on (SPEC, Signals and why).
const CHECKS: { key: string; family: string; label: string; fmt: (v: number) => string; basis: (s: Signals) => string }[] = [
  { key: "fake_likers", family: "likes", label: "Fake-looking likers", fmt: (v) => pct(v), basis: (s) => `${s.n_likers ?? 0} likers checked` },
  { key: "likes_per_view", family: "likes", label: "Likes per view", fmt: (v) => pct(v, 1), basis: () => "own reels" },
  { key: "views_cv", family: "likes", label: "How much views vary between reels", fmt: two, basis: () => "last 30 reels" },
  { key: "likes_cv", family: "likes", label: "How much likes vary between reels", fmt: two, basis: () => "last 30 reels" },
  { key: "fake_followers", family: "followers", label: "Fake-looking newest followers", fmt: (v) => pct(v), basis: (s) => `${s.n_followers ?? 0} newest followers` },
  { key: "views_per_follower", family: "followers", label: "Views per follower", fmt: two, basis: () => "typical own reel" },
  { key: "generic_comments", family: "comments", label: "Generic or repeated comments", fmt: (v) => pct(v), basis: (s) => `${s.n_comments ?? 0} comments` },
  { key: "repeat_commenters", family: "comments", label: "Accounts on 60% or more of reels", fmt: whole, basis: () => "comments on 10 reels" },
  { key: "ring_size", family: "comments", label: "WLDD creators sharing 3+ commenters", fmt: whole, basis: () => "all WLDD creators" },
];
const FAMILIES = [
  { key: "likes", label: "Likes and views" },
  { key: "followers", label: "Followers" },
  { key: "comments", label: "Comments" },
];

export default function Authenticity({ r }: { r: Report }) {
  const a = r.audience;
  const flagged = new Set(a.flags.map((f) => f.signal));
  return (
    <section aria-labelledby="authenticity">
      <div className="flex flex-wrap items-baseline gap-x-4 gap-y-1">
        <h2 id="authenticity" className="section-title">
          Authenticity
        </h2>
        <span className="font-semibold" style={{ color: VERDICT_COLOR[a.verdict] }}>
          {a.verdict}
        </span>
        <span className="basis">
          {a.failed_families.length === 0 ? "All three check families pass" : `${a.failed_families.length} of 3 check families fail`}, compared with WLDD creators of the same follower band
        </span>
      </div>

      {a.flags.length > 0 && (
        <ul className="mt-4 space-y-1.5">
          {a.flags.map((f) => (
            <li key={f.signal} className="text-avoid">
              {f.text}
            </li>
          ))}
        </ul>
      )}
      {a.warnings.length > 0 && (
        <ul className="mt-2 space-y-1">
          {a.warnings.map((w) => (
            <li key={w} className="text-negotiate">
              {w}
            </li>
          ))}
        </ul>
      )}

      <div className="mt-5 overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="text-left text-muted">
            <tr>
              <th className="py-2 pr-3 font-normal">Check</th>
              <th className="py-2 pr-3 text-right font-normal">This creator</th>
              <th className="py-2 pr-3 text-right font-normal">Similar creators</th>
              <th className="py-2 pr-3 font-normal">Based on</th>
              <th className="py-2 font-normal">Result</th>
            </tr>
          </thead>
          {FAMILIES.map((fam) => (
            <tbody key={fam.key} className="divide-y divide-line">
              <tr>
                <th colSpan={5} scope="colgroup" className="pb-1 pt-4 text-left font-semibold">
                  {fam.label}
                  <span className={`ml-2 font-normal ${a.failed_families.includes(fam.key) ? "text-avoid" : "text-go"}`}>
                    {a.failed_families.includes(fam.key) ? "fails" : "passes"}
                  </span>
                </th>
              </tr>
              {CHECKS.filter((c) => c.family === fam.key).map((c) => {
                const value = a.signals[c.key];
                const median = a.medians[c.key];
                return (
                  <tr key={c.key}>
                    <td className="py-2 pr-3">{c.label}</td>
                    <td className="figure py-2 pr-3 text-right">{value == null ? "not measured" : c.fmt(value)}</td>
                    <td className="figure basis py-2 pr-3 text-right">{median == null ? "no norm yet" : c.fmt(median)}</td>
                    <td className="basis py-2 pr-3">{c.basis(a.signals)}</td>
                    <td className={`py-2 ${flagged.has(c.key) ? "text-avoid" : "text-muted"}`}>{flagged.has(c.key) ? "Red flag" : "Normal"}</td>
                  </tr>
                );
              })}
            </tbody>
          ))}
        </table>
      </div>
    </section>
  );
}
