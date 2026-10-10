"use client";

import { ChevronDown, X } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useRef, useState } from "react";

export type Column<T> = { label: string; cell: (item: T) => React.ReactNode; className?: string };

// A creator or brand as its display name with the handle beside it, never in brackets.
export function NameHandle({ name, handle }: { name?: string | null; handle: string }) {
  return (
    <span className="flex min-w-0 items-baseline gap-2">
      {name && <span className="truncate font-semibold">{name}</span>}
      <span className={name ? "basis shrink-0" : "font-semibold"}>@{handle}</span>
    </span>
  );
}

const ROW = 53; // one-line rows (52px plus the divider), so the rows that fit can be worked out from the page's height

// The recent list on the creator, compare and brand pages: a table that stops at the bottom of the first screen
// (the rest behind "Show all"), each row opening its page, with an × that takes it off the list.
export default function RecentTable<T extends { id: string }>({ title, items, href, columns, onRemove, removeLabel, empty, className = "" }: {
  title: string;
  items: T[] | null;
  href: (item: T) => string;
  columns: Column<T>[];
  onRemove: (id: string) => void;
  removeLabel: (item: T) => string;
  empty: string;
  className?: string;
}) {
  const router = useRouter();
  const table = useRef<HTMLTableElement>(null);
  const [fit, setFit] = useState(5);
  const [showAll, setShowAll] = useState(false);
  const loaded = items !== null;

  // Runs again when Next shows this page again, and on every resize.
  useEffect(() => {
    // Measured, not guessed: how far the page's real bottom (padding and the "Show all" button included) sits above or
    // below the window, turned into rows to add or take away. Only while the list is cut short.
    const measure = () => {
      const t = table.current;
      const page = t?.closest("main");
      if (!t || !page || showAll) return;
      const spare = window.innerHeight - page.getBoundingClientRect().bottom;
      setFit(Math.max(1, t.tBodies[0].rows.length + Math.floor(spare / ROW)));
    };
    const frame = requestAnimationFrame(measure);
    window.addEventListener("resize", measure);
    return () => {
      cancelAnimationFrame(frame);
      window.removeEventListener("resize", measure);
    };
  }, [loaded, showAll]);

  const id = title.toLowerCase().replace(/\W+/g, "-");
  const shown = items && !showAll ? items.slice(0, fit) : (items ?? []);
  return (
    <section aria-labelledby={id} className={className}>
      <h2 id={id} className="section-title">
        {title}
      </h2>
      {items === null ? (
        <p className="basis mt-3">Loading…</p>
      ) : items.length === 0 ? (
        <p className="basis mt-3">{empty}</p>
      ) : (
        <>
          {/* On a narrow window the table scrolls inside this box instead of widening the page; "relative" keeps the hidden "Remove" header label inside it too. */}
          <div className="relative mt-3 overflow-x-auto">
          <table ref={table} className="w-full min-w-[44rem] table-fixed text-sm">
            <thead className="text-left text-muted">
              <tr>
                {columns.map((c) => (
                  <th key={c.label} className={`py-2 pr-4 font-normal ${c.className ?? ""}`}>
                    {c.label}
                  </th>
                ))}
                <th className="w-12">
                  <span className="sr-only">Remove</span>
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-line">
              {shown.map((item) => (
                <tr key={item.id} className="cursor-pointer transition-colors duration-150 hover:bg-surface" onClick={() => router.push(href(item))}>
                  {columns.map((c, i) => (
                    <td key={c.label} className={`h-[52px] truncate py-0 pr-4 ${c.className ?? ""}`}>
                      {i === 0 ? (
                        <Link href={href(item)} className="block min-w-0 no-underline" onClick={(e) => e.stopPropagation()}>
                          {c.cell(item)}
                        </Link>
                      ) : (
                        c.cell(item)
                      )}
                    </td>
                  ))}
                  <td className="text-right">
                    <button
                      type="button"
                      onClick={(e) => {
                        e.stopPropagation();
                        onRemove(item.id);
                      }}
                      aria-label={removeLabel(item)}
                      title="Remove from this list"
                      className="rounded-md p-2 text-muted transition-colors duration-150 hover:bg-surface hover:text-text"
                    >
                      <X size={16} aria-hidden />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          </div>
          {items.length > fit && (
            <button type="button" className="btn btn-quiet mt-4 py-2 text-sm" aria-expanded={showAll} onClick={() => setShowAll((v) => !v)}>
              {showAll ? "Show fewer" : `Show all ${items.length}`}
              <ChevronDown size={16} aria-hidden className={`transition-transform duration-150 ${showAll ? "rotate-180" : ""}`} />
            </button>
          )}
        </>
      )}
    </section>
  );
}
