const CALL_STYLE: Record<string, string> = {
  Go: "bg-go text-bg",
  Negotiate: "bg-negotiate text-bg",
  Avoid: "bg-avoid text-bg",
};

export function CallChip({ call, large = false }: { call: string; large?: boolean }) {
  return (
    <span className={`inline-flex items-center rounded-lg font-bold ${CALL_STYLE[call] ?? "bg-surface text-text"} ${large ? "px-4 py-2 text-2xl" : "px-2 py-0.5 text-sm"}`}>
      {call}
    </span>
  );
}

export const VERDICTS = ["Real audience", "Some fake activity", "Mostly fake"] as const;
export const VERDICT_COLOR: Record<string, string> = {
  "Real audience": "var(--go)",
  "Some fake activity": "var(--negotiate)",
  "Mostly fake": "var(--avoid)",
};
