# Deploying ROBARK.IO to Railway

The site is the Next.js app in **`web/`**. The whitelist checker reads the
**bundled snapshot** (`web/data/snapshot.json`), so **no API keys or secrets are
needed at runtime** — only two public config vars.

---

## What ships

- `web/` — the Next.js app (build + serve)
- `web/data/snapshot.json` (4.8 MB) — the frozen eligibility snapshot the checker reads
- `web/data/whitelist-collections.json`, `robark-traits.json`, `extra-wallets.json`

All of these are committed (only `data/allowlist.json` is git-ignored, and the
web app doesn't use it).

---

## Option A — Railway CLI (fastest, no GitHub needed)

```bash
npm i -g @railway/cli
railway login

cd web
railway init                 # create a new project/service
railway up                   # uploads web/ and builds it

# set the two public vars
railway variables --set NEXT_PUBLIC_MINT_START=2026-06-29T09:00:00Z
railway variables --set NEXT_PUBLIC_SITE_URL=https://YOUR-APP.up.railway.app

railway domain               # generate a public URL
```

Because you run `railway up` **from inside `web/`**, that folder is the build
root — Nixpacks auto-detects Next.js and runs `npm install → build → start`.

After you get the real domain (or attach a custom one), update
`NEXT_PUBLIC_SITE_URL` to it and redeploy so share links/OG tags are correct.

## Option B — Deploy from GitHub

1. Push the repo to GitHub (this folder isn't a git repo yet):
   ```bash
   cd c:/Users/USER/Downloads/ROBARK.IO
   git init && git add . && git commit -m "ROBARK site"
   git branch -M main && git remote add origin <your-repo> && git push -u origin main
   ```
2. Railway → **New Project → Deploy from GitHub repo**.
3. Service **Settings → Source → Root Directory = `web`** (the app lives in the subfolder).
4. Railway auto-detects Next.js (Nixpacks) and uses `web/railway.json`
   (build = NIXPACKS, start = `npm run start`).
5. **Settings → Variables**, add:
   | Variable | Value |
   | --- | --- |
   | `NEXT_PUBLIC_MINT_START` | `2026-06-29T09:00:00Z` |
   | `NEXT_PUBLIC_SITE_URL` | `https://<your-domain>` |
6. **Settings → Networking → Generate Domain** (or add a custom domain).

---

## Notes

- **Node**: pinned to ≥18.18 (`.nvmrc` = 20, `engines` in package.json).
- **Port/host**: `start` is `next start -H 0.0.0.0`; Next reads Railway's `$PORT` automatically.
- **No secrets in prod.** `ALCHEMY_API_KEY` / `FAL_KEY` / Pinata keys are only used
  by the offline scripts in `snapshot/` and `art-pipeline/` — never by the website.
- **Updating the snapshot / collections later**: re-run the snapshot locally
  (`cd snapshot && python make_snapshot.py`), commit the changed
  `web/data/snapshot.json` + `whitelist-collections.json`, and redeploy.
- **Before mint**: set the real **OpenSea URL** (`SITE.opensea`) and **X handle**
  (`SITE.twitterHandle`) in `web/lib/config.ts`, then redeploy.
```
