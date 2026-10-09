import { Suspense } from "react";

import AnalysisView from "./analysis-view";

// cacheComponents: params are request data, so they're read inside Suspense.
export default function AnalysisPage({ params }: PageProps<"/analyses/[id]">) {
  return (
    <Suspense fallback={<main className="mx-auto max-w-6xl px-6 pt-10 text-3xl font-bold">Loading…</main>}>
      <AnalysisView params={params} />
    </Suspense>
  );
}
