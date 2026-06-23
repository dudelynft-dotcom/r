import wl from "@/data/whitelist-collections.json";
import extra from "@/data/extra-wallets.json";

export type PhaseId = "allowlist" | "public";

/** When the chain snapshot was taken (ISO). The eligible set is final. */
export const SNAPSHOT_AT: string | null = (wl as { generatedAt?: string }).generatedAt ?? null;

// Manually-added supporter wallets (e.g. from X) — always on the allowlist.
const EXTRA = new Set<string>(((extra.wallets as string[]) ?? []).map((w) => w.toLowerCase()));
export const SUPPORTER_COUNT = EXTRA.size;

export function isSupporter(address: string) {
  return EXTRA.has(address.toLowerCase());
}

export type EligibleCollection = { address: string; name: string; image: string | null };

// One combined eligible set (site never labels them trending/featured).
const RAW: EligibleCollection[] = [
  ...((wl.trending as { address: string; name: string; image?: string }[]) ?? []),
  ...((wl.featured as { address: string; name: string; image?: string }[]) ?? []),
].map((c) => ({ address: c.address.toLowerCase(), name: c.name, image: c.image ?? null }));

const _seen = new Set<string>();
export const ELIGIBLE_COLLECTIONS: EligibleCollection[] = RAW.filter(
  (c) => !_seen.has(c.address) && _seen.add(c.address),
);

export type Match = { address: string; name: string; image: string | null };

export type CheckResult = {
  address: string;
  matches: Match[];
  supporter: boolean;
  phase: PhaseId;
  phaseLabel: string;
  source: "snapshot" | "demo";
  note?: string;
};

const PHASE_LABELS: Record<PhaseId, string> = {
  allowlist: "You're on the allowlist",
  public: "Public phase only",
};

/** Build a result from the eligible collections a wallet holds (per the snapshot). */
export function buildResult(
  address: string,
  matches: Match[],
  source: CheckResult["source"],
  note?: string,
): CheckResult {
  const supporter = isSupporter(address);
  const phase: PhaseId = matches.length || supporter ? "allowlist" : "public";
  return {
    address: address.toLowerCase(),
    matches,
    supporter,
    phase,
    phaseLabel: PHASE_LABELS[phase],
    source,
    note,
  };
}

export { PHASE_LABELS };
