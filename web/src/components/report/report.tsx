import type { Analysis, Report } from "@/lib/api";
import { compact, daysAgo } from "@/lib/format";

import Audience from "./audience";
import Authenticity from "./authenticity";
import Decision from "./decision";
import Engagement from "./engagement";
import Evidence from "./evidence";
import Negotiation from "./negotiation";
import Placement from "./placement";
import Waterfall from "./waterfall";

export default function ReportView({ report: r, inputs }: { report: Report; inputs: Analysis["inputs"] }) {
  const asked = [inputs.category && `for ${inputs.category}`, inputs.quote && `quote ₹${inputs.quote.toLocaleString("en-IN")}`, inputs.budget && `budget ₹${inputs.budget.toLocaleString("en-IN")}`].filter(Boolean);
  return (
    <main className="mx-auto max-w-6xl px-6 pb-24 pt-4">
      <div className="flex flex-wrap items-baseline gap-x-3 gap-y-1">
        <h1 className="text-3xl font-bold">@{r.handle}</h1>
        <span className="basis">
          {r.profile.full_name} · {compact(r.profile.followers)} followers · {r.category} · data from {daysAgo(r.fetched_at)}
          {asked.length > 0 && ` · ${asked.join(", ")}`}
        </span>
      </div>

      <div className="mt-5">
        <Decision r={r} />
      </div>
      {/* Gaps follow weight: loose after the dense table and the chart, tight around the one-line engagement block. */}
      <div className="[&>section]:pt-12">
        <Waterfall r={r} />
      </div>
      <div className="[&>section]:pt-16">
        <Authenticity r={r} />
      </div>
      <div className="[&>section]:pt-10">
        <Engagement r={r} />
      </div>
      <div className="[&>section]:pt-14">
        <Placement r={r} />
      </div>
      <div className="[&>section]:pt-16">
        <Audience r={r} />
      </div>
      <div className="[&>section]:pt-12">
        <Evidence r={r} />
      </div>
      <div className="mt-12">
        <Negotiation r={r} />
      </div>
    </main>
  );
}
