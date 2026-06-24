"use client";

import { useEffect, useRef } from "react";
import { ANNOUNCEMENT, SITE } from "@/lib/config";

/**
 * Pinned announcement from the official @robark_io account, framed as a
 * notification. Uses X's official embed (widgets.js) so the real tweet renders;
 * if the script is blocked, the blockquote degrades to a link.
 */
export function TweetNotice() {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const render = () => {
      // @ts-expect-error twttr is injected by widgets.js
      window.twttr?.widgets?.load(ref.current);
    };
    // @ts-expect-error twttr is injected by widgets.js
    if (window.twttr?.widgets) {
      render();
      return;
    }
    let s = document.getElementById("twitter-wjs") as HTMLScriptElement | null;
    if (!s) {
      s = document.createElement("script");
      s.id = "twitter-wjs";
      s.src = "https://platform.twitter.com/widgets.js";
      s.async = true;
      document.body.appendChild(s);
    }
    s.addEventListener("load", render);
    return () => s?.removeEventListener("load", render);
  }, []);

  return (
    <div className="mx-auto mb-8 max-w-2xl border-2 border-robark-line bg-robark-ink">
      {/* notification header */}
      <div className="flex items-center gap-2.5 border-b-2 border-robark-line bg-robark-black px-4 py-2.5">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor" className="text-robark-white">
          <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
        </svg>
        <span className="font-mono text-[11px] uppercase tracking-[0.12em] text-robark-soft">
          New from <span className="text-robark-white">@{SITE.twitterHandle}</span>
        </span>
        <span className="ml-auto flex items-center gap-1.5 font-mono text-[10px] uppercase tracking-[0.12em] text-robark-rust">
          <span className="h-2 w-2 animate-blink bg-robark-rust" /> Pinned
        </span>
      </div>

      {/* official X embed */}
      <div ref={ref} className="px-3 [&_.twitter-tweet]:!mx-auto [&_.twitter-tweet]:!my-2">
        <blockquote
          className="twitter-tweet"
          data-theme="dark"
          data-dnt="true"
          data-conversation="none"
          data-align="center"
        >
          <a href={ANNOUNCEMENT.tweetUrl}>Announcement from @{SITE.twitterHandle} on X →</a>
        </blockquote>
      </div>
    </div>
  );
}
