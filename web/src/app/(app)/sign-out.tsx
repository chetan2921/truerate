"use client";

import { useRouter } from "next/navigation";

import { SESSION_COOKIE } from "@/lib/format";

export default function SignOut() {
  const router = useRouter();
  return (
    <button
      type="button"
      className="basis rounded-lg px-2 py-1 hover:text-text"
      onClick={() => {
        document.cookie = `${SESSION_COOKIE}=; path=/; max-age=0`;
        router.replace("/login");
      }}
    >
      Sign out
    </button>
  );
}
