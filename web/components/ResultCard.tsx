import { type CheckResult, SNAPSHOT_AT } from "@/lib/eligibility";
import { SITE, MINT_PRICE_ETH, MINT_PRICE_PUBLIC_ETH, COLLECTION } from "@/lib/config";
import { CollectionCard } from "./CollectionCard";

const SNAP_DATE = SNAPSHOT_AT
  ? new Date(SNAPSHOT_AT).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" })
  : null;

// X's current intent endpoint (deep-links the mobile app reliably).
const intent = (text: string) => `https://x.com/intent/post?text=${encodeURIComponent(text)}`;

function shareTweetUrl() {
  return intent(`I'm on the ROBARK allowlist and approved to mint.

5,555 pixel NFTs on Ethereum. Mint June 29 at ${MINT_PRICE_ETH} ETH.

Check your eligibility: ${SITE.url}/checker

@${SITE.twitterHandle} #ROBARK`);
}

// deterministic ROBARK for this wallet
const dogFor = (addr: string) => parseInt(addr.slice(2, 10), 16) % COLLECTION.totalSupply;

export function ResultCard({
  result,
  openseaUrl,
  onCheckAnother,
}: {
  result: CheckResult;
  openseaUrl: string;
  onCheckAnother?: () => void;
}) {
  const eligible = result.phase === "allowlist";
  const dog = dogFor(result.address);

  const aText = eligible ? "text-robark-green" : "text-robark-red";
  const aBorder = eligible ? "border-robark-green" : "border-robark-red";
  const aBg = eligible ? "bg-robark-green" : "bg-robark-red";
  const tierLabel = result.tier === 1 ? "Tier 1" : result.tier === 2 ? "Tier 2" : null;

  return (
    <div className={`relative overflow-hidden border-2 ${aBorder} bg-robark-ink`}>
      {/* top bar */}
      <div className="flex items-center justify-between border-b border-robark-line bg-robark-black px-5 py-3">
        <div className="flex items-center gap-2.5">
          <span className="h-5 w-5 overflow-hidden border border-robark-line bg-robark-cream">
            <img src={`/api/art/${dog}.svg`} alt="" className="h-full w-full" />
          </span>
          <span className="font-pixel text-[11px] text-robark-white">ROBARK</span>
        </div>
        {SNAP_DATE && (
          <span className="font-mono text-[10px] uppercase tracking-[0.18em] text-robark-mute">
            Snapshot · {SNAP_DATE}
          </span>
        )}
      </div>

      {/* hero: dog + verdict */}
      <div className={`relative grid items-center gap-5 p-6 sm:grid-cols-[150px_1fr] sm:p-8 ${eligible ? "bg-robark-green/10" : "bg-robark-red/10"}`}>
        <div className="pointer-events-none absolute inset-0 bg-dot-mono [background-size:14px_14px] opacity-30" />
        <div className={`relative mx-auto w-[150px] overflow-hidden border-2 ${aBorder} bg-robark-cream sm:mx-0`}>
          <img src={`/api/art/${dog}.svg`} alt="ROBARK" className="block aspect-square w-full" />
        </div>

        <div className="relative text-center sm:text-left">
          <p className="font-mono text-[11px] text-robark-mute">{result.address.slice(0, 12)}…{result.address.slice(-10)}</p>
          <h3 className={`mt-2 font-display text-3xl font-bold leading-none sm:text-4xl ${aText}`}>
            {eligible ? "ALLOWLISTED" : "NOT ELIGIBLE"}
          </h3>
          <div className="mt-3 flex flex-wrap items-center justify-center gap-2 sm:justify-start">
            <span className={`inline-flex items-center gap-1.5 border ${aBorder} ${aText} px-2.5 py-1 font-mono text-[11px] font-bold uppercase tracking-[0.15em]`}>
              {eligible ? (
                <><svg width="13" height="13" viewBox="0 0 24 24" fill="none"><path d="m5 13 4 4L19 7" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" /></svg> Approved to mint</>
              ) : (
                <><svg width="12" height="12" viewBox="0 0 24 24" fill="none"><path d="M6 6l12 12M18 6 6 18" stroke="currentColor" strokeWidth="3" strokeLinecap="round" /></svg> Not on the list</>
              )}
            </span>
            {eligible && tierLabel && (
              <span className="inline-flex items-center bg-robark-green px-2.5 py-1 font-mono text-[11px] font-bold uppercase tracking-[0.15em] text-robark-black">
                {tierLabel}{result.tier === 1 ? " · mints first" : ""}
              </span>
            )}
          </div>
          <p className="mt-3 text-sm text-robark-soft">
            {eligible
              ? `${result.matches.length ? `Qualified by ${result.matches.length} eligible collection${result.matches.length === 1 ? "" : "s"}.` : "Verified supporter from X."}${result.tier === 1 ? " You're in Tier 1 — the top-holder window mints first." : result.tier === 2 ? " You're in Tier 2 — mints after Tier 1." : ""}`
              : "No eligible collection in this wallet — request a spot below or mint public."}
          </p>
        </div>
      </div>

      {/* qualifying collections */}
      {eligible && result.matches.length > 0 && (
        <div className="border-t border-robark-line p-6 sm:p-8">
          <p className="eyebrow mb-3 text-robark-green">Holds {result.matches.length} eligible</p>
          <div className="grid grid-cols-3 gap-3 sm:grid-cols-5">
            {result.matches.slice(0, 10).map((m) => (
              <CollectionCard key={m.address} name={m.name} image={m.image} held />
            ))}
          </div>
        </div>
      )}

      {/* stat row: price · supply · status */}
      <div className="grid grid-cols-3 divide-x divide-robark-line border-t border-robark-line">
        <Stat label="Mint Price" value={`${eligible ? MINT_PRICE_ETH : MINT_PRICE_PUBLIC_ETH} Ξ`} accent={eligible ? aText : undefined} />
        <Stat label="Supply" value={COLLECTION.totalSupply.toLocaleString()} />
        <Stat label={eligible ? "Phase" : "Access"} value={eligible ? (tierLabel ?? "Allowlist") : "Public"} accent={aText} />
      </div>

      {/* actions */}
      <div className="border-t border-robark-line p-6 sm:p-8">
        {!eligible && (
          <div className="mb-5 border border-robark-line bg-robark-black p-4">
            <p className="text-sm text-robark-soft">
              Not on the snapshot? You can still earn a spot. Complete a few quick X tasks and submit your wallet to the public whitelist.
            </p>
            <a href="/whitelist" className="btn-rust mt-3 w-full sm:w-auto">
              Apply for the whitelist →
            </a>
          </div>
        )}

        <div className="flex flex-wrap items-center gap-3">
          {eligible ? (
            <>
              <a href={openseaUrl} target="_blank" rel="noreferrer" className="btn inline-flex bg-robark-green text-robark-black hover:bg-robark-greendk active:translate-y-px">
                You&apos;re in — Mint on OpenSea
              </a>
              <a href={shareTweetUrl()} target="_blank" rel="noreferrer" className="btn-line">
                <XIcon /> Tell your friends
              </a>
            </>
          ) : (
            <a href={openseaUrl} target="_blank" rel="noreferrer" className="btn-line">Mint in Public Phase</a>
          )}
          {onCheckAnother && (
            <button onClick={onCheckAnother} className="btn-line">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none"><path d="M3 12a9 9 0 0 1 15-6.7L21 8M21 3v5h-5M21 12a9 9 0 0 1-15 6.7L3 16m0 5v-5h5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" /></svg>
              Check another wallet
            </button>
          )}
        </div>
      </div>

      {/* watermark */}
      <div className="flex items-center justify-between border-t border-robark-line bg-robark-black px-5 py-2.5 font-mono text-[10px] uppercase tracking-[0.18em] text-robark-mute">
        <span>{SITE.domain.toLowerCase()}</span>
        <span>24-hour degen mint</span>
      </div>
    </div>
  );
}

function Stat({ label, value, accent }: { label: string; value: string; accent?: string }) {
  return (
    <div className="px-3 py-5 text-center">
      <div className={`font-mono text-xl font-bold sm:text-2xl ${accent ?? "text-robark-white"}`}>{value}</div>
      <div className="mt-1 font-mono text-[10px] uppercase tracking-[0.18em] text-robark-mute">{label}</div>
    </div>
  );
}

function XIcon() {
  return <svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" /></svg>;
}
