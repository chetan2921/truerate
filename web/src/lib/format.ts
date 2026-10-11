// Money in INR with Indian grouping, counts compact in K / L / Cr (DESIGN.md, Content).

export function inr(n: number): string {
  return "₹" + Math.round(n).toLocaleString("en-IN");
}

// A price range, written the same way on every screen: "₹7,500 – ₹50,000".
export function inrRange(low: number, high: number): string {
  return `${inr(low)} – ${inr(high)}`;
}

function trim(x: number): string {
  return x >= 100 ? Math.round(x).toString() : x.toFixed(1).replace(/\.0$/, "");
}

export function compact(n: number): string {
  if (n >= 1e7) return `${trim(n / 1e7)}Cr`;
  if (n >= 1e5) return `${trim(n / 1e5)}L`;
  if (n >= 1e3) return `${trim(n / 1e3)}K`;
  return `${Math.round(n)}`;
}

export function pct(x: number, digits = 0): string {
  return `${(x * 100).toFixed(digits)}%`;
}

export function daysAgo(iso: string): string {
  const days = Math.floor((Date.now() - new Date(iso).getTime()) / 86_400_000);
  if (days < 1) return "today";
  return days === 1 ? "yesterday" : `${days} days ago`;
}

export const SESSION_COOKIE = "truerate_session";
