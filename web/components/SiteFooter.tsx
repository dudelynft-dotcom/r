import Link from "next/link";
import { SITE } from "@/lib/config";
import { BrandMark } from "./Logo";

function Social({ href, label, children }: { href: string; label: string; children: React.ReactNode }) {
  return (
    <a
      href={href}
      target="_blank"
      rel="noreferrer"
      aria-label={label}
      className="grid h-10 w-10 place-items-center border border-robark-line text-robark-soft transition hover:border-robark-rust hover:text-robark-white"
    >
      {children}
    </a>
  );
}

export function SiteFooter() {
  return (
    <footer className="border-t border-robark-line bg-robark-black">
      <div className="container-x grid gap-10 py-14 md:grid-cols-[1.6fr_1fr_1fr]">
        <div>
          <div className="flex items-center gap-3">
            <BrandMark size={32} />
            <span className="font-pixel text-[13px] text-robark-white">ROBARK</span>
          </div>
          <p className="mt-4 max-w-xs text-sm leading-relaxed text-robark-mute">
            5,555 pixel degens who survived the crash. One dog, 5,555 bad days.
            On-chain energy, served live.
          </p>
        </div>

        <div>
          <h4 className="eyebrow">Explore</h4>
          <ul className="mt-4 space-y-2.5 font-mono text-[12px] text-robark-soft">
            <li><Link href="/#collection" className="hover:text-robark-white">Collection</Link></li>
            <li><Link href="/#traits" className="hover:text-robark-white">Traits</Link></li>
            <li><Link href="/#mint" className="hover:text-robark-white">Mint</Link></li>
            <li><Link href="/checker" className="hover:text-robark-white">Whitelist Checker</Link></li>
          </ul>
        </div>

        <div>
          <h4 className="eyebrow">Channel</h4>
          <div className="mt-4 flex gap-3">
            <Social href={SITE.twitter} label="X">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>
            </Social>
            <Social href={SITE.discord} label="Discord">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M20.317 4.369A19.79 19.79 0 0 0 16.558 3a13.7 13.7 0 0 0-.66 1.35 18.27 18.27 0 0 0-5.487 0A13.6 13.6 0 0 0 9.745 3 19.74 19.74 0 0 0 5.98 4.37C2.5 9.41 1.71 14.3 2.04 19.12a19.9 19.9 0 0 0 6.04 3.05c.49-.67.93-1.39 1.3-2.14-.71-.27-1.4-.6-2.05-.99.17-.13.34-.26.5-.4a14.2 14.2 0 0 0 12.14 0c.16.14.33.27.5.4-.65.39-1.34.72-2.05.99.37.75.81 1.47 1.3 2.14a19.85 19.85 0 0 0 6.04-3.05c.39-5.59-.83-10.44-3.44-14.75ZM8.68 15.79c-1.18 0-2.15-1.08-2.15-2.41 0-1.33.95-2.42 2.15-2.42s2.17 1.09 2.15 2.42c0 1.33-.95 2.41-2.15 2.41Zm6.64 0c-1.18 0-2.15-1.08-2.15-2.41 0-1.33.95-2.42 2.15-2.42s2.17 1.09 2.15 2.42c0 1.33-.94 2.41-2.15 2.41Z"/></svg>
            </Social>
            <Social href={SITE.opensea} label="OpenSea">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M12 0C5.37 0 0 5.37 0 12s5.37 12 12 12 12-5.37 12-12S18.63 0 12 0Zm-6.08 12.4.05-.08 3.18-4.97a.11.11 0 0 1 .19.01c.53 1.19.99 2.67.77 3.59-.09.38-.34.89-.63 1.36a2.3 2.3 0 0 1-.18.27.1.1 0 0 1-.08.04H6.01a.11.11 0 0 1-.09-.21Zm13.92 1.48c0 .06-.04.12-.09.14-.32.14-1.4.65-1.85 1.27-1.15 1.6-2.03 3.9-4 3.9H8.06A3.66 3.66 0 0 1 4.4 15.5v-.14c0-.06.05-.11.11-.11h3.55c.07 0 .12.06.12.13 0 .26.04.51.14.74.18.46.63.78 1.13.78h1.75v-1.37H9.6a.11.11 0 0 1-.09-.18c.05-.07.1-.14.17-.23.45-.64 1.1-1.64 1.52-2.6.29-.64.5-1.31.59-1.94.05-.34.07-.63.07-.92 0-.11 0-.23-.01-.34l1.51.17c.93.13 1.66.97 1.66 1.94v.04h1.34c.07 0 .12.05.12.12v.7c0 .07-.05.12-.12.12h-1.34v.65h1.34c.07 0 .12.06.12.12 0 .06-.05.12-.12.12h-1.34v.65h1.34c.07 0 .12.06.12.12Z"/></svg>
            </Social>
          </div>
        </div>
      </div>

      <div className="hairline">
        <div className="container-x flex flex-col items-center justify-between gap-2 py-5 font-mono text-[11px] text-robark-mute sm:flex-row">
          <p>© {new Date().getFullYear()} ROBARK.IO — pixel-bred on Ethereum.</p>
          <p>NOT FINANCIAL ADVICE · DYOR</p>
        </div>
      </div>
    </footer>
  );
}
