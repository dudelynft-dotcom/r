import { NextResponse } from "next/server";
import { isAddress } from "viem";
import { buildResult, isSupporter, ELIGIBLE_COLLECTIONS, type CheckResult, type Match } from "@/lib/eligibility";
import { lookupWallet, snapshotReady } from "@/lib/snapshot";

export const runtime = "nodejs";

export async function POST(req: Request) {
  let address = "";
  try {
    const body = await req.json();
    address = String(body?.address ?? "").trim();
  } catch {
    return NextResponse.json({ error: "Invalid request body" }, { status: 400 });
  }

  if (!isAddress(address)) {
    return NextResponse.json(
      { error: "That doesn't look like a valid Ethereum address (0x…)." },
      { status: 400 },
    );
  }
  const addr = address.toLowerCase();

  // Read straight from the finalized snapshot — no live chain call.
  if (snapshotReady()) {
    const matches = lookupWallet(addr);
    return NextResponse.json(buildResult(addr, matches, "snapshot") satisfies CheckResult);
  }

  // Snapshot file not present (e.g. before it's generated) — deterministic demo.
  return NextResponse.json(demoResult(addr));
}

function demoResult(addr: string): CheckResult {
  const n = parseInt(addr.slice(2, 8), 16);
  const matches: Match[] = isSupporter(addr)
    ? []
    : n % 3
      ? [{ ...ELIGIBLE_COLLECTIONS[n % ELIGIBLE_COLLECTIONS.length] }]
      : [];
  return buildResult(addr, matches, "demo", "Demo data — snapshot.json not found.");
}
