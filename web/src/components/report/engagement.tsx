import type { Report } from "@/lib/api";
import { pct } from "@/lib/format";

const BAND_LABEL: Record<string, string> = { small: "under 20K followers", medium: "20K to 100K followers", big: "100K+ followers" };

export default function Engagement({ r }: { r: Report }) {
  const e = r.engagement;
  return (
    <section aria-labelledby="engagement" className="max-w-3xl">
      <h2 id="engagement" className="section-title">
        Engagement
      </h2>
      <p className="mt-3">
        <b className="figure text-2xl">{pct(e.rate, 1)}</b> of viewers like or comment on an own reel.
        {e.percentile != null && e.band_median != null && (
          <>
            {" "}
            That beats {e.percentile}% of WLDD creators with {BAND_LABEL[e.band]} (their median: {pct(e.band_median, 1)}).
          </>
        )}
      </p>
      {e.percentile != null && (
        <div className="relative mt-4 h-2 rounded bg-line" role="img" aria-label={`Percentile ${e.percentile} of 100 among similar WLDD creators`}>
          <span className="absolute left-0 top-0 h-2 rounded bg-accent" style={{ width: `${e.percentile}%` }} />
          <span className="absolute -top-1 h-4 w-0.5 bg-info" style={{ left: "50%" }} title="Median of similar creators" />
        </div>
      )}
      <p className="basis mt-2">Lime is this creator; the blue tick is the similar-creator median.</p>
    </section>
  );
}
