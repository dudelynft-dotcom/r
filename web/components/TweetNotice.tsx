import { ANNOUNCEMENT, SITE } from "@/lib/config";

/**
 * Compact "@robark_io just posted" notification — the whole bar is a link that
 * redirects to the tweet on X. No embed, just a clickable notice.
 */
export function TweetNotice() {
  return (
    <a
      href={ANNOUNCEMENT.tweetUrl}
      target="_blank"
      rel="noreferrer"
      className="group mx-auto mb-8 flex max-w-2xl items-center gap-3 border-2 border-robark-line bg-robark-ink px-4 py-3 transition hover:border-robark-rust"
    >
      {/* X app-style avatar with a notification dot */}
      <span className="relative grid h-9 w-9 shrink-0 place-items-center border border-robark-line bg-robark-black">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor" className="text-robark-white">
          <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
        </svg>
        <span className="absolute -right-1 -top-1 h-2.5 w-2.5 animate-blink bg-robark-rust" />
      </span>

      <div className="min-w-0 flex-1">
        <p className="font-mono text-[10px] font-medium uppercase tracking-[0.16em] text-robark-rust">New post on X</p>
        <p className="truncate text-sm text-robark-fog">
          <span className="font-semibold text-robark-white">@{SITE.twitterHandle}</span> just tweeted — tap to read
        </p>
      </div>

      <span className="shrink-0 font-mono text-[12px] text-robark-soft transition group-hover:text-robark-white">
        Read&nbsp;→
      </span>
    </a>
  );
}
