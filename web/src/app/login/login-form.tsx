"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import { SESSION_COOKIE } from "@/lib/format";

export default function LoginForm() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [error, setError] = useState("");

  function signIn(who: string) {
    document.cookie = `${SESSION_COOKIE}=${encodeURIComponent(who)}; path=/; max-age=2592000; samesite=lax`;
    const next = new URLSearchParams(location.search).get("next");
    router.replace(next?.startsWith("/") ? next : "/");
  }

  function submit(e: React.FormEvent) {
    e.preventDefault();
    const value = email.trim().toLowerCase();
    if (!value.endsWith("@wldd.in")) {
      setError("Use your @wldd.in email.");
      return;
    }
    signIn(value);
  }

  return (
    <div className="mt-10">
      <button type="button" className="btn btn-primary w-full justify-center" onClick={() => signIn("demo")}>
        Demo login
      </button>
      <form onSubmit={submit} className="mt-8" noValidate>
        <label htmlFor="email" className="basis">
          Or sign in with your WLDD email
        </label>
        <div className="mt-2 flex gap-2">
          <input
            id="email"
            type="email"
            className="field min-w-0 flex-1"
            placeholder="name@wldd.in"
            value={email}
            onChange={(e) => {
              setEmail(e.target.value);
              setError("");
            }}
            aria-invalid={Boolean(error)}
            aria-describedby={error ? "email-error" : undefined}
          />
          <button type="submit" className="btn btn-quiet">
            Continue
          </button>
        </div>
        {error && (
          <p id="email-error" className="mt-2 text-sm text-avoid">
            {error}
          </p>
        )}
      </form>
    </div>
  );
}
