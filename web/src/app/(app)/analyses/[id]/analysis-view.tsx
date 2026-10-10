"use client";

import { Check } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { use, useEffect, useState } from "react";

import ReportView from "@/components/report/report";
import { api, type Analysis } from "@/lib/api";

// The API stores UTC without a zone marker; without the "Z" a browser in India would read it 5.5 hours off.
function Elapsed({ since }: { since: string }) {
  const start = new Date(/[zZ]$|[+-]\d\d:?\d\d$/.test(since) ? since : `${since}Z`).getTime();
  const [now, setNow] = useState(() => Date.now());
  useEffect(() => {
    const t = setInterval(() => setNow(Date.now()), 1000);
    return () => clearInterval(t);
  }, []);
  const seconds = Math.max(0, Math.round((now - start) / 1000));
  return (
    <span className="figure text-text">
      {Math.floor(seconds / 60)}:{String(seconds % 60).padStart(2, "0")}
    </span>
  );
}

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
        <p className="basis mt-2">
          Running for <Elapsed since={analysis.created_at} />. Usually about 35 seconds for a creator seen for the first time, about 25 for one seen before. Instagram
          data, then the checks, then the price.
        </p>
        <ol className="mt-8 max-w-md space-y-4" aria-live="polite">
          {analysis.steps.map((label, i) => {
            const state = i < analysis.step ? "done" : i === analysis.step ? "current" : "next";
            return (
              <li key={label} className="flex items-center gap-3">
                <span className="flex h-5 w-5 items-center justify-center">
                  {state === "done" ? <Check size={18} className="text-go" aria-label="Done" /> : <span className={`h-2 w-2 rounded-full ${state === "current" ? "bg-accent" : "bg-line"}`} />}
                </span>
                <span className={`flex-1 ${state === "next" ? "text-muted" : ""}`}>
                  {label}
                  {state === "current" && (
                    <span className="mt-2 block h-0.5 overflow-hidden rounded bg-line" aria-hidden>
                      <span className="step-bar block h-full w-2/5 bg-accent" />
                    </span>
                  )}
                </span>
              </li>
            );
          })}
        </ol>
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

  return <ReportView id={id} report={analysis.result} inputs={analysis.inputs} outputs={analysis.outputs ?? []} />;
}

function Shell({ title, children }: { title: string; children?: React.ReactNode }) {
  return (
    <main className="mx-auto max-w-6xl px-6 pb-24 pt-10">
      <h1 className="text-3xl font-bold">{title}</h1>
      {children}
    </main>
  );
}
