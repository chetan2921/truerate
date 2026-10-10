import { Suspense } from "react";

import ConnectView from "./connect-view";

export default function ConnectPage({ params }: PageProps<"/connect/[handle]">) {
  return (
    <Suspense fallback={<main className="mx-auto max-w-lg px-6 pt-16">Loading…</main>}>
      <ConnectView params={params} />
    </Suspense>
  );
}
