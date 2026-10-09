import { Suspense } from "react";

import BatchView from "./batch-view";

export default function BatchResultPage({ params }: PageProps<"/batch/[id]">) {
  return (
    <Suspense fallback={<main className="mx-auto max-w-6xl px-6 pt-10 text-3xl font-bold">Loading…</main>}>
      <BatchView params={params} />
    </Suspense>
  );
}
