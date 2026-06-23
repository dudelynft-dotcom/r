// OpenSea API v2 client — fetch top collections to seed the eligible set.
// Docs: https://docs.opensea.io/reference/list_collections
//
// "Trending" and "Featured" are sourced as two different rankings of OpenSea's
// /collections list (the public API has no editorial "featured" endpoint):
//   trending  -> ordered by recent volume
//   featured  -> ordered by market cap (established / blue collections)
// Adjust ORDER_BY below if OpenSea changes the accepted enum values.

export const ORDER_BY = {
  trending: process.env.OPENSEA_TRENDING_ORDER ?? "seven_day_volume",
  featured: process.env.OPENSEA_FEATURED_ORDER ?? "market_cap",
};

function headers(requireKey = true) {
  const key = process.env.OPENSEA_API_KEY;
  if (requireKey && !key) throw new Error("OPENSEA_API_KEY is not set");
  return key
    ? { accept: "application/json", "x-api-key": key }
    : { accept: "application/json" };
}

/** Resolve a single collection by OpenSea slug -> { address, name, image, slug }.
 *  The GET /collections/{slug} endpoint works without an API key. */
export async function collectionBySlug(slug) {
  const res = await fetch(`https://api.opensea.io/api/v2/collections/${slug}`, {
    headers: headers(false),
  });
  if (!res.ok) throw new Error(`OpenSea ${res.status} for slug "${slug}"`);
  const d = await res.json();
  const eth = (d.contracts ?? []).find((x) => x.chain === "ethereum");
  if (!eth?.address) return null;
  return {
    address: eth.address.toLowerCase(),
    name: d.name ?? slug,
    image: d.image_url ?? null,
    slug,
  };
}

async function getJson(url, { retries = 3 } = {}) {
  for (let attempt = 0; ; attempt++) {
    const res = await fetch(url, { headers: headers() });
    if (res.ok) return res.json();
    if ((res.status === 429 || res.status >= 500) && attempt < retries) {
      await new Promise((r) => setTimeout(r, 800 * (attempt + 1)));
      continue;
    }
    const body = await res.text().catch(() => "");
    throw new Error(`OpenSea ${res.status}: ${body.slice(0, 200)}`);
  }
}

/**
 * Page through /api/v2/collections (ethereum) by `orderBy` until we collect
 * `limit` collections that have a real Ethereum contract. Returns
 * [{ address, name, image, slug }].
 */
export async function topCollections(orderBy, limit) {
  const out = [];
  const seen = new Set();
  let next;
  let guard = 0;

  while (out.length < limit && guard++ < 25) {
    const qs = new URLSearchParams({
      chain: "ethereum",
      order_by: orderBy,
      limit: "100",
    });
    if (next) qs.set("next", next);

    const data = await getJson(`https://api.opensea.io/api/v2/collections?${qs}`);
    for (const c of data.collections ?? []) {
      const eth = (c.contracts ?? []).find((x) => x.chain === "ethereum");
      const address = eth?.address?.toLowerCase();
      if (!address || seen.has(address)) continue;
      seen.add(address);
      out.push({
        address,
        name: c.name ?? c.collection ?? "Unknown",
        image: c.image_url ?? null,
        slug: c.collection ?? null,
      });
      if (out.length >= limit) break;
    }
    next = data.next;
    if (!next) break;
  }

  return out.slice(0, limit);
}
