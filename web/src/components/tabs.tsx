"use client";

import { useEffect, useRef, useState } from "react";

export type Tab = { key: string; label: string; panel: React.ReactNode };

// The open tab lives in the URL hash, so a shared link can open a page on a given tab. The first tab is the default.
function fromHash(keys: string[]): string {
  const key = location.hash.slice(1);
  return keys.includes(key) ? key : keys[0];
}

// Tabs for the creator report and the brand result: a sticky bar, arrow keys, `#tab` links, and each panel mounted the
// first time it opens and then kept, so a quote check survives a look at another tab.
export default function Tabs({ tabs, label }: { tabs: Tab[]; label: string }) {
  const keys = tabs.map((t) => t.key);
  const joined = keys.join(",");
  const [active, setActive] = useState(() => fromHash(keys));
  const [opened, setOpened] = useState(() => new Set<string>([fromHash(keys)]));
  const start = useRef<HTMLDivElement>(null);
  const buttons = useRef(new Map<string, HTMLButtonElement>());

  useEffect(() => {
    const onHash = () => {
      const key = fromHash(joined.split(","));
      setActive(key);
      setOpened((s) => (s.has(key) ? s : new Set(s).add(key)));
    };
    window.addEventListener("hashchange", onHash);
    return () => window.removeEventListener("hashchange", onHash);
  }, [joined]);

  function select(key: string) {
    setActive(key);
    setOpened((s) => (s.has(key) ? s : new Set(s).add(key)));
    window.history.replaceState(null, "", `#${key}`);
    // Switching from far down a long tab: start the new one at its top, under the tab bar.
    const top = (start.current?.getBoundingClientRect().top ?? 0) + window.scrollY;
    if (window.scrollY > top) window.scrollTo({ top });
  }

  function onKeyDown(e: React.KeyboardEvent) {
    const i = keys.indexOf(active);
    const next = ({ ArrowRight: i + 1, ArrowLeft: i - 1, Home: 0, End: keys.length - 1 } as Record<string, number>)[e.key];
    if (next === undefined) return;
    e.preventDefault();
    const key = keys[(next + keys.length) % keys.length];
    select(key);
    buttons.current.get(key)?.focus();
  }

  return (
    <>
      <div ref={start} />
      {/* On a narrow window the bar scrolls sideways instead of widening the page; the underline and focus ring sit inside each tab so the scroll can't clip them. */}
      <div role="tablist" aria-label={label} onKeyDown={onKeyDown} className="sticky top-0 z-10 -mx-6 mt-4 flex gap-1 overflow-x-auto border-b border-line bg-bg px-6">
        {tabs.map((t) => {
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
      {tabs.map((t) => (
        <div key={t.key} role="tabpanel" id={`panel-${t.key}`} aria-labelledby={`tab-${t.key}`} hidden={t.key !== active} className="pt-6">
          {opened.has(t.key) && t.panel}
        </div>
      ))}
    </>
  );
}
