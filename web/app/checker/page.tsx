"use client";

import { useMemo, useRef, useState } from "react";
import { isAddress } from "viem";
import type { CheckResult } from "@/lib/eligibility";
import { ELIGIBLE_COLLECTIONS, SNAPSHOT_AT } from "@/lib/eligibility";
import { ResultCard } from "@/components/ResultCard";
import { CollectionCard } from "@/components/CollectionCard";
import { SITE } from "@/lib/config";

const SNAP_DATE = SNAPSHOT_AT
  ? new Date(SNAPSHOT_AT).toLocaleDateString("en-US", { month: "long", day: "numeric", year: "numeric" })
  : null;

export default function CheckerPage() {
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<CheckResult | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  function checkAnother() {
    setResult(null);
    setError(null);
    setInput("");
    inputRef.current?.focus();
    inputRef.current?.scrollIntoView({ behavior: "smooth", block: "center" });
  }

  const heldSet = useMemo(
    () => new Set((result?.matches ?? []).map((m) => m.address.toLowerCase())),
    [result],
  );

  async function check(addr: string) {
    setError(null);
    setResult(null);
    if (!isAddress(addr)) {
      setError("Enter a valid Ethereum address (0x followed by 40 hex characters).");
      return;
    }
    setLoading(true);
    try {
      const res = await fetch("/api/check", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ address: addr }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data?.error ?? "Check failed. Try again.");
      setResult(data as CheckResult);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Something went wrong.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="relative">
      <div className="container-x py-14 lg:py-20">
        <div className="mx-auto max-w-2xl text-center">
          <span className="ticker mx-auto w-fit">
            <span className="text-robark-green"><span className="h-2 w-2 bg-robark-green" /> Snapshot taken</span>
            {SNAP_DATE && <span className="text-robark-fog">{SNAP_DATE}</span>}
            <span className="text-robark-mute">final</span>
          </span>
          <h1 className="mt-5 font-display text-4xl font-bold text-robark-white sm:text-5xl">Hold one, you&apos;re in.</h1>
          <p className="mt-4 font-mono text-sm leading-relaxed text-robark-soft">
            <span className="text-robark-rust">$</span> snapshot is final. hold any eligible collection
            (or be added as an X supporter) and your wallet is on the allowlist. no forms, no connect.
          </p>
        </div>

        {/* search — terminal prompt */}
        <div className="win mx-auto mt-10 max-w-2xl">
          <div className="win-bar">
            <span className="flex items-center gap-1.5">
              <span className="h-2.5 w-2.5 bg-robark-rust" />
              <span className="h-2.5 w-2.5 bg-robark-line" />
              <span className="h-2.5 w-2.5 bg-robark-line" />
            </span>
            <span>robark@checker — eligibility</span>
          </div>
          <div className="p-5 sm:p-6">
            <form
              onSubmit={(e) => { e.preventDefault(); check(input.trim()); }}
              className="flex items-center gap-2 border-2 border-robark-line bg-robark-black px-3 transition focus-within:border-robark-rust"
            >
              <span className="font-mono text-sm text-robark-green">$</span>
              <input
                ref={inputRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="check 0x… paste any wallet"
                spellCheck={false}
                autoComplete="off"
                autoFocus
                className="flex-1 bg-transparent py-3 font-mono text-sm text-robark-white outline-none placeholder:text-robark-mute"
              />
              <button type="submit" className="btn-rust shrink-0 px-4 py-2 text-[12px]" disabled={loading}>
                {loading ? "…" : "Run"}
              </button>
            </form>
            {error && (
              <p className="mt-4 border-l-2 border-robark-red bg-robark-red/10 px-4 py-3 font-mono text-sm text-robark-red">{error}</p>
            )}
          </div>
        </div>

        {/* result */}
        <div className="mx-auto mt-8 max-w-2xl">
          {loading && <LoadingCard />}
          {!loading && result && (
            <ResultCard result={result} openseaUrl={SITE.opensea} onCheckAnother={checkAnother} />
          )}
        </div>

        {/* eligible roster */}
        <div className="mt-16">
          <div className="flex items-end justify-between gap-4 border-b border-robark-line pb-4">
            <p className="eyebrow">Eligible Collections</p>
            <span className="hidden font-mono text-[11px] text-robark-mute sm:block">{SNAP_DATE ? `snapshot taken ${SNAP_DATE} · final` : "eligible set"}</span>
          </div>

          <div className="mt-6 grid grid-cols-3 gap-3 sm:grid-cols-4 md:grid-cols-5 lg:grid-cols-6">
            {ELIGIBLE_COLLECTIONS.map((c) => (
              <CollectionCard
                key={c.address}
                name={c.name}
                image={c.image}
                held={result ? heldSet.has(c.address.toLowerCase()) : false}
              />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

function LoadingCard() {
  return (
    <div className="card p-8">
      <div className="flex items-center gap-3 text-robark-rust">
        <span className="h-4 w-4 animate-spin border-2 border-robark-line border-t-robark-rust" />
        <span className="font-mono text-[11px] uppercase tracking-[0.2em]">reading the chain…</span>
      </div>
      <div className="mt-6 space-y-3">
        {[100, 80, 60].map((w) => (
          <div key={w} className="h-3 animate-pulse bg-robark-line" style={{ width: `${w}%` }} />
        ))}
      </div>
    </div>
  );
}
