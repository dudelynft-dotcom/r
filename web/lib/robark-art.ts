/**
 * ROBARK pixel-art renderer (TypeScript port of art-pipeline/mutts/generate.py).
 * Pure, deterministic — turns a token's traits into the exact same 24x24 SVG the
 * collection was generated with. Used by the /api/art and /api/metadata routes
 * so the art is served live from the site (no IPFS/file hosting needed).
 */

export type Traits = {
  Background: string;
  Fur: string;
  Shirt: string;
  Eyes: string;
  Mouth: string;
  Hat: string;
  Accessory: string;
};

const INK = "#1b1714";
const CREAM = "#f5f0e2";
const ACCENT = "#c0492f";
const ACCENT_L = "#e0917a";
const GOLD = "#c79a44";

const BGS: Record<string, string> = {
  Bone: "#e6dfce", Mist: "#d3d9d6", Haze: "#ccd5dd", Clay: "#e3d2c2", Ash: "#cdccc6",
};
// fur: [base, shadow, muzzle]
const FURS: Record<string, [string, string, string]> = {
  Sand: ["#d0a868", "#a67e48", "#e3c690"],
  Wheat: ["#e2cc99", "#b9a46f", "#f0e1bc"],
  Stone: ["#a7a59b", "#7b796f", "#c5c3ba"],
  Cocoa: ["#8b6043", "#5f3f2a", "#a67a58"],
  Soot: ["#332f2a", "#191310", "#4d4840"],
  Chalk: ["#e5e0d2", "#bbb6a7", "#f3efe4"],
  Moss: ["#92a26d", "#6a794b", "#b0bc8d"],
  Steel: ["#7e8fa9", "#596984", "#9eacc2"],
};
// shirt: null (none) or [base, outline]
const SHIRTS: Record<string, [string, string] | null> = {
  None: null, Rust: [ACCENT, "#8d2f1d"], Navy: ["#36415d", "#222a40"],
  Olive: ["#6f7a4c", "#4d5533"], Stone: ["#7c7a70", "#56544c"], Bone: ["#d6d0bf", "#a9a392"],
};

type Px = [number, number, string];
const rect = (px: Px[], x1: number, y1: number, x2: number, y2: number, c: string) => {
  for (let y = y1; y <= y2; y++) for (let x = x1; x <= x2; x++) px.push([x, y, c]);
};

function basePortrait(fur: [string, string, string], shirt: [string, string] | null): Px[] {
  const [B, D, M] = fur;
  const O = INK;
  const px: Px[] = [];

  const head: Record<number, [number, number]> = { 4: [8, 15], 5: [7, 16], 6: [6, 17], 7: [6, 17], 8: [6, 17], 9: [7, 16], 10: [8, 15] };
  for (const y in head) { const [c0, c1] = head[y]; rect(px, c0, +y, c1, +y, B); }

  const earL: Record<number, [number, number]> = { 4: [6, 7], 5: [5, 7], 6: [4, 7], 7: [4, 6], 8: [4, 6], 9: [4, 6], 10: [4, 6], 11: [5, 6], 12: [5, 6] };
  for (const y in earL) { const [c0, c1] = earL[y]; rect(px, c0, +y, c1, +y, B); rect(px, 23 - c1, +y, 23 - c0, +y, B); }
  for (let y = 6; y <= 10; y++) { px.push([6, y, D], [17, y, D]); }
  for (const [x, y] of [[6, 4], [5, 5], [4, 6], [4, 7], [4, 8], [4, 9], [4, 10], [5, 11], [5, 12], [6, 12]] as const) { px.push([x, y, O], [23 - x, y, O]); }

  for (let x = 8; x <= 15; x++) px.push([x, 4, O]);
  for (const [x, y] of [[7, 5], [16, 5], [6, 6], [17, 6], [6, 7], [17, 7], [6, 8], [17, 8], [7, 9], [16, 9]] as const) px.push([x, y, O]);
  for (const x of [8, 9, 14, 15]) px.push([x, 10, O]);

  const snout: Record<number, [number, number]> = { 11: [9, 14], 12: [9, 14], 13: [10, 13], 14: [10, 13] };
  for (const y in snout) { const [c0, c1] = snout[y]; rect(px, c0, +y, c1, +y, M); }
  for (const [x, y] of [[8, 11], [15, 11], [8, 12], [15, 12], [9, 13], [14, 13], [9, 14], [14, 14]] as const) px.push([x, y, O]);
  rect(px, 10, 15, 13, 15, O);
  rect(px, 11, 12, 12, 13, O);
  px.push([7, 9, D], [16, 9, D]);

  rect(px, 10, 16, 13, 17, B);
  px.push([9, 16, O], [9, 17, O], [14, 16, O], [14, 17, O], [13, 16, D], [13, 17, D]);

  const [SB, SO] = shirt === null ? [D, O] : shirt;
  rect(px, 7, 18, 16, 18, SB); rect(px, 5, 19, 18, 19, SB); rect(px, 3, 20, 20, 20, SB);
  rect(px, 1, 21, 22, 21, SB); rect(px, 0, 22, 23, 23, SB);
  px.push([7, 18, SO], [16, 18, SO], [5, 19, SO], [18, 19, SO]);
  rect(px, 3, 20, 4, 20, SO); rect(px, 19, 20, 20, 20, SO);
  rect(px, 1, 21, 2, 21, SO); rect(px, 21, 21, 22, 21, SO);
  rect(px, 0, 22, 1, 22, SO); rect(px, 22, 22, 23, 22, SO);
  if (shirt !== null) { rect(px, 10, 18, 13, 18, B); rect(px, 11, 19, 12, 19, B); }
  return px;
}

function eyes(kind: string): Px[] {
  const O = INK, W = CREAM, px: Px[] = [];
  for (const [ex, far] of [[9, false], [13, true]] as const) {
    const ey = 8;
    if (kind === "Normal") px.push([ex, ey, W], [ex + 1, ey, W], [ex, ey + 1, O], [ex + 1, ey + 1, W]);
    else if (kind === "Sleepy") px.push([ex, ey + 1, O], [ex + 1, ey + 1, O]);
    else if (kind === "Blank") rect(px, ex, ey, ex + 1, ey + 1, W);
    else if (kind === "Wink") {
      if (!far) px.push([ex, ey, W], [ex + 1, ey, W], [ex, ey + 1, O], [ex + 1, ey + 1, W]);
      else px.push([ex, ey + 1, O], [ex + 1, ey + 1, O]);
    } else if (kind === "Laser") { rect(px, ex, ey, ex + 1, ey + 1, ACCENT); px.push([ex - 1, ey, ACCENT], [ex - 2, ey, ACCENT_L]); }
    else if (kind === "Shades") { rect(px, ex - 1, ey, ex + 1, ey + 1, INK); px.push([ex, ey, CREAM]); }
  }
  if (kind === "Shades") px.push([11, 8, INK], [12, 8, INK]);
  return px;
}

function mouth(kind: string): Px[] {
  const O = INK, px: Px[] = [];
  if (kind === "Smile") px.push([10, 14, O], [11, 15, O], [12, 15, O], [13, 14, O]);
  else if (kind === "Neutral") px.push([10, 14, O], [11, 14, O], [12, 14, O], [13, 14, O]);
  else if (kind === "Tongue") px.push([10, 14, O], [11, 15, O], [12, 15, O], [13, 14, O], [11, 15, ACCENT_L], [12, 15, ACCENT_L]);
  else if (kind === "Fang") px.push([10, 14, O], [11, 15, O], [12, 15, O], [13, 14, O], [10, 15, CREAM], [13, 15, CREAM]);
  return px;
}

function hat(kind: string): Px[] {
  const O = INK, px: Px[] = [];
  if (kind === "None") return px;
  if (kind === "Beanie") {
    for (let x = 6; x <= 17; x++) px.push([x, 3, ACCENT]);
    for (let x = 7; x <= 16; x++) px.push([x, 2, ACCENT]);
    for (let x = 8; x <= 15; x++) px.push([x, 1, ACCENT]);
    px.push([11, 0, CREAM], [12, 0, CREAM]);
    for (let x = 6; x <= 17; x++) px.push([x, 4, O]);
  } else if (kind === "Cap") {
    for (let x = 7; x <= 16; x++) px.push([x, 2, INK], [x, 3, INK]);
    for (let x = 15; x <= 18; x++) px.push([x, 4, INK]);
    rect(px, 10, 3, 13, 3, ACCENT);
    for (let x = 7; x <= 16; x++) px.push([x, 4, O]);
  } else if (kind === "Crown") {
    for (let i = 0; i < 5; i++) { const x = 7 + i * 2; px.push([x, 3, GOLD], [x, 2, GOLD], [x, 1, GOLD]); }
    for (let x = 7; x <= 16; x++) px.push([x, 3, GOLD]);
    for (let x = 7; x <= 16; x++) px.push([x, 4, O]);
    px.push([11, 3, ACCENT], [12, 3, ACCENT]);
  } else if (kind === "Halo") {
    for (let x = 8; x <= 15; x++) px.push([x, 0, GOLD]);
    px.push([7, 1, GOLD], [16, 1, GOLD]);
  } else if (kind === "Cone") {
    px.push([12, 0, ACCENT], [11, 1, ACCENT], [12, 1, ACCENT],
      [10, 2, ACCENT], [11, 2, CREAM], [12, 2, ACCENT], [13, 2, ACCENT],
      [10, 3, ACCENT], [11, 3, ACCENT], [12, 3, CREAM], [13, 3, ACCENT], [14, 3, ACCENT]);
    for (let x = 9; x <= 14; x++) px.push([x, 4, O]);
  }
  return px;
}

function accessory(kind: string): Px[] {
  const O = INK, px: Px[] = [];
  if (kind === "None") return px;
  if (kind === "Cigar") px.push([14, 14, O], [15, 14, O], [16, 14, O], [17, 14, ACCENT], [17, 13, ACCENT_L], [18, 12, CREAM]);
  else if (kind === "Bone") {
    for (let x = 8; x <= 15; x++) px.push([x, 14, CREAM]);
    px.push([8, 13, CREAM], [15, 13, CREAM], [8, 15, CREAM], [15, 15, CREAM], [7, 14, O], [16, 14, O]);
  } else if (kind === "Collar") {
    for (let x = 9; x <= 14; x++) px.push([x, 17, ACCENT]);
    px.push([11, 17, GOLD], [12, 17, GOLD]);
  } else if (kind === "Chain") {
    for (let x = 6; x <= 17; x++) px.push([x, 19, x % 2 === 0 ? GOLD : "#e6c87e"]);
    rect(px, 10, 20, 13, 21, GOLD); px.push([11, 21, O], [12, 21, O]);
  } else if (kind === "Bandana") {
    for (let x = 7; x <= 16; x++) px.push([x, 5, ACCENT], [x, 4, ACCENT]);
    px.push([16, 6, ACCENT], [17, 6, ACCENT]);
    for (let x = 7; x <= 16; x++) px.push([x, 6, O]);
  }
  return px;
}

function compose(t: Traits): Px[] {
  return [
    ...basePortrait(FURS[t.Fur], SHIRTS[t.Shirt]),
    ...eyes(t.Eyes), ...mouth(t.Mouth), ...hat(t.Hat), ...accessory(t.Accessory),
  ];
}

export function robarkSvg(t: Traits, size = 1024): string {
  const body = compose(t)
    .map(([x, y, c]) => `<rect x="${x}" y="${y}" width="1" height="1" fill="${c}"/>`)
    .join("");
  const bg = BGS[t.Background] ?? "#e6dfce";
  return (
    `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="${size}" height="${size}" ` +
    `shape-rendering="crispEdges" style="background:${bg};image-rendering:pixelated">` +
    `<rect width="24" height="24" fill="${bg}"/>${body}</svg>`
  );
}

export const TRAIT_ORDER: (keyof Traits)[] = ["Background", "Fur", "Shirt", "Eyes", "Mouth", "Hat", "Accessory"];
