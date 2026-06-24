import { NextResponse } from "next/server";
import { isAddress } from "viem";
import { getSql } from "@/lib/db";

export const runtime = "nodejs";

const TWEET_RE = /(?:x|twitter)\.com\/[^/]+\/status\/\d+/i;

export async function POST(req: Request) {
  let body: Record<string, unknown> = {};
  try {
    body = await req.json();
  } catch {
    return NextResponse.json({ error: "Invalid request." }, { status: 400 });
  }

  const xUsername = String(body.xUsername ?? "").trim().replace(/^@+/, "");
  const quoteUrl = String(body.quoteUrl ?? "").trim();
  const wallet = String(body.wallet ?? "").trim().toLowerCase();

  if (!xUsername || xUsername.length > 30) {
    return NextResponse.json({ error: "Enter your X username." }, { status: 400 });
  }
  if (!TWEET_RE.test(quoteUrl)) {
    return NextResponse.json({ error: "Paste the link to your quote tweet." }, { status: 400 });
  }
  if (!isAddress(wallet)) {
    return NextResponse.json({ error: "Enter a valid wallet address (0x…)." }, { status: 400 });
  }

  const ip = req.headers.get("x-forwarded-for") ?? "";
  console.log("[whitelist-submission]", JSON.stringify({ xUsername, wallet, quoteUrl }));

  const sql = getSql();
  if (!sql) {
    return NextResponse.json({ error: "Submissions are temporarily unavailable." }, { status: 503 });
  }

  try {
    await sql`
      INSERT INTO whitelist_submissions (x_username, wallet, quote_url, ip)
      VALUES (${xUsername}, ${wallet}, ${quoteUrl}, ${ip})
      ON CONFLICT (wallet) DO UPDATE
        SET x_username = EXCLUDED.x_username,
            quote_url  = EXCLUDED.quote_url,
            ip         = EXCLUDED.ip,
            updated_at = now()
    `;
  } catch (e) {
    console.error("[whitelist-db] insert failed:", e);
    return NextResponse.json({ error: "Could not save submission. Try again." }, { status: 500 });
  }

  return NextResponse.json({ ok: true });
}

/**
 * Admin export. GET /api/whitelist?key=ADMIN_KEY[&format=wallets]
 *  - default: JSON of all submissions
 *  - format=wallets: newline-separated wallet list (paste into extra-wallets.json)
 */
export async function GET(req: Request) {
  const url = new URL(req.url);
  const key = url.searchParams.get("key");
  if (!process.env.ADMIN_KEY || key !== process.env.ADMIN_KEY) {
    return NextResponse.json({ error: "Unauthorized." }, { status: 401 });
  }
  const sql = getSql();
  if (!sql) return NextResponse.json({ error: "No database configured." }, { status: 503 });

  const rows = (await sql`
    SELECT x_username, wallet, quote_url, created_at
    FROM whitelist_submissions
    ORDER BY created_at DESC
  `) as { x_username: string; wallet: string; quote_url: string; created_at: string }[];

  if (url.searchParams.get("format") === "wallets") {
    return new Response(rows.map((r) => r.wallet).join("\n"), {
      headers: { "content-type": "text/plain; charset=utf-8" },
    });
  }
  return NextResponse.json({ count: rows.length, submissions: rows });
}
