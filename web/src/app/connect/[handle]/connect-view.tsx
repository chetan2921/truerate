"use client";

import { use, useState } from "react";

import { api } from "@/lib/api";

type PhylloConnect = {
  initialize: (config: Record<string, string>) => { on: (event: string, fn: (...args: string[]) => void) => void; open: () => void };
};
declare global {
  interface Window {
    PhylloConnect?: PhylloConnect;
  }
}

const SDK = "https://cdn.getphyllo.com/connect/v2/phyllo-connect.js";

function loadSdk(): Promise<PhylloConnect> {
  return new Promise((resolve, reject) => {
    if (window.PhylloConnect) return resolve(window.PhylloConnect);
    const script = Object.assign(document.createElement("script"), { src: SDK, async: true });
    script.onload = () => (window.PhylloConnect ? resolve(window.PhylloConnect) : reject(new Error("Phyllo Connect didn't load.")));
    script.onerror = () => reject(new Error("Phyllo Connect didn't load. Check the connection and try again."));
    document.body.appendChild(script);
  });
}

// For the creator, not WLDD: they connect Instagram through Phyllo so WLDD sees their real reach and audience.
export default function ConnectView({ params }: { params: Promise<{ handle: string }> }) {
  const { handle } = use(params);
  const [state, setState] = useState<"idle" | "connecting" | "done" | "error">("idle");
  const [message, setMessage] = useState("");

  async function connect() {
    setState("connecting");
    setMessage("");
    try {
      const [sdk, start] = await Promise.all([loadSdk(), api.startVerify(handle)]);
      const phyllo = sdk.initialize({ clientDisplayName: "TrueRate by WLDD", environment: start.environment, userId: start.user_id, token: start.sdk_token });
      // Phyllo Connect checks each callback's argument count, so they declare every argument it passes.
      /* eslint-disable @typescript-eslint/no-unused-vars */
      phyllo.on("accountConnected", async (_accountId, _platformId, _userId) => {
        try {
          await api.getVerified(handle);
          setState("done");
        } catch (e) {
          setState("error");
          setMessage((e as Error).message);
        }
      });
      phyllo.on("connectionFailure", (reason, _platformId, _userId) => {
        setState("error");
        setMessage(`Instagram didn't connect: ${reason}.`);
      });
      phyllo.on("tokenExpired", (_userId) => {
        setState("error");
        setMessage("This link has expired. Ask WLDD for a new one.");
      });
      phyllo.on("accountDisconnected", (_accountId, _platformId, _userId) => {});
      phyllo.on("exit", (_reason, _userId) => setState((s) => (s === "connecting" ? "idle" : s)));
      /* eslint-enable @typescript-eslint/no-unused-vars */
      phyllo.open();
    } catch (e) {
      setState("error");
      setMessage((e as Error).message);
    }
  }

  return (
    <main className="mx-auto flex min-h-screen max-w-lg flex-col justify-center px-6">
      <h1 className="text-3xl font-bold">Share your real reach with WLDD</h1>
      {state === "done" ? (
        <p className="mt-4 text-lg text-go">Thank you, @{handle}. WLDD can now see your verified reach and audience.</p>
      ) : (
        <>
          <p className="mt-4">
            WLDD prices campaigns on what your reels actually deliver. Connecting @{handle} through Phyllo shares your post reach and your audience&apos;s
            countries, cities, age and gender. Nothing is posted, and you can disconnect at any time.
          </p>
          <button type="button" className="btn btn-primary mt-8 justify-center" onClick={connect} disabled={state === "connecting"}>
            {state === "connecting" ? "Opening Phyllo…" : "Connect Instagram"}
          </button>
          {message && (
            <p role="alert" className="mt-3 text-avoid">
              {message}
            </p>
          )}
        </>
      )}
      <p className="basis mt-10">Powered by Phyllo, a creator-consented data service. TrueRate is WLDD&apos;s internal pricing tool.</p>
    </main>
  );
}
