"use client";

import { useEffect, useState } from "react";

const pad = (n: number) => String(n).padStart(2, "0");

function diff(target: number) {
  const ms = Math.max(0, target - Date.now());
  const s = Math.floor(ms / 1000);
  return { d: Math.floor(s / 86400), h: Math.floor((s % 86400) / 3600), m: Math.floor((s % 3600) / 60), s: s % 60 };
}

export function Countdown({ iso }: { iso: string }) {
  const target = new Date(iso).getTime();
  const [t, setT] = useState(() => diff(target));
  useEffect(() => {
    const id = setInterval(() => setT(diff(target)), 1000);
    return () => clearInterval(id);
  }, [target]);

  const units = [
    { v: t.d, label: "Days" },
    { v: t.h, label: "Hrs" },
    { v: t.m, label: "Min" },
    { v: t.s, label: "Sec" },
  ];

  return (
    <div className="flex items-stretch gap-2">
      {units.map((u, i) => (
        <div key={u.label} className="flex items-center gap-2">
          <div className="flex w-[62px] flex-col items-center border border-robark-line bg-robark-ink py-2.5">
            <span className="font-mono text-2xl font-bold tabular-nums text-robark-white">{pad(u.v)}</span>
            <span className="font-mono text-[10px] uppercase tracking-[0.2em] text-robark-mute">{u.label}</span>
          </div>
          {i < units.length - 1 && <span className="font-mono text-lg text-robark-rust">:</span>}
        </div>
      ))}
    </div>
  );
}
