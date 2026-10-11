"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { use, useEffect, useState } from "react";

import ReportView from "@/components/report/report";
import RunProgress from "@/components/run-progress";
import { api, type Analysis } from "@/lib/api";

export default function AnalysisView({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const router = useRouter();
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [error, setError] = useState("");
  const [retrying, setRetrying] = useState(false);

  useEffect(() => {
    let stopped = false;
    let timer: ReturnType<typeof setTimeout>;
    const load = async () => {
      try {
        const next = await api.getAnalysis(id);
        if (stopped) return;
        setAnalysis(next);
        if (next.status === "running") timer = setTimeout(load, 1500);
      } catch (e) {
        if (!stopped) setError((e as Error).message);
      }
    };
    load();
    return () => {
      stopped = true;
      clearTimeout(timer);
    };
  }, [id]);

  async function retry() {
    if (!analysis) return;
    setRetrying(true);
    try {
      const { id: next } = await api.createAnalysis({ handle: analysis.handle, ...analysis.inputs });
      router.push(`/analyses/${next}`);
    } catch (e) {
      setError((e as Error).message);
      setRetrying(false);
    }
  }

  if (error) {
    return (
      <Shell title="Couldn't load this analysis">
        <p className="mt-3">{error}</p>
        <button type="button" className="btn btn-primary mt-6" onClick={() => location.reload()}>
          Retry
        </button>
      </Shell>
    );
  }
  if (!analysis) return <Shell title="Loading…" />;

  if (analysis.status === "running") {
    return (
      <Shell title={`@${analysis.handle}`}>
        <p className="basis mt-2">Usually about 45 seconds. Instagram data, then the checks, then the price.</p>
        <RunProgress steps={analysis.steps} step={analysis.step} createdAt={analysis.created_at} stepAt={analysis.step_at} usual={45} />
      </Shell>
    );
  }

  if (analysis.status === "out_of_scope") {
    return (
      <Shell title={`@${analysis.handle} is out of scope`}>
        <p className="mt-3 max-w-xl">{analysis.reason}</p>
        <Link href="/" className="btn btn-quiet mt-6 no-underline">
          Price another creator
        </Link>
      </Shell>
    );
  }

  if (analysis.status === "failed" || !analysis.result) {
    return (
      <Shell title={`Couldn't finish @${analysis.handle}`}>
        <p className="mt-3 max-w-xl">{analysis.error ?? "The analysis stopped without a result."}</p>
        <button type="button" className="btn btn-primary mt-6" onClick={retry} disabled={retrying}>
          {retrying ? "Starting…" : "Retry"}
        </button>
      </Shell>
    );
  }

  return <ReportView id={id} report={analysis.result} inputs={analysis.inputs} outputs={analysis.outputs ?? []} paid={analysis.wldd_paid ?? null} />;
}

function Shell({ title, children }: { title: string; children?: React.ReactNode }) {
  return (
    <main className="mx-auto max-w-6xl px-6 pb-24 pt-10">
      <h1 className="text-3xl font-bold">{title}</h1>
      {children}
    </main>
  );
}
