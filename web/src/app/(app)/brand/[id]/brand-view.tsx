"use client";

import Link from "next/link";
import { use, useEffect, useState } from "react";

import BrandResult from "@/components/brand/result";
import RunProgress from "@/components/run-progress";
import { api, type BrandRun } from "@/lib/api";

export default function BrandView({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const [run, setRun] = useState<BrandRun | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    let stopped = false;
    let timer: ReturnType<typeof setTimeout>;
    const load = async () => {
      try {
        const next = await api.getBrandRun(id);
        if (stopped) return;
        setRun(next);
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

  if (error) return <Shell title="Couldn't load this brand">{<p className="mt-3">{error}</p>}</Shell>;
  if (!run) return <Shell title="Loading…" />;

  if (run.status === "running") {
    return (
      <Shell title={run.request.brand}>
        <p className="basis mt-2">Usually under a minute: the brand, then WLDD&apos;s creators and everyone analysed before.</p>
        <RunProgress steps={run.steps} step={run.step} createdAt={run.created_at} stepAt={run.step_at} usual={60} />
      </Shell>
    );
  }

  if (run.status === "failed" || !run.result) {
    return (
      <Shell title={`Couldn't finish ${run.request.brand}`}>
        <p className="mt-3 max-w-xl">{run.error ?? "The run stopped without a result."}</p>
        <Link href="/brand" className="btn btn-quiet mt-6 no-underline">
          Try another brand
        </Link>
      </Shell>
    );
  }

  return <BrandResult run={run} />;
}

function Shell({ title, children }: { title: string; children?: React.ReactNode }) {
  return (
    <main className="mx-auto max-w-6xl px-6 pb-24 pt-10">
      <h1 className="text-3xl font-bold">{title}</h1>
      {children}
    </main>
  );
}
