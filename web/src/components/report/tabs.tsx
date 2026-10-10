"use client";

import { useEffect, useRef, useState } from "react";

const TABS = [
  { key: "summary", label: "Summary" },
  { key: "price", label: "Price" },
  { key: "audience", label: "Audience" },
  { key: "content", label: "Content" },
  { key: "similar", label: "Similar" },
] as const;

export type TabKey = (typeof TABS)[number]["key"];

// The open tab lives in the URL hash, so a shared link can open the report on Price or Audience.
function fromHash(): TabKey {
  const key = location.hash.slice(1);
  return TABS.find((t) => t.key === key)?.key ?? "summary";
}

export default function ReportTabs({ panels }: { panels: Record<TabKey, React.ReactNode> }) {
  const [active, setActive] = useState(fromHash);
  // A panel mounts the first time it opens and then stays, so a quote check survives a look at another tab.
  const [opened, setOpened] = useState(() => new Set<TabKey>([fromHash()]));
  const start = useRef<HTMLDivElement>(null);
  const buttons = useRef(new Map<TabKey, HTMLButtonElement>());

  useEffect(() => {
    const onHash = () => {
      const key = fromHash();
      setActive(key);
      setOpened((s) => (s.has(key) ? s : new Set(s).add(key)));
    };
    window.addEventListener("hashchange", onHash);
    return () => window.removeEventListener("hashchange", onHash);
  }, []);

  function select(key: TabKey) {
    setActive(key);
    setOpened((s) => (s.has(key) ? s : new Set(s).add(key)));
    window.history.replaceState(null, "", `#${key}`);
    // Switching from far down a long tab: start the new one at its top, under the tab bar.
    const top = (start.current?.getBoundingClientRect().top ?? 0) + window.scrollY;
    if (window.scrollY > top) window.scrollTo({ top });
  }

  function onKeyDown(e: React.KeyboardEvent) {
    const i = TABS.findIndex((t) => t.key === active);
    const next = ({ ArrowRight: i + 1, ArrowLeft: i - 1, Home: 0, End: TABS.length - 1 } as Record<string, number>)[e.key];
    if (next === undefined) return;
    e.preventDefault();
    const key = TABS[(next + TABS.length) % TABS.length].key;
    select(key);
    buttons.current.get(key)?.focus();
  }

  return (
    <>
      <div ref={start} />
      {/* On a narrow window the bar scrolls sideways instead of widening the page; the underline and focus ring sit inside each tab so the scroll can't clip them. */}
      <div role="tablist" aria-label="Report sections" onKeyDown={onKeyDown} className="sticky top-0 z-10 -mx-6 mt-4 flex gap-1 overflow-x-auto border-b border-line bg-bg px-6">
        {TABS.map((t) => {
          const on = t.key === active;
          return (
            <button
              key={t.key}
              ref={(el) => {
                if (el) buttons.current.set(t.key, el);
                else buttons.current.delete(t.key);
              }}
              id={`tab-${t.key}`}
              type="button"
              role="tab"
              aria-selected={on}
              aria-controls={`panel-${t.key}`}
              tabIndex={on ? 0 : -1}
              onClick={() => select(t.key)}
              className={`shrink-0 px-4 py-3 transition-colors duration-150 focus-visible:outline-offset-[-2px] ${on ? "font-semibold text-text shadow-[inset_0_-2px_0_var(--accent)]" : "text-muted hover:text-text"}`}
            >
              {t.label}
            </button>
          );
        })}
      </div>
      {TABS.map((t) => (
        <div key={t.key} role="tabpanel" id={`panel-${t.key}`} aria-labelledby={`tab-${t.key}`} hidden={t.key !== active} className="pt-6">
          {opened.has(t.key) && panels[t.key]}
        </div>
      ))}
    </>
  );
}
