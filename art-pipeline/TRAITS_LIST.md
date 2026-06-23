# ROBARK — Trait List (5,555 collection)

**Locked style:** flat hand-drawn comic (OK-Guy vibe) — FLUX + canny-ControlNet
(locks the FINAL pose/structure) + `Flux-Sketch-Flat-LoRA`. Same dog, same pose,
elements swap. See `art-previews/STYLE_LOCKED/`.

- **7 trait categories**, **78 total trait options**
- Combination space = 10 × 12 × 12 × 8 × 8 × 13 × 15 = **17,971,200** → 5,555 unique is trivial
- "Approx count" = weight share × 5,555 (rounded). Tune in `final_traits.yaml`.

---

## 1. FUR — 10 options  *(the dog's color)*
| Trait | Weight | ~Count /5555 |
|---|---|---|
| White | 24 | ~1,290 |
| Golden | 18 | ~970 |
| Grey | 14 | ~750 |
| Chocolate | 12 | ~645 |
| Black | 9 | ~485 |
| Cream | 9 | ~485 |
| Zombie Green | 5 | ~270 |
| Blue Merle | 4 | ~215 |
| Pink | 3 | ~160 |
| Solid Gold ✦ | 2 | ~105 |

## 2. CLOTHING — 12 options
| Trait | Weight | ~Count |
|---|---|---|
| Red Hoodie | 16 | ~745 |
| Black Suit | 13 | ~605 |
| Navy Suit | 10 | ~465 |
| Varsity Jacket | 10 | ~465 |
| Tracksuit | 10 | ~465 |
| Denim Jacket | 9 | ~420 |
| Puffer | 8 | ~370 |
| Grey Hoodie | 7 | ~325 |
| Hawaiian | 6 | ~280 |
| Tuxedo | 5 | ~230 |
| Hazmat | 3 | ~140 |
| Golden Suit ✦ | 2 | ~95 |

## 3. HEADWEAR — 12 options
| Trait | Weight | ~Count |
|---|---|---|
| None | 28 | ~1,460 |
| Red Cap | 13 | ~680 |
| Beanie | 12 | ~625 |
| Durag | 9 | ~470 |
| Bucket Hat | 8 | ~415 |
| Headphones | 7 | ~365 |
| Cowboy Hat | 6 | ~315 |
| Party Hat | 5 | ~260 |
| Crown ✦ | 4 | ~210 |
| Halo ✦ | 3 | ~155 |
| Devil Horns ✦ | 3 | ~155 |
| Flaming Head ✦ | 2 | ~105 |

## 4. EYEWEAR — 8 options
| Trait | Weight | ~Count |
|---|---|---|
| None | 34 | ~1,775 |
| Dark Shades | 20 | ~1,045 |
| Shades Up | 12 | ~625 |
| Nerd Glasses | 10 | ~520 |
| 3D Glasses | 8 | ~420 |
| Eye Patch | 7 | ~365 |
| Monocle | 5 | ~260 |
| VR Headset ✦ | 4 | ~210 |

## 5. MOUTH — 8 options
| Trait | Weight | ~Count |
|---|---|---|
| Cigarette | 30 | ~1,565 |
| Cigar | 16 | ~835 |
| Blunt | 12 | ~625 |
| Toothpick | 10 | ~520 |
| Vape | 9 | ~470 |
| Pipe | 8 | ~415 |
| Lollipop | 8 | ~415 |
| Bubblegum | 7 | ~365 |

## 6. HAND ITEM — 13 options  *(in the raised paw)*
| Trait | Weight | ~Count |
|---|---|---|
| Coffee | 14 | ~615 |
| Beer | 13 | ~570 |
| Energy Drink | 11 | ~485 |
| Phone (red chart) | 11 | ~485 |
| Money Stack | 10 | ~440 |
| Cocktail | 8 | ~350 |
| Bone | 7 | ~310 |
| Pizza | 6 | ~265 |
| Controller | 5 | ~220 |
| Gold Bar ✦ | 4 | ~175 |
| Diamond ✦ | 3 | ~130 |
| Microphone | 3 | ~130 |
| Empty Paw | 5 | ~220 |

## 7. BACKGROUND — 15 options  *(all text-free)*
| Trait | Weight | ~Count |
|---|---|---|
| Plain Color | 10 | ~440 |
| Degen Room | 12 | ~530 |
| Dim Bar | 10 | ~440 |
| Office Desk | 9 | ~395 |
| Casino Floor | 8 | ~350 |
| Neon City Night | 8 | ~350 |
| Trading Desk | 8 | ~350 |
| Money Rain | 6 | ~265 |
| Rooftop Night | 6 | ~265 |
| Sunset Beach | 5 | ~220 |
| Graveyard Night | 4 | ~175 |
| Outer Space | 4 | ~175 |
| Vaporwave ✦ | 3 | ~130 |
| Heaven Clouds ✦ | 2 | ~90 |
| Hell Flames ✦ | 1.5 | ~65 |

---

✦ = rarer / "chase" values. **Rarity Tier** (Common → Rare → Epic → Legendary →
Mythic) is computed per token from the combined frequency of its traits in
`metadata.py`. Every token also gets a unique **Rarity Rank** (1 = rarest).

**Totals:** 7 categories · 78 options · 5,555 unique tokens.
