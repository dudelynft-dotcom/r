# ROBARK.IO — Website

Professional, fully-blue NFT site: landing page + **whitelist checker**. No
wallet connect — the checker is paste-an-address only. Mint happens on OpenSea
(no on-chain mint page by design).

## Run
```bash
npm install
cp .env.example .env.local   # add ALCHEMY_API_KEY
npm run dev      # http://localhost:3000 (or next free port)
npm run build    # production build
```

## Environment (`.env.local`, git-ignored)
| Var | Needed for | Notes |
| --- | --- | --- |
| `ALCHEMY_API_KEY` | Live whitelist checker | Key only (not the RPC URL). dashboard.alchemy.com. Without it the checker runs in demo/allowlist mode. |
| `NEXT_PUBLIC_MINT_START` | Homepage countdown | ISO 8601 UTC |

## Pages
- `/` — landing: hero, stats, collection preview, **3 phases**, how the snapshot works, FAQ, CTA.
- `/checker` — the whitelist checker: **paste any Ethereum address → Search**. No wallet connection required.

## How the checker resolves a wallet (`app/api/check/route.ts`)
1. **Live (Alchemy):** `getContractsForOwner` returns each held collection's name, count, and OpenSea floor → convert floor to USD → count NFTs in collections with floor > $10 (spam filtered) → tag bluechips → decide phase.
2. **Allowlist fallback:** if `web/data/allowlist.json` exists (from the snapshot script), it's used.
3. **Demo:** deterministic mock so the UI is fully usable with no keys.

Eligibility rules live in `lib/config.ts` (`ELIGIBILITY`) and the decision in
`lib/eligibility.ts` (`decidePhase`). Bluechips: `lib/bluechips.ts`.

## Theme
Blue palette sampled from the demo art in `tailwind.config.ts` (`robark.*`).
Drop real hero art at `public/art/hero.png` (falls back to an SVG pixel Shiba).

## Deploy
Vercel: import the repo, set `ALCHEMY_API_KEY`, deploy. (Set the project root to `web/`.)
