/**
 * ROBARK.IO central configuration.
 * Everything that changes between testnet/mainnet or marketing tweaks lives here.
 * Values prefixed with NEXT_PUBLIC_ can be overridden via .env.local.
 */

export const SITE = {
  name: "ROBARK",
  domain: "ROBARK.IO",
  tagline: "The 24-Hour Degen Mint",
  description:
    "10,000 pixel-bred Shibas on Ethereum. No whitelist forms. We snapshot the chain — if you hold, you're in.",
  // public site URL (used for share links). Override with NEXT_PUBLIC_SITE_URL.
  url: process.env.NEXT_PUBLIC_SITE_URL ?? "https://robark.io",
  // social — replace with real handles
  twitter: "https://x.com/robark_io",
  // official X handle (no @) — used in BOTH the eligible share tweet and the
  // not-eligible WL-request tweet. Swap this when the official account is ready.
  twitterHandle: "robark_io",
  discord: "https://discord.gg/robark",
  opensea: "https://opensea.io/collection/robark",
  etherscan: "https://etherscan.io",
} as const;

export const MINT_PRICE_ETH = "0.0003"; // allowlist (Tier 1 / Tier 2)
export const MINT_PRICE_PUBLIC_ETH = "0.10"; // public stage

export const ANNOUNCEMENT = {
  // Checker "@robark_io just tweeted" notification + the /whitelist QUOTE task.
  tweetUrl: "https://x.com/i/status/2069578100644413930",
  // The /whitelist LIKE + RETWEET task.
  likeRtTweetUrl: "https://x.com/i/status/2069774644987535540",
} as const;

export const COLLECTION = {
  totalSupply: 5_555,
  // mint configuration — wire to the real contract when deployed
  price: {
    phase1: "0.0", // bluechip + 10+ holders (free / configurable)
    phase2: "0.005", // 10+ holders
    public: "0.01",
  },
  maxPerWallet: {
    phase1: 3,
    phase2: 2,
    public: 5,
  },
} as const;

/**
 * Mint window — a single rolling 24h "degen" event split into phases.
 * Set MINT_START via env once the date is final. Defaults to a placeholder.
 */
// Mint goes live Monday, June 29, 2026 (09:00 UTC). Override via env if it moves.
export const MINT_START_ISO =
  process.env.NEXT_PUBLIC_MINT_START ?? "2026-06-29T09:00:00Z";

export const PHASES = [
  {
    id: "tier1",
    name: "Tier 1 — Allowlist",
    badge: "TOP HOLDERS",
    time: "Jun 29 · 09:00 UTC",
    price: "0.0003",
    limit: "1 / wallet",
    rule: "Top holders (most eligible collections). Mints first.",
  },
  {
    id: "tier2",
    name: "Tier 2 — Allowlist",
    badge: "ALLOWLIST",
    time: "Jun 29 · 12:00 UTC",
    price: "0.0003",
    limit: "1 / wallet",
    rule: "The rest of the allowlist + X supporters.",
  },
  {
    id: "public",
    name: "Public",
    badge: "OPEN",
    time: "Jun 29 · 15:00 UTC",
    price: "0.10",
    limit: "11 / wallet",
    rule: "Open to everyone, while supply lasts. Ends Jul 1.",
  },
] as const;

/** Whitelist is auto-built from a curated snapshot of top OpenSea collections. */
export const WHITELIST = {
  trendingCount: 20,
  featuredCount: 20,
} as const;

/** Contract — fill in after deployment. Leave zero address to disable live mint. */
export const CONTRACT = {
  address:
    (process.env.NEXT_PUBLIC_CONTRACT_ADDRESS as `0x${string}`) ??
    "0x0000000000000000000000000000000000000000",
  chainId: Number(process.env.NEXT_PUBLIC_CHAIN_ID ?? 1),
} as const;

export const isContractLive =
  CONTRACT.address.toLowerCase() !==
  "0x0000000000000000000000000000000000000000";
