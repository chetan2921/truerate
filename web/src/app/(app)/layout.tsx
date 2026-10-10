import Link from "next/link";
import { Suspense } from "react";

import Nav, { NavLinks } from "./nav";
import SignOut from "./sign-out";

export default function AppLayout({ children }: LayoutProps<"/">) {
  return (
    <>
      <header className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-3 px-6 py-6 print:hidden">
        <div className="flex flex-wrap items-center gap-x-6 gap-y-2 sm:gap-x-12">
          <Link href="/" className="text-2xl font-bold no-underline">
            TruRate
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
