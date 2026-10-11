"use client";

import { Check } from "lucide-react";
import { useEffect, useState } from "react";

// The API stores UTC without a zone marker; without the "Z" a browser in India would read it 5.5 hours off.
const utc = (at: string) => new Date(/[zZ]$|[+-]\d\d:?\d\d$/.test(at) ? at : `${at}Z`).getTime();

const CIRCLE = 2 * Math.PI * 9;

const clock = (seconds: number) => `${Math.floor(seconds / 60)}:${String(seconds % 60).padStart(2, "0")}`;

// The steps of a running job, each with how long it took (live for the step under way, from when the API began it), and a
// small timer on the right whose ring fills over `usual` seconds and stays full if the run takes longer.
export default function RunProgress({ steps, step, createdAt, stepAt, usual }: {
  steps: string[];
  step: number;
  createdAt: string;
  stepAt?: string[];
  usual: number;
}) {
  const [now, setNow] = useState(() => Date.now());
  useEffect(() => {
    const t = setInterval(() => setNow(Date.now()), 1000);
    return () => clearInterval(t);
  }, []);
  const started = stepAt?.map(utc) ?? [];
  const seconds = Math.max(0, Math.round((now - utc(createdAt)) / 1000));
  const took = (i: number) => (started[i] === undefined ? null : ((started[i + 1] ?? now) - started[i]) / 1000);

  return (
    <div className="mt-8 grid items-start gap-x-12 gap-y-8 lg:grid-cols-[minmax(0,28rem)_1fr]">
      <ol className="space-y-4">
        {steps.map((label, i) => {
          const state = i < step ? "done" : i === step ? "current" : "next";
          const t = state === "next" ? null : took(i);
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
              {t !== null && (
                <span className={`figure ${state === "done" ? "basis" : "text-text"}`} aria-hidden={state === "current"}>
                  {state === "done" ? `${t.toFixed(1)} s` : `${Math.floor(t)} s`}
                </span>
              )}
            </li>
          );
        })}
      </ol>
      <div className="flex items-center gap-2.5 lg:justify-self-end" role="timer" aria-label="Time running">
        <svg width="22" height="22" viewBox="0 0 22 22" className="-rotate-90" aria-hidden>
          <circle cx="11" cy="11" r="9" fill="none" stroke="var(--line)" strokeWidth="2.5" />
          <circle cx="11" cy="11" r="9" fill="none" stroke="var(--accent)" strokeWidth="2.5" strokeLinecap="round" strokeDasharray={CIRCLE}
            strokeDashoffset={CIRCLE * (1 - Math.min(seconds / usual, 1))} style={{ transition: "stroke-dashoffset 1s linear" }} />
        </svg>
        <span className="figure text-lg">{clock(seconds)}</span>
      </div>
    </div>
  );
}
