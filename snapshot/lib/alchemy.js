// Alchemy NFT API (v3) client for the snapshot (Node, global fetch).
import { BLUECHIPS } from "./config.js";

function baseUrl() {
  const key = process.env.ALCHEMY_API_KEY;
  if (!key) throw new Error("ALCHEMY_API_KEY is not set");
  return `https://eth-mainnet.g.alchemy.com/nft/v3/${key}`;
}

export const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function getJson(url, { retries = 3 } = {}) {
  for (let attempt = 0; ; attempt++) {
    const res = await fetch(url, { headers: { accept: "application/json" } });
    if (res.ok) return res.json();
    if ((res.status === 429 || res.status >= 500) && attempt < retries) {
      await sleep(800 * (attempt + 1));
      continue;
    }
    const body = await res.text().catch(() => "");
    throw new Error(`Alchemy ${res.status}: ${body.slice(0, 160)}`);
  }
}

const MAX_PLAUSIBLE_FLOOR_USD = 500_000;

let ethUsdCache = null;
export async function getEthUsd() {
  if (ethUsdCache) return ethUsdCache;
  try {
    const j = await getJson("https://api.coinbase.com/v2/prices/ETH-USD/spot");
    const v = Number(j?.data?.amount);
    if (v > 0) return (ethUsdCache = v);
  } catch {
    /* fall through */
  }
  return (ethUsdCache = 3000);
}

/** Collection PFP image + name via getContractMetadata (OpenSea-sourced). */
export async function getContractImage(contract) {
  try {
    const d = await getJson(`${baseUrl()}/getContractMetadata?contractAddress=${contract}`);
    const osm = d.openSeaMetadata ?? {};
    const image =
      osm.imageUrl ??
      (typeof d.image === "object" ? d.image?.cachedUrl ?? d.image?.originalUrl : null) ??
      null;
    return { name: d.name ?? osm.collectionName ?? null, image };
  } catch {
    return { name: null, image: null };
  }
}

/** Owners of a collection (paginated). Returns a Set of lowercase addresses. */
export async function getCollectionOwners(contract, { maxPages = 2000 } = {}) {
  const owners = new Set();
  let pageKey;
  let pages = 0;
  do {
    const qs = new URLSearchParams({ contractAddress: contract });
    if (pageKey) qs.set("pageKey", pageKey);
    const data = await getJson(`${baseUrl()}/getOwnersForContract?${qs}`);
    for (const o of data.owners ?? []) owners.add(String(o).toLowerCase());
    pageKey = data.pageKey;
    pages++;
  } while (pageKey && pages < maxPages);
  return owners;
}

/** A wallet's collections with USD floor (spam-filtered), via getContractsForOwner. */
export async function getOwnerCollections(address, { maxPages = 20 } = {}) {
  const ethUsd = await getEthUsd();
  const out = [];
  let pageKey;
  let pages = 0;
  do {
    const qs = new URLSearchParams({ owner: address, withMetadata: "true" });
    if (pageKey) qs.set("pageKey", pageKey);
    const data = await getJson(`${baseUrl()}/getContractsForOwner?${qs}`);
    for (const c of data.contracts ?? []) {
      const addr = String(c.address).toLowerCase();
      let count = Number(c.numDistinctTokensOwned ?? c.totalBalance ?? 1) || 1;
      const spammyCount = count > 100_000;
      if (spammyCount) count = 1;
      const floorEth =
        c.openSeaMetadata?.floorPrice ?? c.opensea?.floorPrice ?? null;
      let floorUsd =
        floorEth != null && floorEth > 0
          ? Math.round(floorEth * ethUsd * 100) / 100
          : null;
      const bluechip = addr in BLUECHIPS;
      if (
        (c.isSpam && !bluechip) ||
        spammyCount ||
        (floorUsd != null && floorUsd > MAX_PLAUSIBLE_FLOOR_USD && !bluechip)
      ) {
        floorUsd = null;
      }
      out.push({ address: addr, name: c.name ?? "Unknown", count, floorUsd });
    }
    pageKey = data.pageKey;
    pages++;
  } while (pageKey && pages < maxPages);
  return out;
}
