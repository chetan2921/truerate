"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const LINKS = [
  { href: "/", label: "Analyze" },
  { href: "/batch", label: "Batch" },
  { href: "/rate-card", label: "Rate card" },
  { href: "/about", label: "About" },
];

function isActive(href: string, path: string): boolean {
  return href === "/" ? path === "/" || path.startsWith("/analyses") : path.startsWith(href);
}

// Rendered as-is while the path is unknown (the Suspense fallback), then with the current page marked.
export function NavLinks({ path }: { path: string | null }) {
  return (
    <nav aria-label="Main" className="flex gap-1 text-sm">
      {LINKS.map((l) => {
        const active = path !== null && isActive(l.href, path);
        return (
          <Link key={l.href} href={l.href} aria-current={active ? "page" : undefined}
            className={`rounded-lg px-3 py-1.5 no-underline transition-colors duration-150 ${active ? "bg-surface text-text" : "text-muted hover:text-text"}`}>
            {l.label}
          </Link>
        );
      })}
    </nav>
  );
}

export default function Nav() {
  return <NavLinks path={usePathname()} />;
}
