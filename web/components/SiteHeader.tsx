"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import { Logo } from "./Logo";
import { SITE } from "@/lib/config";

const NAV = [
  { href: "/#how", label: "How it works" },
  { href: "/#mint", label: "Mint" },
  { href: "/checker", label: "Checker" },
  { href: "/whitelist", label: "Get WL" },
];

export function SiteHeader() {
  const pathname = usePathname();
  const [open, setOpen] = useState(false);

  return (
    <header className="sticky top-0 z-50 border-b border-robark-line bg-robark-black/85 backdrop-blur-xl">
      <div className="container-x flex h-16 items-center justify-between">
        <Logo />

        <nav className="hidden items-center gap-8 md:flex">
          {NAV.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className={`font-mono text-[12px] uppercase tracking-[0.18em] transition-colors hover:text-robark-white ${
                pathname === item.href ? "text-robark-white" : "text-robark-mute"
              }`}
            >
              {item.label}
            </Link>
          ))}
        </nav>

        <div className="flex items-center gap-3">
          <a
            href={SITE.opensea}
            target="_blank"
            rel="noreferrer"
            className="hidden btn-rust sm:inline-flex"
          >
            Mint on OpenSea
          </a>
          <button
            aria-label="Menu"
            onClick={() => setOpen((v) => !v)}
            className="btn-line px-3 py-2 md:hidden"
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
              <path d="M4 6h16M4 12h16M4 18h16" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
            </svg>
          </button>
        </div>
      </div>

      {open && (
        <div className="border-t border-robark-line bg-robark-black md:hidden">
          <div className="container-x flex flex-col gap-1 py-3">
            {NAV.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                onClick={() => setOpen(false)}
                className="px-2 py-2.5 font-mono text-[12px] uppercase tracking-[0.18em] text-robark-soft hover:text-robark-white"
              >
                {item.label}
              </Link>
            ))}
            <a
              href={SITE.opensea}
              target="_blank"
              rel="noreferrer"
              onClick={() => setOpen(false)}
              className="btn-rust mt-2"
            >
              Mint on OpenSea
            </a>
          </div>
        </div>
      )}
    </header>
  );
}
