"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const LINKS = [
  { href: "/", label: "Price a creator" },
  { href: "/batch", label: "Compare creators" },
  { href: "/brand", label: "Creators for a brand" },
  { href: "/rate-card", label: "Rate card" },
  { href: "/about", label: "About" },
];

function isActive(href: string, path: string): boolean {
  return href === "/" ? path === "/" || path.startsWith("/analyses") : path.startsWith(href);
}

// Rendered as-is while the path is unknown (the Suspense fallback), then with the current page marked.
export function NavLinks({ path }: { path: string | null }) {
  return (
    <nav aria-label="Main" className="flex flex-wrap gap-1 text-base sm:gap-3">
      {LINKS.map((l) => {
        const active = path !== null && isActive(l.href, path);
        return (
          <Link key={l.href} href={l.href} aria-current={active ? "page" : undefined}
            className={`rounded-lg px-2.5 py-2 no-underline sm:px-4 transition-colors duration-150 ${active ? "bg-surface text-text" : "text-muted hover:text-text"}`}>
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
