// ROBARK whitelist snapshot.
//
// Sources the eligible set from OpenSea's top collections (trending + featured),
// writes it to the website (web/data/whitelist-collections.json), and optionally
// snapshots every holder of those collections into an allowlist.json mint list.
//
//   node snapshot.js              # refresh the eligible-collection list (+ images)
//   node snapshot.js --holders    # also snapshot all holders -> output/allowlist.json
//
// Env (snapshot/.env or shell):
//   OPENSEA_API_KEY   required to pull live trending/featured
//   ALCHEMY_API_KEY   required for images fallback + holder snapshot
//
import { promises as fs } from "fs";
import path from "path";
import { fileURLToPath } from "url";
import { topCollections, collectionBySlug, ORDER_BY } from "./lib/opensea.js";
import { getContractImage, getCollectionOwners } from "./lib/alchemy.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const WEB_DATA = path.resolve(__dirname, "../web/data/whitelist-collections.json");
const EXTRA_WALLETS = path.resolve(__dirname, "../web/data/extra-wallets.json");
const MANUAL = path.resolve(__dirname, "manual.json");
const OUT_DIR = path.resolve(__dirname, "output");

const TRENDING_COUNT = Number(process.env.TRENDING_COUNT ?? 20);
const FEATURED_COUNT = Number(process.env.FEATURED_COUNT ?? 20);
const wantHolders = process.argv.includes("--holders");

const log = (...a) => console.log(...a);

async function loadExisting() {
  try {
    return JSON.parse(await fs.readFile(WEB_DATA, "utf8"));
  } catch {
    return { trending: [], featured: [] };
  }
}

/** Ensure every collection has a PFP image (OpenSea -> Alchemy fallback). */
async function fillImages(list) {
  for (const c of list) {
    if (c.image) continue;
    const { image, name } = await getContractImage(c.address);
    c.image = image;
    if (!c.name || c.name === "Unknown") c.name = name ?? c.name;
    log(`   image ${String(c.name ?? "").slice(0, 28).padEnd(28)} ${c.image ? "OK" : "—"}`);
  }
  return list;
}

async function readJson(p, fallback) {
  try {
    return JSON.parse(await fs.readFile(p, "utf8"));
  } catch {
    return fallback;
  }
}

/** Apply manual.json: drop removeNames, resolve+append addSlugs (keyless). */
async function applyManual(set) {
  const manual = await readJson(MANUAL, { addSlugs: [], removeNames: [] });
  const removeNames = new Set((manual.removeNames ?? []).map((n) => n.trim().toLowerCase()));

  if (removeNames.size) {
    for (const tier of ["trending", "featured"]) {
      const before = (set[tier] ?? []).length;
      set[tier] = (set[tier] ?? []).filter((c) => !removeNames.has(String(c.name).trim().toLowerCase()));
      if (before - set[tier].length) log(`   [manual] removed ${before - set[tier].length} from ${tier}`);
    }
  }

  const have = new Set([...(set.trending ?? []), ...(set.featured ?? [])].map((c) => c.address));
  for (const slug of manual.addSlugs ?? []) {
    try {
      const c = await collectionBySlug(slug);
      if (!c) { log(`   [manual] ${slug}: no ETH contract`); continue; }
      if (have.has(c.address)) { log(`   [manual] ${slug}: already present`); continue; }
      have.add(c.address);
      (set.featured ??= []).push(c);
      log(`   [manual] +${c.name} (${slug})`);
    } catch (e) {
      log(`   [manual] ${slug}: ${e.message}`);
    }
  }
  return set;
}

async function buildEligibleSet() {
  if (!process.env.OPENSEA_API_KEY) {
    log("[!] OPENSEA_API_KEY not set — keeping the existing eligible set, only refreshing images.");
    const existing = await loadExisting();
    await fillImages([...(existing.trending ?? []), ...(existing.featured ?? [])]);
    return existing;
  }

  log(`[1/2] OpenSea: top ${TRENDING_COUNT} trending (${ORDER_BY.trending}) + top ${FEATURED_COUNT} featured (${ORDER_BY.featured})`);
  const trending = await topCollections(ORDER_BY.trending, TRENDING_COUNT);

  // featured: pull extra, then drop anything already in trending
  const trendAddrs = new Set(trending.map((c) => c.address));
  const featuredRaw = await topCollections(ORDER_BY.featured, FEATURED_COUNT + TRENDING_COUNT);
  const featured = featuredRaw.filter((c) => !trendAddrs.has(c.address)).slice(0, FEATURED_COUNT);

  log(`      trending=${trending.length} featured=${featured.length}`);
  log("[2/2] resolving collection images…");
  await fillImages([...trending, ...featured]);

  return { generatedAt: new Date().toISOString(), trending, featured };
}

async function snapshotHolders(collections) {
  log(`\n[holders] snapshotting owners of ${collections.length} collections…`);
  // wallet -> Set(collection names) held from the eligible set
  const wallets = new Map();
  for (const c of collections) {
    process.stdout.write(`   ${String(c.name ?? "").slice(0, 28).padEnd(28)} `);
    let owners;
    try {
      owners = await getCollectionOwners(c.address);
    } catch (e) {
      log(`ERR ${e.message}`);
      continue;
    }
    for (const w of owners) {
      if (!wallets.has(w)) wallets.set(w, new Set());
      wallets.get(w).add(c.name);
    }
    log(`${owners.size} owners (running total ${wallets.size})`);
  }

  const entries = {};
  for (const [w, cols] of wallets) entries[w] = { eligible: true, collections: [...cols] };

  // merge manually-added supporter wallets (from X)
  const extra = await readJson(EXTRA_WALLETS, { wallets: [] });
  let supporters = 0;
  for (const raw of extra.wallets ?? []) {
    const w = String(raw).toLowerCase();
    if (!/^0x[0-9a-f]{40}$/.test(w)) continue;
    if (!entries[w]) { entries[w] = { eligible: true, collections: ["Supporter (X)"], supporter: true }; supporters++; }
    else entries[w].supporter = true;
  }
  if (supporters) log(`[holders] + ${supporters} supporter wallets from X`);

  const all = Object.keys(entries);
  await fs.mkdir(OUT_DIR, { recursive: true });
  const allowlist = {
    generatedAt: new Date().toISOString(),
    walletCount: all.length,
    holderCount: wallets.size,
    supporterCount: supporters,
    collectionCount: collections.length,
    entries,
  };
  await fs.writeFile(path.join(OUT_DIR, "allowlist.json"), JSON.stringify(allowlist));
  await fs.writeFile(path.join(OUT_DIR, "allowlist-wallets.txt"), all.join("\n"));
  log(`\n[holders] ${all.length.toLocaleString()} unique eligible wallets (${wallets.size} holders + ${supporters} supporters)`);
  log(`          output/allowlist.json + output/allowlist-wallets.txt`);
}

async function main() {
  const set = await buildEligibleSet();

  log("[manual] applying manual.json curation…");
  await applyManual(set);
  await fillImages([...(set.trending ?? []), ...(set.featured ?? [])]);

  const payload = {
    _note: "Auto-generated by snapshot/snapshot.js from OpenSea top collections.",
    generatedAt: set.generatedAt ?? new Date().toISOString(),
    trending: set.trending ?? [],
    featured: set.featured ?? [],
  };
  await fs.writeFile(WEB_DATA, JSON.stringify(payload, null, 2));
  const total = payload.trending.length + payload.featured.length;
  log(`\n[web] wrote ${total} eligible collections -> ${path.relative(process.cwd(), WEB_DATA)}`);

  if (wantHolders) {
    await snapshotHolders([...payload.trending, ...payload.featured]);
  } else {
    log("\n(tip) re-run with --holders to also snapshot every holder into output/allowlist.json");
  }
}

main().catch((e) => {
  console.error("\n[FATAL]", e.message);
  process.exit(1);
});
