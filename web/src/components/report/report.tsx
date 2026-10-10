import { Download } from "lucide-react";
import Link from "next/link";

import type { Analysis, Output, Report } from "@/lib/api";
import { compact, daysAgo } from "@/lib/format";

import Audience from "./audience";
import Authenticity from "./authenticity";
import Decision from "./decision";
import Engagement from "./engagement";
import { CheaperCreators, Suggestions } from "./evidence";
import Negotiation from "./negotiation";
import Placement from "./placement";
import QuoteChecker from "./quote";
import ReportTabs from "./tabs";
import Waterfall from "./waterfall";

export default function ReportView({ id, report: r, inputs, outputs }: { id: string; report: Report; inputs: Analysis["inputs"]; outputs: Output[] }) {
  const asked = [inputs.category && `for ${inputs.category}`, inputs.quote && `quote ₹${inputs.quote.toLocaleString("en-IN")}`, inputs.budget && `budget ₹${inputs.budget.toLocaleString("en-IN")}`].filter(Boolean);
  return (
    <main className="mx-auto max-w-6xl px-6 pb-24 pt-4">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div className="flex flex-wrap items-baseline gap-x-3 gap-y-1">
          <h1 className="text-3xl font-bold">@{r.handle}</h1>
          <span className="basis">
            {r.profile.full_name} · {compact(r.profile.followers)} followers · {r.category} · data from {daysAgo(r.fetched_at)}
            {asked.length > 0 && ` · ${asked.join(", ")}`}
          </span>
        </div>
        <Link href={`/analyses/${id}/print`} className="basis inline-flex items-center gap-1.5 rounded-lg px-2 py-1 no-underline hover:text-text">
          <Download size={15} aria-hidden />
          Client one-pager
        </Link>
      </div>

      {/* Inside each tab, gaps follow weight: loose after a dense table or the chart, tight around one-line blocks. */}
      <ReportTabs
        panels={{
          summary: (
            <>
              <Decision r={r} outputs={outputs} />
              <div className="mt-12">
                <Negotiation r={r} />
              </div>
            </>
          ),
          price: (
            <>
              <Waterfall r={r} />
              <div className="[&>section]:pt-12">
                <QuoteChecker id={id} initial={inputs.quote ?? null} />
              </div>
              <div className="[&>section]:pt-16">
                <CheaperCreators r={r} />
              </div>
            </>
          ),
          audience: (
            <>
              <Authenticity r={r} />
              <div className="[&>section]:pt-10">
                <Engagement r={r} />
              </div>
              <div className="[&>section]:pt-14">
                <Audience r={r} />
              </div>
            </>
          ),
          content: <Placement r={r} />,
          similar: <Suggestions r={r} />,
        }}
      />
    </main>
  );
}
