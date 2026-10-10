"use client";

import { useRouter } from "next/navigation";

import { SESSION_COOKIE } from "@/lib/format";

export default function SignOut() {
  const router = useRouter();
  return (
    <button
      type="button"
      className="rounded-lg px-3 py-2 text-base text-muted hover:text-text"
      onClick={() => {
        document.cookie = `${SESSION_COOKIE}=; path=/; max-age=0`;
        router.replace("/login");
      }}
    >
      Sign out
    </button>
  );
}
