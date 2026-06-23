"""Build ROBARK pixel-dog trait sprites (24x32 PNGs) into traits/.
Ported from the slonks/ANTNA engine — same careful pixel approach, but the
character is a DOG (ears + snout + nose). Eyes/mouth/outfit/accessory sprites
keep the slonks face rows so they align. Run this, then generator.py.
"""
from pathlib import Path
from PIL import Image
import random

W, H = 24, 32
ROOT = Path(__file__).parent
TRAITS = ROOT / "traits"

NONE = (0, 0, 0, 0)
BLACK = (24, 22, 28, 255)
DARK = (44, 42, 50, 255)
GREY = (115, 118, 130, 255)
DARK_GREY = (70, 72, 82, 255)
LIGHT = (200, 202, 212, 255)
WHITE = (248, 248, 250, 255)
RED = (190, 54, 54, 255)
DARK_RED = (150, 36, 38, 255)
ORANGE = (255, 140, 30, 255)
YELLOW = (228, 196, 74, 255)
GREEN = (70, 150, 84, 255)
BLUE = (60, 110, 200, 255)
NAVY = (40, 50, 86, 255)
PURPLE = (160, 70, 200, 255)
DEEP_PURPLE = (110, 50, 150, 255)
BROWN = (140, 90, 55, 255)
PINK_EAR = (206, 150, 158, 255)
NOSE = (26, 22, 22, 255)
CIG_FILTER = (170, 110, 65, 255)
EMBER = (255, 90, 60, 255)
SMOKE = (235, 235, 240, 240)
GOLD = (224, 188, 70, 255)

# fur palettes
FURS = {
    "cream": (226, 200, 156, 255), "golden": (224, 162, 78, 255),
    "grey": (150, 154, 166, 255), "choco": (150, 102, 64, 255),
    "black": (66, 64, 74, 255), "zombie": (120, 176, 96, 255),
    "white": (236, 236, 230, 255), "blue": (110, 140, 200, 255),
    "gold": (230, 196, 96, 255),
}
BGS = {"navy": (26, 28, 44, 255), "slate": (44, 48, 64, 255), "blood": (60, 26, 30, 255),
       "forest": (24, 46, 38, 255), "purple": (52, 34, 70, 255), "sky": (96, 140, 175, 255),
       "mustard": (150, 120, 40, 255), "pink": (150, 84, 104, 255)}


def new_img(fill=NONE): return Image.new("RGBA", (W, H), fill)
def put(img, x, y, c):
    if 0 <= x < W and 0 <= y < H: img.putpixel((x, y), c)
def fill_rect(img, x0, y0, x1, y1, c):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1): put(img, x, y, c)
def save(img, cat, name):
    (TRAITS / cat).mkdir(parents=True, exist_ok=True)
    img.save(TRAITS / cat / f"{name}.png")
def shade(c, d=34): return tuple(max(0, v - d) if i < 3 else 255 for i, v in enumerate(c))


# ---------- DOG HEAD (skin layer) ---------- #
HEAD_ROWS = [  # rounded dog head; eyes sit at row 11, mouth at row 15 (slonks-aligned)
    (5, 8, 15), (6, 7, 16), (7, 6, 17), (8, 6, 17), (9, 6, 17), (10, 6, 17),
    (11, 6, 17), (12, 6, 17), (13, 7, 16), (14, 8, 15), (15, 8, 15), (16, 9, 14),
]
MUZZLE_ROWS = [(13, 9, 14), (14, 9, 14), (15, 9, 14), (16, 9, 14), (17, 10, 13)]
NECK_ROWS = [(17, 10, 13), (18, 10, 13)]
CHEST_ROWS = [(19, 8, 15), (20, 5, 18), (21, 4, 19), (22, 3, 20), (23, 2, 21),
              (24, 1, 22), (25, 0, 23), (26, 0, 23), (27, 0, 23), (28, 0, 23),
              (29, 0, 23), (30, 0, 23), (31, 0, 23)]


def paint_chest(img, color):
    for r, c0, c1 in CHEST_ROWS:
        for c in range(c0, c1 + 1): put(img, c, r, color)


def paint_head(img, fur):
    sh = shade(fur, 36); muz = tuple(min(255, v + 22) if i < 3 else 255 for i, v in enumerate(fur))
    # ears — pointy, fur with darker inner edge + pink inner
    LEFT = [(6, 2), (5, 3), (5, 4), (6, 4), (4, 5), (5, 5), (6, 5), (7, 5),
            (4, 6), (5, 6), (6, 6), (7, 6), (5, 7), (6, 7), (7, 7)]
    for x, y in LEFT:
        put(img, x, y, fur); put(img, 23 - x, y, fur)
    put(img, 6, 4, PINK_EAR); put(img, 17, 4, PINK_EAR)
    put(img, 6, 5, PINK_EAR); put(img, 17, 5, PINK_EAR)
    # head
    for r, c0, c1 in HEAD_ROWS:
        for c in range(c0, c1 + 1): put(img, c, r, fur)
        put(img, c0, r, sh)
    # muzzle (lighter)
    for r, c0, c1 in MUZZLE_ROWS:
        for c in range(c0, c1 + 1): put(img, c, r, muz)
    # brow shading
    put(img, 8, 10, sh); put(img, 15, 10, sh)
    # nose
    fill_rect(img, 10, 12, 13, 13, NOSE)
    put(img, 11, 12, (64, 58, 54, 255))
    # neck + chest
    nk = shade(fur, 52)
    for r, c0, c1 in NECK_ROWS:
        for c in range(c0, c1 + 1): put(img, c, r, nk)
    paint_chest(img, fur)
    for r, c0, c1 in CHEST_ROWS[:3]:
        put(img, c0, r, sh); put(img, c1, r, sh)


def build_fur():
    for name, col in FURS.items():
        img = new_img(); paint_head(img, col)
        save(img, "skin", name)


# ---------- BACKGROUNDS ---------- #
def bg_dots(base):
    img = new_img(base); rng = random.Random(7)
    for y in range(H):
        for x in range(W):
            if rng.random() < 0.05: put(img, x, y, shade(base, -12))
    return img

def build_backgrounds():
    for name, col in BGS.items():
        save(bg_dots(col), "background", name)


# ---------- EYES (slonks, face-aligned) ---------- #
def eyes_normal():
    img = new_img()
    for ex in (8, 14):
        put(img, ex, 11, WHITE); put(img, ex + 1, 11, BLACK)
    return img

def eyes_shades(frame):
    img = new_img()
    fill_rect(img, 6, 9, 17, 9, frame); fill_rect(img, 6, 10, 17, 10, frame)
    fill_rect(img, 6, 13, 17, 13, frame); fill_rect(img, 6, 11, 6, 12, frame)
    fill_rect(img, 10, 11, 12, 12, frame); fill_rect(img, 17, 11, 17, 12, frame)
    fill_rect(img, 7, 11, 9, 12, WHITE); fill_rect(img, 13, 11, 16, 12, WHITE)
    put(img, 8, 11, BLACK); put(img, 9, 12, BLACK); put(img, 14, 11, BLACK); put(img, 15, 12, BLACK)
    return img

def eyes_vr():
    img = new_img(); fill_rect(img, 5, 9, 18, 13, DARK); fill_rect(img, 6, 10, 17, 12, BLACK)
    for ex in (8, 9, 14, 15): put(img, ex, 11, GREEN)
    fill_rect(img, 4, 11, 4, 12, DARK); fill_rect(img, 19, 11, 19, 12, DARK)
    return img

def eyes_laser():
    img = new_img()
    for ex in (8, 14): put(img, ex, 11, WHITE); put(img, ex + 1, 11, RED)
    for x in range(15, 24): put(img, x, 11, RED)
    for x in range(0, 9): put(img, x, 11, RED)
    return img

def eyes_3d():
    img = new_img()
    fill_rect(img, 6, 9, 17, 9, BLACK); fill_rect(img, 6, 13, 17, 13, BLACK)
    fill_rect(img, 6, 10, 6, 12, BLACK); fill_rect(img, 17, 10, 17, 12, BLACK)
    fill_rect(img, 11, 10, 12, 12, BLACK)
    fill_rect(img, 7, 10, 10, 12, (220, 50, 50, 255)); fill_rect(img, 13, 10, 16, 12, (60, 190, 220, 255))
    return img

def eyes_patch():
    img = new_img(); fill_rect(img, 6, 9, 17, 9, BLACK)
    fill_rect(img, 7, 10, 11, 13, BLACK); fill_rect(img, 8, 11, 10, 12, DARK)
    put(img, 14, 11, WHITE); put(img, 15, 11, WHITE); put(img, 14, 12, BLACK); put(img, 15, 12, BLACK)
    return img

def eyes_aviators():
    img = new_img()
    fill_rect(img, 6, 9, 17, 9, GOLD)
    fill_rect(img, 7, 10, 10, 12, BLACK); put(img, 6, 10, BLACK); put(img, 6, 11, BLACK)
    fill_rect(img, 13, 10, 16, 12, BLACK); put(img, 17, 10, BLACK); put(img, 17, 11, BLACK)
    put(img, 11, 10, GOLD); put(img, 12, 10, GOLD); put(img, 8, 10, WHITE); put(img, 14, 10, WHITE)
    return img

def eyes_money():
    img = new_img()
    for ex in (8, 14):
        put(img, ex, 11, GREEN); put(img, ex + 1, 11, (210, 230, 180, 255))
    return img

def build_eyes():
    save(eyes_normal(), "eyes", "normal")
    save(eyes_shades(BLACK), "eyes", "shades_black")
    save(eyes_shades(PURPLE), "eyes", "shades_purple")
    save(eyes_shades(RED), "eyes", "shades_red")
    save(eyes_vr(), "eyes", "vr")
    save(eyes_laser(), "eyes", "laser")
    save(eyes_3d(), "eyes", "glasses_3d")
    save(eyes_patch(), "eyes", "eyepatch")
    save(eyes_aviators(), "eyes", "aviators")
    save(eyes_money(), "eyes", "money")


# ---------- MOUTH (slonks, snout-aligned at row 15) ---------- #
def mouth_neutral():
    img = new_img(); fill_rect(img, 10, 15, 13, 15, DARK); return img

def mouth_tongue():
    img = new_img(); fill_rect(img, 10, 15, 13, 15, DARK)
    fill_rect(img, 11, 16, 12, 17, (210, 90, 110, 255)); return img

def mouth_cigarette():
    img = new_img()
    fill_rect(img, 9, 15, 12, 15, BLACK)
    fill_rect(img, 13, 14, 14, 15, CIG_FILTER); put(img, 13, 15, BROWN); put(img, 14, 15, BROWN)
    fill_rect(img, 15, 14, 19, 15, WHITE); put(img, 17, 14, LIGHT)
    put(img, 20, 14, EMBER); put(img, 20, 15, RED)
    put(img, 21, 13, SMOKE); put(img, 22, 11, SMOKE); put(img, 21, 9, SMOKE)
    return img

def mouth_cigar():
    img = new_img(); DB = (95, 60, 30, 255); LB = (170, 115, 75, 255)
    fill_rect(img, 9, 15, 12, 15, BLACK)
    fill_rect(img, 13, 14, 18, 15, BROWN); fill_rect(img, 13, 14, 18, 14, DB); fill_rect(img, 13, 15, 18, 15, LB)
    put(img, 19, 14, EMBER); put(img, 19, 15, RED); put(img, 20, 13, SMOKE); put(img, 21, 11, SMOKE)
    return img

def mouth_blunt():
    img = new_img()
    fill_rect(img, 9, 15, 12, 15, BLACK); fill_rect(img, 13, 14, 18, 15, (90, 70, 50, 255))
    put(img, 19, 14, EMBER); put(img, 20, 13, SMOKE); put(img, 21, 11, SMOKE)
    return img

def mouth_pipe():
    img = new_img()
    fill_rect(img, 9, 15, 12, 15, BLACK); fill_rect(img, 13, 15, 16, 15, BROWN); put(img, 13, 14, BROWN)
    fill_rect(img, 16, 13, 18, 16, BROWN); put(img, 17, 11, SMOKE); put(img, 18, 10, SMOKE)
    return img

def mouth_grin_gold():
    img = new_img()
    put(img, 9, 14, DARK); put(img, 14, 14, DARK); fill_rect(img, 10, 15, 13, 15, DARK)
    fill_rect(img, 10, 16, 13, 16, GOLD); return img

def mouth_smile():
    img = new_img(); fill_rect(img, 10, 15, 13, 15, DARK)
    put(img, 9, 14, DARK); put(img, 14, 14, DARK); put(img, 11, 16, WHITE); put(img, 12, 16, WHITE); return img

def build_mouths():
    save(mouth_cigarette(), "mouth", "cigarette")
    save(mouth_cigar(), "mouth", "cigar")
    save(mouth_blunt(), "mouth", "blunt")
    save(mouth_pipe(), "mouth", "pipe")
    save(mouth_tongue(), "mouth", "tongue")
    save(mouth_grin_gold(), "mouth", "grin_gold")
    save(mouth_smile(), "mouth", "smile")
    save(mouth_neutral(), "mouth", "neutral")


# ---------- HEADWEAR (hair layer; sits on forehead between ears) ---------- #
def hat_none(): return new_img()

def hat_cap():
    img = new_img(); fill_rect(img, 6, 4, 17, 6, RED); fill_rect(img, 7, 3, 16, 3, RED)
    fill_rect(img, 13, 7, 21, 8, DARK_RED); put(img, 11, 4, WHITE); put(img, 12, 4, WHITE); return img

def hat_beanie():
    img = new_img(); fill_rect(img, 6, 3, 17, 6, NAVY); fill_rect(img, 7, 2, 16, 2, NAVY)
    fill_rect(img, 6, 5, 17, 6, RED); put(img, 11, 1, WHITE); put(img, 12, 1, WHITE); return img

def hat_cowboy():
    img = new_img(); DB = (100, 65, 35, 255)
    fill_rect(img, 8, 1, 15, 4, BROWN); fill_rect(img, 8, 5, 15, 5, BLACK)
    fill_rect(img, 3, 6, 20, 6, BROWN); fill_rect(img, 2, 7, 21, 7, DB); put(img, 11, 5, YELLOW); return img

def hat_tophat():
    img = new_img(); fill_rect(img, 8, 0, 15, 5, BLACK); fill_rect(img, 8, 4, 15, 4, LIGHT)
    fill_rect(img, 4, 5, 19, 6, BLACK); return img

def hat_crown():
    img = new_img(); fill_rect(img, 8, 4, 15, 6, GOLD)
    for x in (8, 11, 15): put(img, x, 2, GOLD); put(img, x, 3, GOLD)
    put(img, 11, 5, RED); return img

def hat_mohawk():
    img = new_img()
    for x in range(11, 13): fill_rect(img, x, 0, x, 5, PURPLE)
    fill_rect(img, 10, 4, 13, 5, DEEP_PURPLE); return img

def hat_durag():
    img = new_img(); fill_rect(img, 6, 3, 17, 7, DARK); fill_rect(img, 5, 6, 6, 9, DARK); return img

def hat_halo():
    img = new_img(); fill_rect(img, 8, 1, 15, 1, GOLD); put(img, 7, 2, GOLD); put(img, 16, 2, GOLD); return img

def hat_horns():
    img = new_img()
    put(img, 7, 3, DARK_RED); put(img, 6, 2, DARK_RED); put(img, 6, 1, RED)
    put(img, 16, 3, DARK_RED); put(img, 17, 2, DARK_RED); put(img, 17, 1, RED); return img

def build_hats():
    save(hat_none(), "hair", "none")
    save(hat_cap(), "hair", "cap")
    save(hat_beanie(), "hair", "beanie")
    save(hat_cowboy(), "hair", "cowboy")
    save(hat_tophat(), "hair", "tophat")
    save(hat_crown(), "hair", "crown")
    save(hat_mohawk(), "hair", "mohawk")
    save(hat_durag(), "hair", "durag")
    save(hat_halo(), "hair", "halo")
    save(hat_horns(), "hair", "horns")


# ---------- OUTFIT (chest) ---------- #
def outfit_bare(): return new_img()

def _hoodie(color):
    img = new_img(); paint_chest(img, color)
    fill_rect(img, 8, 19, 15, 20, shade(color, 30)); fill_rect(img, 9, 19, 14, 19, shade(color, 55))
    for y in (21, 22, 23): put(img, 10, y, WHITE); put(img, 13, y, WHITE)
    fill_rect(img, 0, 24, 1, 31, shade(color, 30)); fill_rect(img, 22, 24, 23, 31, shade(color, 30))
    return img

def outfit_suit():
    img = new_img(); paint_chest(img, NAVY)
    fill_rect(img, 8, 19, 15, 19, WHITE); fill_rect(img, 9, 20, 14, 20, WHITE)
    fill_rect(img, 10, 21, 13, 21, WHITE); fill_rect(img, 11, 22, 12, 31, RED)
    put(img, 7, 20, BLACK); put(img, 8, 21, BLACK); put(img, 16, 20, BLACK); put(img, 15, 21, BLACK)
    return img

def outfit_track():
    img = new_img(); paint_chest(img, (170, 54, 54, 255))
    fill_rect(img, 11, 19, 12, 31, WHITE); fill_rect(img, 4, 22, 4, 31, WHITE); fill_rect(img, 19, 22, 19, 31, WHITE)
    return img

def build_outfits():
    save(outfit_bare(), "outfit", "bare")
    save(_hoodie((40, 40, 48, 255)), "outfit", "hoodie_black")
    save(_hoodie((170, 54, 54, 255)), "outfit", "hoodie_red")
    save(_hoodie((54, 84, 150, 255)), "outfit", "hoodie_blue")
    save(_hoodie((96, 100, 112, 255)), "outfit", "hoodie_grey")
    save(_hoodie((70, 130, 80, 255)), "outfit", "hoodie_green")
    save(outfit_suit(), "outfit", "suit")
    save(outfit_track(), "outfit", "tracksuit")


# ---------- ACCESSORY (overlay) ---------- #
def acc_none(): return new_img()
def acc_chain(col):
    img = new_img()
    for x in range(9, 16, 2): put(img, x, 19, col); put(img, x + 1, 20, col)
    return img
def acc_earring():
    img = new_img(); put(img, 5, 8, GOLD); put(img, 4, 9, GOLD); put(img, 5, 10, GOLD); return img

def build_accessories():
    save(acc_none(), "accessory", "none")
    save(acc_chain(GOLD), "accessory", "gold_chain")
    save(acc_chain((150, 210, 230, 255)), "accessory", "diamond_chain")
    save(acc_earring(), "accessory", "earring")


def main():
    TRAITS.mkdir(exist_ok=True)
    build_backgrounds(); build_fur(); build_outfits(); build_hats()
    build_eyes(); build_mouths(); build_accessories()
    print(f"Traits written to {TRAITS}")


if __name__ == "__main__":
    main()
