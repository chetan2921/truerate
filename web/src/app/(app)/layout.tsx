import Link from "next/link";
import { Suspense } from "react";

import Nav, { NavLinks } from "./nav";
import SignOut from "./sign-out";

export default function AppLayout({ children }: LayoutProps<"/">) {
  return (
    <>
      <header className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-3 px-6 py-5 print:hidden">
        <div className="flex items-center gap-6">
          <Link href="/" className="text-lg font-bold no-underline">
            TrueRate
          </Link>
          <Suspense fallback={<NavLinks path={null} />}>
            <Nav />
          </Suspense>
        </div>
        <SignOut />
      </header>
      {children}
    </>
  );
}
