import Link from "next/link";

import SignOut from "./sign-out";

export default function AppLayout({ children }: LayoutProps<"/">) {
  return (
    <>
      <header className="mx-auto flex max-w-6xl items-center justify-between px-6 py-5">
        <Link href="/" className="text-lg font-bold no-underline">
          TrueRate
        </Link>
        <SignOut />
      </header>
      {children}
    </>
  );
}
