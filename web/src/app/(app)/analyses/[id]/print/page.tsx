import { Suspense } from "react";

import PrintView from "./print-view";

export default function PrintPage({ params }: PageProps<"/analyses/[id]/print">) {
  return (
    <Suspense fallback={<main className="mx-auto max-w-3xl px-6 pt-10">Loading…</main>}>
      <PrintView params={params} />
    </Suspense>
  );
}
