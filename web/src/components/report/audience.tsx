import type { Report } from "@/lib/api";
import { pct } from "@/lib/format";

export default function Audience({ r }: { r: Report }) {
  const mix = r.audience.mix;
  const parts = [
    { key: "people", label: "people", n: mix.people, color: "var(--info)" },
    { key: "creators", label: "creators", n: mix.creators, color: "rgb(151 186 255 / 0.6)" },
    { key: "brands", label: "brands", n: mix.brands, color: "var(--negotiate)" },
    { key: "fake", label: "fake-looking", n: mix.fake, color: "var(--avoid)" },
  ];
  const languages = mix.languages.slice(0, 4);
  const topics = Object.entries(r.niche.topics).sort((a, b) => b[1] - a[1]);

  return (
    <section aria-labelledby="audience" className="grid gap-10 lg:grid-cols-2">
      <div>
        <h2 id="audience" className="section-title">
          Audience and niche
        </h2>
        <p className="mt-3">
          Of the {mix.top} most active commenters: {parts.filter((x) => x.n).map((x) => `${x.n} ${x.label}`).join(", ")}.
        </p>
        <div className="mt-3 flex h-3 overflow-hidden rounded" role="img" aria-label="Top commenters by kind">
          {parts.map((x) => (x.n ? <span key={x.key} style={{ width: `${(100 * x.n) / Math.max(mix.top, 1)}%`, background: x.color }} /> : null))}
        </div>
        <p className="basis mt-2">Fake-looking by the account model; creators are verified or labelled by Gemini; brands are labelled by Gemini.</p>
        {languages.length > 0 && (
          <p className="mt-5">Comments are {languages.map((l) => `${pct(l.share)} ${l.language}`).join(", ")}.</p>
        )}
      </div>

      <div className="lg:pt-9">
        <p>
          <b>Niche:</b> {r.category}
          <span className="basis"> ({r.category_source === "wldd" ? "from WLDD's records" : "from the bio and captions"})</span>
        </p>
        {topics.length > 0 && <p className="basis mt-1">Reel topics: {topics.map(([t, n]) => `${t} ${n}`).join(" · ")}</p>}
        <p className="mt-5 text-lg">{r.worth_reaching}</p>
        {r.competitor && (
          <p className="mt-4 text-avoid">
            Competitor conflict: promoted {r.competitor.brand ? `@${r.competitor.brand}` : "a brand"} in {r.niche.product} {r.competitor.days} days ago.
          </p>
        )}
      </div>
    </section>
  );
}
