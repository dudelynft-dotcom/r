import Link from "next/link";
import { Countdown } from "@/components/Countdown";
import { Marquee } from "@/components/Marquee";
import { CollectionCard } from "@/components/CollectionCard";
import { SITE, COLLECTION, PHASES, MINT_START_ISO, MINT_PRICE_ETH } from "@/lib/config";
import { SNAPSHOT_AT, ELIGIBLE_COLLECTIONS } from "@/lib/eligibility";
import { snapshotWalletCount } from "@/lib/snapshot";

const SNAP_DATE = SNAPSHOT_AT
  ? new Date(SNAPSHOT_AT).toLocaleDateString("en-US", { month: "long", day: "numeric", year: "numeric" })
  : null;

// a single tasteful art strip — no more wall-to-wall sneak peeks
const STRIP = [5, 23, 44, 91, 168, 333, 420, 612, 808, 1009, 1337, 1500, 1969, 2222, 2480, 2750, 3333, 3690, 4040, 4242];
const HERO = 42;
// 5 singles + the 2×2 feature fills the 3-col grid exactly (no empty tile)
const HERO_GRID = [777, 1234, 2048, 3690, 4555];

function Dog({ id }: { id: number }) {
  return (
    <div className="tile" style={{ aspectRatio: "1/1" }}>
      <img src={`/api/art/${id}.svg`} alt="ROBARK" className="h-full w-full" />
    </div>
  );
}

export default function HomePage() {
  const wallets = snapshotWalletCount();
  const stats = [
    { k: "Supply", v: COLLECTION.totalSupply.toLocaleString() },
    { k: "Eligible Collections", v: ELIGIBLE_COLLECTIONS.length.toString() },
    { k: "Wallets Snapshotted", v: wallets ? wallets.toLocaleString() : "—" },
    { k: "Mint Price", v: `${MINT_PRICE_ETH} Ξ` },
    { k: "Mint Window", v: "24H" },
  ];

  const steps = [
    {
      n: "01",
      t: "Snapshot taken",
      d: `We snapshotted ${ELIGIBLE_COLLECTIONS.length} top Ethereum collections${SNAP_DATE ? ` on ${SNAP_DATE}` : ""}. ${wallets ? wallets.toLocaleString() : "Every"} holder wallets are frozen — the list is final.`,
    },
    {
      n: "02",
      t: "Check instantly",
      d: "Paste any wallet. Eligibility is read straight from the frozen snapshot — no wallet connect, no forms, no live calls. Sub-second.",
    },
    {
      n: "03",
      t: "Mint on OpenSea",
      d: `Allowlist window first, then public — a single 24-hour degen mint at ${MINT_PRICE_ETH} ETH. No clunky mint dApp.`,
    },
  ];

  return (
    <>
      {/* ───────── HERO ───────── */}
      <section className="relative overflow-hidden border-b-2 border-robark-line">
        <div className="container-x grid items-center gap-12 py-16 lg:grid-cols-[1.05fr_0.95fr] lg:py-24">
          <div className="animate-rise">
            <p className="font-mono text-xs lowercase tracking-wide text-robark-mute">
              {COLLECTION.totalSupply.toLocaleString()} on ethereum
              <span className="mx-2 text-robark-line">·</span>{MINT_PRICE_ETH} eth
              <span className="mx-2 text-robark-line">·</span>
              <span className="text-robark-rust">mint jun 29</span>
            </p>

            <h1 className="mt-6 font-display text-[2.7rem] font-bold leading-[0.98] tracking-tight text-robark-white sm:text-6xl lg:text-7xl">
              5,555 degens
              <br />
              who <span className="text-robark-rust">survived</span>
              <br />
              the crash<span className="cursor" />
            </h1>

            <p className="mt-6 max-w-md font-mono text-sm leading-relaxed text-robark-soft">
              <span className="text-robark-rust">$</span> one iconic pixel mutt, 5,555 hand-coded combos.
              allowlist is decided on-chain — hold any eligible collection and you&apos;re in.
              no forms, no connect.
            </p>

            <div className="mt-8 flex flex-wrap items-center gap-3">
              <Link href="/checker" className="btn-rust text-sm">
                Check eligibility
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none"><path d="M5 12h14m-6-6 6 6-6 6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/></svg>
              </Link>
              <a href={SITE.opensea} target="_blank" rel="noreferrer" className="btn-line text-sm">Mint on OpenSea</a>
            </div>

            <div className="mt-10">
              <p className="eyebrow mb-3">Mint goes live in</p>
              <Countdown iso={MINT_START_ISO} />
            </div>
          </div>

          <div className="win animate-rise [animation-delay:120ms]">
            <div className="win-bar">
              <span className="flex items-center gap-1.5">
                <span className="h-2.5 w-2.5 bg-robark-rust" />
                <span className="h-2.5 w-2.5 bg-robark-line" />
                <span className="h-2.5 w-2.5 bg-robark-line" />
              </span>
              <span>~/robark/gallery — 5555 items</span>
            </div>
            <div className="grid grid-cols-3 gap-2 p-2">
              <div className="col-span-2 row-span-2"><Dog id={HERO} /></div>
              {HERO_GRID.map((id) => <div key={id}><Dog id={id} /></div>)}
            </div>
            <div className="flex items-center justify-between border-t-2 border-robark-line bg-robark-black px-3 py-2 font-mono text-[11px] text-robark-mute">
              <span>hand-coded · no AI · no IPFS</span>
              <span className="text-robark-green">served live ▮</span>
            </div>
          </div>
        </div>
      </section>

      {/* ───────── STAT BAR (real numbers) ───────── */}
      <section className="border-b border-robark-line bg-robark-ink/40">
        <div className="container-x grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5">
          {stats.map((s, i) => (
            <div key={s.k} className={`px-3 py-8 text-center ${i ? "border-robark-line sm:border-l" : ""} ${i >= 3 ? "border-t sm:border-t-0" : ""}`}>
              <div className="font-mono text-2xl font-bold text-robark-white sm:text-3xl">{s.v}</div>
              <div className="mt-1.5 font-mono text-[10px] uppercase tracking-[0.18em] text-robark-mute">{s.k}</div>
            </div>
          ))}
        </div>
      </section>

      {/* ───────── HOW IT WORKS ───────── */}
      <section id="how" className="container-x py-20 lg:py-28">
        <div className="max-w-2xl">
          <p className="eyebrow">How it works</p>
          <h2 className="mt-3 font-display text-4xl font-bold text-robark-white sm:text-5xl">The snapshot decides. Instantly.</h2>
          <p className="mt-4 text-robark-soft">
            No allowlist spreadsheet, no Discord grind. Eligibility is a frozen on-chain
            snapshot you can verify yourself in one paste.
          </p>
        </div>

        <div className="mt-12 grid gap-3 lg:grid-cols-3">
          {steps.map((s) => (
            <div key={s.n} className="panel flex flex-col p-7">
              <span className="font-mono text-4xl font-bold text-robark-line">{s.n}</span>
              <h3 className="mt-4 font-display text-xl font-bold text-robark-white">{s.t}</h3>
              <p className="mt-2 flex-1 text-sm leading-relaxed text-robark-soft">{s.d}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ───────── CHECKER CTA ───────── */}
      <section className="border-y border-robark-line bg-robark-ink/40 py-16 lg:py-20">
        <div className="container-x grid items-center gap-8 lg:grid-cols-[1.2fr_1fr]">
          <div>
            <p className="eyebrow">Whitelist Checker</p>
            <h2 className="mt-3 font-display text-3xl font-bold text-robark-white sm:text-4xl">
              {wallets ? wallets.toLocaleString() : "Thousands of"} wallets already qualified.
            </h2>
            <p className="mt-3 max-w-md text-robark-soft">Paste any Ethereum address and find out if it&apos;s on the ROBARK allowlist — free, instant, no connect.</p>
          </div>
          <Link href="/checker" className="group block border border-robark-line bg-robark-black p-4 transition hover:border-robark-rust">
            <div className="flex items-center justify-between gap-3 border border-robark-line bg-robark-ink px-4 py-3">
              <span className="font-mono text-sm text-robark-mute">0x… paste a wallet</span>
              <span className="btn-rust px-3 py-1.5 text-[12px]">Check →</span>
            </div>
          </Link>
        </div>
      </section>

      {/* ───────── ELIGIBLE COLLECTIONS WALL (useful) ───────── */}
      <section id="eligible" className="container-x py-20 lg:py-28">
        <div className="flex flex-wrap items-end justify-between gap-4">
          <div>
            <p className="eyebrow">Eligible Collections</p>
            <h2 className="mt-3 font-display text-4xl font-bold text-robark-white sm:text-5xl">Hold any of these {ELIGIBLE_COLLECTIONS.length}</h2>
            <p className="mt-3 max-w-md text-robark-soft">Own an NFT from any collection below at snapshot and your wallet is on the allowlist — automatically.</p>
          </div>
          <Link href="/checker" className="btn-line text-sm">Check your wallet</Link>
        </div>

        <div className="mt-10 grid grid-cols-3 gap-3 sm:grid-cols-4 md:grid-cols-5 lg:grid-cols-7">
          {ELIGIBLE_COLLECTIONS.map((c) => (
            <CollectionCard key={c.address} name={c.name} image={c.image} />
          ))}
        </div>
      </section>

      {/* ───────── COLLECTION SNEAK PEEK (single strip) ───────── */}
      <section id="collection" className="border-y border-robark-line bg-robark-ink/40 py-16">
        <div className="container-x mb-8 flex flex-wrap items-end justify-between gap-4">
          <div>
            <p className="eyebrow">The Collection</p>
            <h2 className="mt-3 font-display text-3xl font-bold text-robark-white sm:text-4xl">5,555 unique mutts</h2>
          </div>
          <p className="max-w-xs text-sm text-robark-soft">Hand-coded pixel by pixel, served live from deterministic code — no AI, no IPFS, no two alike.</p>
        </div>
        <Marquee ids={STRIP} />
      </section>

      {/* ───────── MINT / PHASES ───────── */}
      <section id="mint" className="container-x py-20 lg:py-28">
        <div className="mx-auto max-w-2xl text-center">
          <p className="eyebrow">The 24-Hour Degen Mint</p>
          <h2 className="mt-3 font-display text-4xl font-bold text-robark-white sm:text-5xl">Mint goes live June 29</h2>
          <p className="mt-4 text-robark-soft">
            Allowlist mints at <span className="text-robark-white">0.0001 ETH</span>, public at{" "}
            <span className="text-robark-white">0.10 ETH</span>. Snapshot is final{SNAP_DATE ? ` — taken ${SNAP_DATE}` : ""}.
          </p>
        </div>

        {/* countdown */}
        <div className="mt-10 flex flex-col items-center">
          <p className="eyebrow mb-3">Mint starts in</p>
          <Countdown iso={MINT_START_ISO} />
          <p className="mt-3 font-mono text-[11px] uppercase tracking-[0.14em] text-robark-mute">June 29, 2026 · 09:00 UTC</p>
        </div>

        {/* schedule */}
        <div className="mx-auto mt-12 grid max-w-5xl gap-3 lg:grid-cols-3">
          {PHASES.map((p, i) => (
            <div key={p.id} className="panel flex flex-col p-6">
              <div className="flex items-center justify-between">
                <span className="chip">{p.badge}</span>
                <span className="font-mono text-3xl font-bold text-robark-line">0{i + 1}</span>
              </div>
              <h3 className="mt-4 font-display text-lg font-bold text-robark-white">{p.name}</h3>
              <p className="mt-1 font-mono text-[11px] uppercase tracking-[0.14em] text-robark-rust">{p.time}</p>
              <div className="mt-3 flex items-center gap-2 font-mono text-[12px]">
                <span className="font-bold text-robark-fog">{p.price} Ξ</span>
                <span className="text-robark-line">·</span>
                <span className="text-robark-soft">{p.limit}</span>
              </div>
              <p className="mt-3 flex-1 text-sm leading-relaxed text-robark-soft">{p.rule}</p>
            </div>
          ))}
        </div>

        <div className="mt-10 flex flex-wrap justify-center gap-3">
          <Link href="/checker" className="btn-line text-sm">Am I eligible?</Link>
          <a href={SITE.opensea} target="_blank" rel="noreferrer" className="btn-rust text-sm">Mint on OpenSea</a>
        </div>
      </section>

      {/* ───────── FINAL CTA ───────── */}
      <section className="border-t border-robark-line">
        <div className="container-x relative overflow-hidden py-20 text-center lg:py-28">
          <p className="mb-5 font-mono text-[12px] text-robark-mute">$ robark --check &lt;your_wallet&gt;</p>
          <h2 className="mx-auto max-w-2xl font-display text-4xl font-bold text-robark-white sm:text-5xl">
            The chain already knows if you&apos;re in.
          </h2>
          <p className="mx-auto mt-4 max-w-md text-robark-soft">Paste your wallet, find your phase, mint your mutt.</p>
          <div className="mt-8 flex flex-wrap justify-center gap-3">
            <Link href="/checker" className="btn-rust text-sm">Check my wallet</Link>
            <a href={SITE.opensea} target="_blank" rel="noreferrer" className="btn-line text-sm">View on OpenSea</a>
          </div>
        </div>
      </section>
    </>
  );
}
