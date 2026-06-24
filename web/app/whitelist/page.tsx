"use client";

import { useMemo, useState } from "react";
import { isAddress } from "viem";
import { SITE, ANNOUNCEMENT } from "@/lib/config";

const LAUNCH = ANNOUNCEMENT.taskTweetUrl;
const HANDLE = SITE.twitterHandle;

// The X app swallows /intent/ links and dumps you on the home feed. Linking to
// the actual profile + post (which the app routes correctly) is reliable on mobile.
const followUrl = `https://x.com/${HANDLE}`; // opens the profile → tap Follow
const postUrl = LAUNCH; // opens the launch post → like / repost→quote / reply there

// capture the handle from a quote-tweet link: x.com/<handle>/status/<id>
const TWEET_RE = /(?:x|twitter)\.com\/([^/]+)\/status\/\d+/i;
const handleFromUrl = (url: string) => url.trim().match(TWEET_RE)?.[1]?.replace(/^@+/, "") ?? "";

function Pill({ done }: { done: boolean }) {
  return (
    <span className={`grid h-6 w-6 shrink-0 place-items-center border font-mono text-[12px] ${done ? "border-robark-green text-robark-green" : "border-robark-line text-robark-mute"}`}>
      {done ? "✓" : "•"}
    </span>
  );
}

export default function WhitelistPage() {
  const [follow, setFollow] = useState(false);
  const [quote, setQuote] = useState("");
  const [liked, setLiked] = useState(false);
  const [commented, setCommented] = useState(false);
  const [wallet, setWallet] = useState("");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [done, setDone] = useState(false);

  const xHandle = handleFromUrl(quote); // auto-derived from the quote link

  const v = useMemo(
    () => ({
      follow,
      quote: TWEET_RE.test(quote.trim()) && xHandle.length > 0,
      liked,
      commented,
      wallet: isAddress(wallet.trim()),
    }),
    [follow, quote, xHandle, liked, commented, wallet],
  );
  const ready = Object.values(v).every(Boolean);

  async function submit() {
    setError(null);
    if (!ready) {
      setError("Complete every step above first.");
      return;
    }
    setLoading(true);
    try {
      const res = await fetch("/api/whitelist", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ xUsername: xHandle, quoteUrl: quote, wallet }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data?.error ?? "Submission failed.");
      setDone(true);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Something went wrong.");
    } finally {
      setLoading(false);
    }
  }

  if (done) {
    return (
      <div className="container-x py-20 lg:py-28">
        <div className="mx-auto max-w-lg border-2 border-robark-green bg-robark-green/10 p-8 text-center">
          <div className="mx-auto grid h-14 w-14 place-items-center border-2 border-robark-green text-robark-green">
            <svg width="30" height="30" viewBox="0 0 24 24" fill="none"><path d="m5 13 4 4L19 7" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" /></svg>
          </div>
          <h1 className="mt-5 font-display text-3xl font-bold text-robark-green">Submission received</h1>
          <p className="mt-3 text-sm text-robark-soft">
            We&apos;ll verify your tasks and add eligible wallets to the public allowlist before mint.
            Keep an eye on <span className="text-robark-white">@{HANDLE}</span>.
          </p>
          <a href={SITE.opensea} target="_blank" rel="noreferrer" className="btn inline-flex mt-6 bg-robark-green text-robark-black hover:bg-robark-greendk">
            View on OpenSea
          </a>
        </div>
      </div>
    );
  }

  return (
    <div className="container-x py-14 lg:py-20">
      <div className="mx-auto max-w-2xl text-center">
        <span className="ticker mx-auto w-fit">
          <span className="text-robark-rust"><span className="h-2 w-2 animate-blink bg-robark-rust" /> Public whitelist</span>
          <span className="text-robark-mute">5,555 · jun 29</span>
        </span>
        <h1 className="mt-5 font-display text-4xl font-bold text-robark-white sm:text-5xl">Earn your spot.</h1>
        <p className="mt-4 font-mono text-sm leading-relaxed text-robark-soft">
          <span className="text-robark-rust">$</span> complete the steps, drop your wallet, and you&apos;re in the public allowlist pool.
        </p>
      </div>

      <div className="mx-auto mt-10 max-w-2xl space-y-3">
        {/* 1 — Follow */}
        <Step n="01" title={`Follow @${HANDLE}`} done={v.follow}>
          <div className="flex flex-wrap items-center gap-3">
            <a href={followUrl} target="_blank" rel="noreferrer" onClick={() => setFollow(true)} className="btn-rust text-[13px]">Open profile</a>
            <Toggle on={v.follow} onClick={() => setFollow((s) => !s)} label="I followed" />
          </div>
          <p className="mt-2 font-mono text-[11px] text-robark-mute">opens @{HANDLE} — tap Follow.</p>
        </Step>

        {/* 2 — Quote tweet (your handle is read from the link) */}
        <Step n="02" title="Quote-tweet the launch post" done={v.quote}>
          <div className="space-y-2.5">
            <a href={postUrl} target="_blank" rel="noreferrer" className="btn-rust text-[13px]">Open post</a>
            <p className="font-mono text-[11px] text-robark-mute">on the post: tap Repost → Quote, post it, then paste your link below.</p>
            <div className="flex items-center gap-2 border-2 border-robark-line bg-robark-black px-3 focus-within:border-robark-rust">
              <span className="font-mono text-sm text-robark-mute">↳</span>
              <input value={quote} onChange={(e) => setQuote(e.target.value)} placeholder="paste your quote-tweet link" spellCheck={false} autoComplete="off"
                className="flex-1 bg-transparent py-2.5 font-mono text-sm text-robark-white outline-none placeholder:text-robark-mute" />
            </div>
            {xHandle && (
              <p className="font-mono text-[11px] text-robark-green">detected: @{xHandle}</p>
            )}
          </div>
        </Step>

        {/* 3 — Like */}
        <Step n="03" title="Like the launch post" done={v.liked}>
          <div className="flex flex-wrap items-center gap-3">
            <a href={postUrl} target="_blank" rel="noreferrer" onClick={() => setLiked(true)} className="btn-line text-[13px]">Open post</a>
            <Toggle on={v.liked} onClick={() => setLiked((s) => !s)} label="I liked it" />
          </div>
          <p className="mt-2 font-mono text-[11px] text-robark-mute">opens the post — tap the heart.</p>
        </Step>

        {/* 4 — Comment */}
        <Step n="04" title="Comment on the launch post" done={v.commented}>
          <div className="flex flex-wrap items-center gap-3">
            <a href={postUrl} target="_blank" rel="noreferrer" onClick={() => setCommented(true)} className="btn-line text-[13px]">Open post</a>
            <Toggle on={v.commented} onClick={() => setCommented((s) => !s)} label="I commented" />
          </div>
          <p className="mt-2 font-mono text-[11px] text-robark-mute">opens the post — tap reply and drop a comment.</p>
        </Step>

        {/* 5 — Wallet */}
        <Step n="05" title="Your wallet" done={v.wallet}>
          <div className="flex items-center gap-2 border-2 border-robark-line bg-robark-black px-3 focus-within:border-robark-rust">
            <span className="font-mono text-sm text-robark-green">$</span>
            <input value={wallet} onChange={(e) => setWallet(e.target.value)} placeholder="0x… your Ethereum wallet" spellCheck={false} autoComplete="off"
              className="flex-1 bg-transparent py-2.5 font-mono text-sm text-robark-white outline-none placeholder:text-robark-mute" />
          </div>
        </Step>

        {error && <p className="border-l-2 border-robark-red bg-robark-red/10 px-4 py-3 font-mono text-sm text-robark-red">{error}</p>}

        <button onClick={submit} disabled={loading || !ready}
          className={`btn w-full ${ready ? "bg-robark-rust text-robark-black hover:bg-robark-ember" : "border border-robark-line text-robark-mute"}`}>
          {loading ? "Submitting…" : ready ? "Submit whitelist entry" : "Complete all steps to submit"}
        </button>
        <p className="text-center font-mono text-[11px] text-robark-mute">Submissions are verified before mint. One entry per wallet.</p>
      </div>
    </div>
  );
}

function Step({ n, title, done, children }: { n: string; title: string; done: boolean; children: React.ReactNode }) {
  return (
    <div className={`border-2 bg-robark-ink p-4 transition ${done ? "border-robark-green/50" : "border-robark-line"}`}>
      <div className="mb-3 flex items-center gap-3">
        <Pill done={done} />
        <span className="font-mono text-[11px] uppercase tracking-[0.14em] text-robark-mute">{n}</span>
        <span className="font-display text-base font-semibold text-robark-white">{title}</span>
      </div>
      {children}
    </div>
  );
}

function Toggle({ on, onClick, label }: { on: boolean; onClick: () => void; label: string }) {
  return (
    <button type="button" onClick={onClick}
      className={`inline-flex items-center gap-2 border px-3 py-2 font-mono text-[12px] transition ${on ? "border-robark-green text-robark-green" : "border-robark-line text-robark-soft hover:border-robark-soft"}`}>
      <span className={`grid h-4 w-4 place-items-center border text-[10px] ${on ? "border-robark-green bg-robark-green text-robark-black" : "border-robark-line"}`}>{on ? "✓" : ""}</span>
      {label}
    </button>
  );
}
