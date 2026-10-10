import { CircleAlert, CircleCheck, CircleX, Info } from "lucide-react";

import type { Output } from "@/lib/api";

// A state always comes with its icon and a word, never colour alone.
export const STATUS = {
  good: { Icon: CircleCheck, color: "text-go", label: "Good" },
  warn: { Icon: CircleAlert, color: "text-negotiate", label: "Watch" },
  bad: { Icon: CircleX, color: "text-avoid", label: "Problem" },
  info: { Icon: Info, color: "text-info", label: "Note" },
} as const;

export function StatusIcon({ status, size = 20 }: { status: Output["status"]; size?: number }) {
  const { Icon, color, label } = STATUS[status];
  return <Icon size={size} className={`shrink-0 ${color}`} role="img" aria-label={label} />;
}

// The plain answers from the API: what the team reads instead of the measurements behind them.
export default function Verdicts({ outputs }: { outputs: Output[] }) {
  return (
    <ul className="grid gap-x-10 gap-y-4 lg:grid-cols-2">
      {outputs.map((o) => (
        <li key={o.key} className="flex gap-3">
          <span className="mt-0.5">
            <StatusIcon status={o.status} />
          </span>
          <div>
            <p className="font-semibold leading-snug">{o.title}</p>
            {o.detail && <p className="basis mt-0.5">{o.detail}</p>}
          </div>
        </li>
      ))}
    </ul>
  );
}
