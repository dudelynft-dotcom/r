import { readFileSync } from "fs";
import path from "path";
import type { Match } from "./eligibility";

/**
 * Server-side reader for the finalized chain snapshot
 * (web/data/snapshot.json, produced by snapshot/make_snapshot.py).
 *
 * The eligibility check reads straight from this file — NO live Alchemy call.
 * Shape: { generatedAt, walletCount, collections:[{address,name,image}], wallets:{addr:[idx]} }
 */

type SnapshotFile = {
  generatedAt: string | null;
  walletCount: number;
  collections: { address: string; name: string; image: string | null }[];
  wallets: Record<string, number[]>;
};

let cache: SnapshotFile | null | undefined;

function load(): SnapshotFile | null {
  if (cache !== undefined) return cache;
  try {
    const file = path.join(process.cwd(), "data", "snapshot.json");
    cache = JSON.parse(readFileSync(file, "utf8")) as SnapshotFile;
  } catch {
    cache = null; // snapshot not generated yet
  }
  return cache;
}

// Tier 1 = top 50,000 wallets by # eligible collections held (tie-break: address asc).
// MUST match snapshot/make_snapshot.py / the OpenSea tier1/tier2 CSV split exactly.
const TIER1_SIZE = 50000;
let tier1Cache: Set<string> | null = null;

function tier1Set(): Set<string> {
  if (tier1Cache) return tier1Cache;
  const snap = load();
  if (!snap) return (tier1Cache = new Set());
  const entries = Object.entries(snap.wallets);
  entries.sort(
    (a, b) => b[1].length - a[1].length || (a[0] < b[0] ? -1 : a[0] > b[0] ? 1 : 0),
  );
  tier1Cache = new Set(entries.slice(0, TIER1_SIZE).map((e) => e[0]));
  return tier1Cache;
}

/** Which allowlist tier a wallet is in: 1 (top holders, mints first), 2, or null. */
export function walletTier(address: string): 1 | 2 | null {
  const snap = load();
  if (!snap) return null;
  const a = address.toLowerCase();
  if (!snap.wallets[a]?.length) return null;
  return tier1Set().has(a) ? 1 : 2;
}

export function snapshotReady(): boolean {
  return load() !== null;
}

export function snapshotWalletCount(): number {
  return load()?.walletCount ?? 0;
}

/** Eligible collections this wallet held at snapshot, or [] if not on the list. */
export function lookupWallet(address: string): Match[] {
  const snap = load();
  if (!snap) return [];
  const idxs = snap.wallets[address.toLowerCase()];
  if (!idxs?.length) return [];
  return idxs
    .map((i) => snap.collections[i])
    .filter(Boolean)
    .map((c) => ({ address: c.address.toLowerCase(), name: c.name, image: c.image }));
}
