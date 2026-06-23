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
          </div>
        </div>
      </div>

      <div className="hairline">
        <div className="container-x flex flex-col items-center justify-between gap-2 py-5 font-mono text-[11px] text-robark-mute sm:flex-row">
          <p>© {new Date().getFullYear()} ROBARK.IO — pixel-bred on Ethereum.</p>
          <p>NOT FINANCIAL ADVICE</p>
        </div>
      </div>
    </footer>
  );
}
