import { NextResponse } from "next/server";
import { isAddress } from "viem";

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
  const wallet = String(body.wallet ?? "").trim();

  if (!xUsername || xUsername.length > 30) {
    return NextResponse.json({ error: "Enter your X username." }, { status: 400 });
  }
  if (!TWEET_RE.test(quoteUrl)) {
    return NextResponse.json({ error: "Paste the link to your quote tweet." }, { status: 400 });
  }
  if (!isAddress(wallet)) {
    return NextResponse.json({ error: "Enter a valid wallet address (0x…)." }, { status: 400 });
  }

  const entry = {
    xUsername,
    quoteUrl,
    wallet: wallet.toLowerCase(),
    at: new Date().toISOString(),
    ip: req.headers.get("x-forwarded-for") ?? "",
  };

  // Always log (captured in Railway logs as a fallback record).
  console.log("[whitelist-submission]", JSON.stringify(entry));

  // Forward to a webhook for persistent collection (Discord-compatible).
  const hook = process.env.WHITELIST_WEBHOOK_URL;
  if (hook) {
    try {
      const isDiscord = hook.includes("discord.com/api/webhooks");
      const payload = isDiscord
        ? {
            content:
              `**New WL submission**\n` +
              `• X: @${xUsername}\n` +
              `• Wallet: \`${entry.wallet}\`\n` +
              `• Quote: ${quoteUrl}`,
          }
        : entry;
      await fetch(hook, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify(payload),
      });
    } catch (e) {
      console.error("[whitelist-webhook] failed:", e);
    }
  }

  return NextResponse.json({ ok: true });
}
