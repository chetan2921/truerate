import { Suspense } from "react";

import BrandView from "./brand-view";

// cacheComponents: params are request data, so they're read inside Suspense.
export default function BrandResultPage({ params }: PageProps<"/brand/[id]">) {
  return (
    <Suspense fallback={<main className="mx-auto max-w-6xl px-6 pt-10 text-3xl font-bold">Loading…</main>}>
      <BrandView params={params} />
    </Suspense>
  );
}
