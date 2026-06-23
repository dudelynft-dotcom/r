// Eligibility thresholds — keep in sync with web/lib/config.ts and eligibility.ts
export const ELIGIBILITY = {
  minNftCount: 10, // 10+ NFTs
  minFloorUsd: 10, // each counted collection must floor above $10 in ETH
};

// Curated bluechips (mainnet, lowercase). Holding one (with floor > threshold)
// unlocks Phase 1. Mirror of web/lib/bluechips.ts.
export const BLUECHIPS = {
  "0xbc4ca0eda7647a8ab7c2061c2e118a18a936f13d": "Bored Ape Yacht Club",
  "0x60e4d786628fea6478f785a6d7e704777c86a7c6": "Mutant Ape Yacht Club",
  "0xed5af388653567af2f388e6224dc7c4b3241c544": "Azuki",
  "0x49cf6f5d44e70224e2e23fdcdd2c053f30ada28b": "CloneX",
  "0x23581767a106ae21c074b2276d25e5c3e136a68b": "Moonbirds",
  "0xbd3531da5cf5857e7cfaa92426877b022e612cf8": "Pudgy Penguins",
  "0x8a90cab2b38dba80c64b7734e58ee1db38b8992e": "Doodles",
  "0x1a92f7381b9f03921564a437210bb9396471050c": "Cool Cats",
  "0x34d85c9cdeb23fa97cb08333b511ac86e1c4e258": "Otherdeed",
  "0x769272677fab02575e84945f03eca517acc544cc": "Captainz",
  "0x5af0d9827e0c53e4799bb226655a1de152a425a5": "Milady Maker",
  "0xe785e82358879f061bc3dcac6f0444462d4b5330": "World of Women",
  "0x9378368ba6b85c1fba5b131b530f5f5bedf21a18": "VeeFriends",
};

export const isBluechip = (a) => a.toLowerCase() in BLUECHIPS;
export const bluechipName = (a) => BLUECHIPS[a.toLowerCase()];
