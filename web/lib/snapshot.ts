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
